"""FastAPI API routes for Quantum FlightPath Optimizer."""

import uuid
from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Query, status

from app.config import settings
from app.models.schemas import (
    Airport,
    OptimizationRequest,
    OptimizationResponse,
    OptimizationWeights,
    BackendStatusResponse,
    DataProvenance,
    RestrictedAirspace,
    AirwaySegment,
    AircraftPerformance,
    MetricsComparison,
    BackendExecutionDetails,
)
from app.providers.airport_provider import DefaultAirportDataProvider
from app.providers.airway_provider import DefaultAeronauticalRouteDataProvider
from app.providers.airspace_provider import DefaultAirspaceDataProvider
from app.providers.weather_provider import DefaultWeatherDataProvider
from app.providers.notam_provider import DefaultNotamDataProvider
from app.providers.congestion_provider import DefaultCongestionDataProvider
from app.providers.aircraft_provider import DefaultAircraftDataProvider
from app.graph.builder import RouteGraphBuilder
from app.graph.corridor import CandidateCorridorExtractor
from app.classical.optimizer import ClassicalRouteOptimizer
from app.quantum.qubo_formulation import FlightRouteQUBO
from app.quantum.backends import BackendFactory
from app.quantum.qaoa_solver import FlightRouteQAOASolver
from app.quantum.decoder import QuantumResultDecoder

router = APIRouter(prefix="/api")

# Provider instances
airport_provider = DefaultAirportDataProvider()
airway_provider = DefaultAeronauticalRouteDataProvider()
airspace_provider = DefaultAirspaceDataProvider()
weather_provider = DefaultWeatherDataProvider()
notam_provider = DefaultNotamDataProvider()
congestion_provider = DefaultCongestionDataProvider()
aircraft_provider = DefaultAircraftDataProvider()

# In-memory storage for generated routes
STORED_ROUTES: Dict[str, Any] = {}


@router.get("/airports/search", response_model=List[Airport])
def search_airports(q: str = Query("", description="Airport search term (name, city, ICAO, IATA)")):
    """Search airports by name, IATA/ICAO code, city, or country."""
    return airport_provider.search_airports(q, limit=15)


@router.get("/airports/{code}", response_model=Airport)
def get_airport_by_code(code: str):
    """Retrieve verified airport details by ICAO or IATA code."""
    apt = airport_provider.get_airport_by_code(code)
    if not apt:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Airport '{code}' not found in authoritative aerodrome registry.",
        )
    return apt


@router.get("/backend/status", response_model=BackendStatusResponse)
def get_backend_status():
    """Report actual quantum backend configuration and availability without exposing secrets."""
    overview = BackendFactory.get_status_overview()
    return BackendStatusResponse(**overview)


@router.post("/quantum/test")
def test_quantum_path(backend_mode: str = Query("auto", description="Backend mode to test: auto, ibm, aer")):
    """Check configured quantum execution path without fabricating a hardware job."""
    try:
        backend_inst, fallback, reason = BackendFactory.get_backend(backend_mode)
        # Run a minimal 2-qubit Bell circuit test
        from qiskit import QuantumCircuit
        test_qc = QuantumCircuit(2, 2)
        test_qc.h(0)
        test_qc.cx(0, 1)
        test_qc.measure([0, 1], [0, 1])

        result = backend_inst.execute_circuit(test_qc, shots=256)
        return {
            "success": True,
            "backend_tested": backend_inst.get_name(),
            "backend_type": backend_inst.get_backend_type(),
            "fallback_occurred": fallback,
            "fallback_reason": reason,
            "test_circuit_qubits": 2,
            "test_shots": 256,
            "counts": result["counts"],
            "execution_time_ms": result["execution_time_ms"],
            "message": "Quantum circuit execution verified successfully.",
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantum execution test failed: {str(e)}",
        )


@router.get("/data/provenance", response_model=List[DataProvenance])
def get_data_provenance():
    """Return all configured aeronautical data sources, dataset versions, timestamps, and validity statuses."""
    return [
        airport_provider.get_provenance(),
        airway_provider.get_provenance(),
        airspace_provider.get_provenance(),
        weather_provider.get_provenance(),
        notam_provider.get_provenance(),
        congestion_provider.get_provenance(),
        aircraft_provider.get_provenance(),
    ]


@router.get("/airways/network")
def get_airways_network():
    """Return published airway segments and waypoints for interactive map layer."""
    return {
        "waypoints": airway_provider.get_waypoints(),
        "segments": airway_provider.get_airway_segments(),
    }


@router.get("/airspace/restricted", response_model=List[RestrictedAirspace])
def get_restricted_airspaces():
    """Return published restricted, prohibited, and danger areas."""
    return airspace_provider.get_restricted_airspaces()


@router.get("/aircraft/types", response_model=List[AircraftPerformance])
def get_aircraft_types():
    """Return supported aircraft performance models."""
    return aircraft_provider.list_supported_aircraft()


@router.get("/routes/{route_id}")
def get_stored_route(route_id: str):
    """Retrieve details for a generated route by ID."""
    if route_id not in STORED_ROUTES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Route '{route_id}' not found in active session store.",
        )
    return STORED_ROUTES[route_id]


@router.post("/optimize", response_model=OptimizationResponse)
def optimize_flight_path(request: OptimizationRequest):
    """Run full-stack route optimization: classical baseline and genuine Qiskit quantum workflow."""
    req_id = f"opt_{uuid.uuid4().hex[:8]}"

    # 1. Airport Validation
    orig = airport_provider.get_airport_by_code(request.origin)
    if not orig:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Departure airport '{request.origin}' is not recognized in authoritative registry.",
        )

    dest = airport_provider.get_airport_by_code(request.destination)
    if not dest:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Destination airport '{request.destination}' is not recognized in authoritative registry.",
        )

    if orig.icao.upper() == dest.icao.upper():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Departure and destination airports cannot be identical. Please select distinct aerodromes.",
        )

    # 2. Aircraft & Weights Setup
    aircraft = aircraft_provider.get_aircraft(request.aircraft_type)
    if not aircraft:
        aircraft = aircraft_provider.get_aircraft("A320neo")

    # Set weights according to objective
    weights = request.weights
    if not weights:
        obj = request.objective.lower()
        if obj == "distance":
            weights = OptimizationWeights(distance=0.80, fuel=0.05, co2=0.05, time=0.05, congestion=0.05)
        elif obj == "fuel":
            weights = OptimizationWeights(distance=0.10, fuel=0.70, co2=0.10, time=0.05, congestion=0.05)
        elif obj == "co2":
            weights = OptimizationWeights(distance=0.05, fuel=0.20, co2=0.65, time=0.05, congestion=0.05)
        elif obj == "time":
            weights = OptimizationWeights(distance=0.10, fuel=0.05, co2=0.05, time=0.75, congestion=0.05)
        elif obj == "congestion":
            weights = OptimizationWeights(distance=0.10, fuel=0.05, co2=0.05, time=0.10, congestion=0.70)
        else:  # balanced
            weights = OptimizationWeights(distance=0.20, fuel=0.25, co2=0.30, time=0.15, congestion=0.10)

    # 3. Construct Route Graph
    graph_builder = RouteGraphBuilder(airway_provider, congestion_provider)
    orig_id, dest_id, _ = graph_builder.connect_airports(orig, dest)

    # 4. Classical Optimization Baseline
    classical_optimizer = ClassicalRouteOptimizer(graph_builder)
    try:
        classical_candidate = classical_optimizer.optimize(orig, dest, aircraft, weights)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Classical routing could not establish continuous airway path: {str(e)}",
        )

    # 5. Candidate Corridor Extraction & QUBO Problem Reduction
    try:
        corridor_data = CandidateCorridorExtractor.extract_candidate_subgraph(
            graph_builder.graph,
            orig_id,
            dest_id,
            aircraft,
            weights,
            max_candidate_paths=4,
            max_edges=16,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Candidate corridor extraction failed: {str(e)}",
        )

    # 6. Formulate QUBO
    qubo = FlightRouteQUBO(
        candidate_edges=corridor_data["candidate_edges"],
        candidate_nodes=corridor_data["candidate_nodes"],
        origin_id=orig_id,
        dest_id=dest_id,
        penalty_multiplier=3.5,
    )

    # 7. Quantum Backend Resolution
    try:
        backend_inst, fallback_occurred, fallback_reason = BackendFactory.get_backend(
            request.backend
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Quantum backend initialization error: {str(e)}",
        )

    # 8. Genuine QAOA Circuit Execution
    try:
        qaoa_result = FlightRouteQAOASolver.execute_qaoa(
            qubo=qubo,
            backend=backend_inst,
            shots=request.shots,
            p_layers=1,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Quantum circuit execution failed on backend '{backend_inst.get_name()}': {str(e)}",
        )

    # 9. Result Decoding and Route Feasibility Validation
    quantum_candidate, is_feasible = QuantumResultDecoder.decode_and_validate(
        qubo=qubo,
        execution_results=qaoa_result,
        origin=orig,
        destination=dest,
        aircraft=aircraft,
        weights=weights,
        full_graph=graph_builder.graph,
    )

    # 10. Metrics Comparison
    c_m = classical_candidate.metrics
    q_m = quantum_candidate.metrics

    dist_delta_nm = round(q_m.distance_nm - c_m.distance_nm, 2)
    dist_delta_pct = round((dist_delta_nm / c_m.distance_nm) * 100.0, 2) if c_m.distance_nm > 0 else 0.0

    fuel_delta_kg = round(q_m.estimated_fuel_kg - c_m.estimated_fuel_kg, 1)
    fuel_delta_pct = round((fuel_delta_kg / c_m.estimated_fuel_kg) * 100.0, 2) if c_m.estimated_fuel_kg > 0 else 0.0

    co2_delta_kg = round(q_m.estimated_co2_kg - c_m.estimated_co2_kg, 1)
    co2_delta_pct = round((co2_delta_kg / c_m.estimated_co2_kg) * 100.0, 2) if c_m.estimated_co2_kg > 0 else 0.0

    time_delta_min = round(q_m.estimated_time_minutes - c_m.estimated_time_minutes, 1)
    time_delta_pct = round((time_delta_min / c_m.estimated_time_minutes) * 100.0, 2) if c_m.estimated_time_minutes > 0 else 0.0

    obj_delta = round(q_m.objective_value - c_m.objective_value, 4)

    if is_feasible and abs(dist_delta_nm) < 0.1:
        verdict = "Quantum QAOA converged to the exact classical optimal airway route."
    elif is_feasible and q_m.objective_value <= c_m.objective_value:
        verdict = "Quantum solution achieved competitive objective parity with classical baseline."
    elif is_feasible:
        verdict = f"Quantum solution identified a feasible alternative route (+{dist_delta_pct:+.1f}% distance)."
    else:
        verdict = "Quantum result required classical post-processing repair due to sampling dispersion in intermediate nodes."

    metrics_comp = MetricsComparison(
        distance_delta_nm=dist_delta_nm,
        distance_delta_pct=dist_delta_pct,
        fuel_delta_kg=fuel_delta_kg,
        fuel_delta_pct=fuel_delta_pct,
        co2_delta_kg=co2_delta_kg,
        co2_delta_pct=co2_delta_pct,
        time_delta_min=time_delta_min,
        time_delta_pct=time_delta_pct,
        objective_delta=obj_delta,
        quantum_feasible=is_feasible,
        summary_verdict=verdict,
    )

    backend_details = BackendExecutionDetails(
        mode_requested=request.backend,
        active_backend=qaoa_result["backend_name"],
        backend_type=qaoa_result["backend_type"],
        qubit_count=qaoa_result["qubit_count"],
        circuit_depth=qaoa_result["circuit_depth"],
        shots=qaoa_result["shots"],
        execution_time_ms=qaoa_result["execution_time_ms"],
        job_id=qaoa_result.get("job_id"),
        fallback_occurred=fallback_occurred,
        fallback_reason=fallback_reason,
        top_bitstrings=qaoa_result.get("top_bitstrings", []),
    )

    provenance_list = [
        airport_provider.get_provenance(),
        airway_provider.get_provenance(),
        airspace_provider.get_provenance(),
        weather_provider.get_provenance(),
        notam_provider.get_provenance(),
        congestion_provider.get_provenance(),
        aircraft_provider.get_provenance(),
    ]

    response = OptimizationResponse(
        success=True,
        request_id=req_id,
        timestamp=datetime.now(timezone.utc).isoformat(),
        origin=orig,
        destination=dest,
        aircraft=aircraft,
        classical_route=classical_candidate,
        quantum_route=quantum_candidate,
        metrics_comparison=metrics_comp,
        backend_execution=backend_details,
        data_provenances=provenance_list,
        disclaimer=settings.AVIATION_DISCLAIMER,
    )

    STORED_ROUTES[req_id] = response
    return response
