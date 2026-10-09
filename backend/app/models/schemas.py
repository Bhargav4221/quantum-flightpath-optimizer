"""Pydantic schemas and data models for Quantum FlightPath Optimizer."""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field, field_validator


class Waypoint(BaseModel):
    identifier: str
    name: Optional[str] = None
    latitude: float
    longitude: float
    waypoint_type: str = "FIX"  # FIX, VOR, NDB, AIRPORT
    source: str = "AAI AIP / Authoritative Published Data"


class Airport(BaseModel):
    icao: str
    iata: Optional[str] = None
    name: str
    city: str
    country: str
    latitude: float
    longitude: float
    elevation_ft: Optional[int] = None
    airport_type: str = "large_airport"
    runways_count: Optional[int] = None
    source: str = "OurAirports / AAI Authoritative Data"


class AirwaySegment(BaseModel):
    airway_id: str
    from_point: str
    to_point: str
    from_coords: List[float]  # [lat, lon]
    to_coords: List[float]    # [lat, lon]
    distance_nm: float
    distance_km: float
    directionality: str = "BOTH"  # BOTH, FORWARD
    minimum_enroute_fl: int = 150
    maximum_enroute_fl: int = 460
    source: str = "AAI Published ATS Route Network"
    validation_status: str = "Authoritative published data"


class RestrictedAirspace(BaseModel):
    identifier: str
    name: str
    airspace_type: str  # Prohibited, Restricted, Danger
    lower_limit: str
    upper_limit: str
    polygon: List[List[float]]  # List of [lat, lon]
    source: str = "AAI En-Route Prohibited/Restricted Airspace"
    validation_status: str = "Authoritative published data"


class AircraftPerformance(BaseModel):
    model_code: str
    name: str
    cruise_mach: float = 0.78
    cruise_tas_knots: float = 450.0  # True Airspeed in Knots
    cruise_altitude_fl: int = 350
    base_fuel_burn_kg_per_nm: float = 4.2  # Nominal cruise fuel rate
    taxi_fuel_kg: float = 200.0
    climb_descent_fuel_kg: float = 450.0
    climb_descent_time_min: float = 25.0
    co2_emission_factor: float = 3.16  # ICAO standard: 3.16 kg CO2 per kg Jet-A1


class OptimizationWeights(BaseModel):
    distance: float = Field(0.20, ge=0.0, le=1.0)
    fuel: float = Field(0.25, ge=0.0, le=1.0)
    co2: float = Field(0.30, ge=0.0, le=1.0)
    time: float = Field(0.15, ge=0.0, le=1.0)
    congestion: float = Field(0.10, ge=0.0, le=1.0)

    @field_validator("congestion")
    @classmethod
    def validate_sum(cls, v, values):
        # Allow small floating point rounding tolerances
        total = values.data.get("distance", 0) + values.data.get("fuel", 0) + values.data.get("co2", 0) + values.data.get("time", 0) + v
        if abs(total - 1.0) > 0.02 and abs(total - 100.0) > 2.0:
            raise ValueError(f"Weights must sum to 1.0 (or 100%), got {total}")
        return v

    def normalized(self) -> Dict[str, float]:
        raw_sum = self.distance + self.fuel + self.co2 + self.time + self.congestion
        if raw_sum <= 0:
            return {"distance": 0.2, "fuel": 0.25, "co2": 0.3, "time": 0.15, "congestion": 0.1}
        return {
            "distance": round(self.distance / raw_sum, 4),
            "fuel": round(self.fuel / raw_sum, 4),
            "co2": round(self.co2 / raw_sum, 4),
            "time": round(self.time / raw_sum, 4),
            "congestion": round(self.congestion / raw_sum, 4),
        }


class OptimizationRequest(BaseModel):
    origin: str  # ICAO or IATA code
    destination: str  # ICAO or IATA code
    objective: str = "balanced"  # balanced, distance, fuel, co2, time, congestion
    weights: Optional[OptimizationWeights] = None
    aircraft_type: str = "A320neo"
    backend: str = "auto"  # auto, ibm, aer
    shots: int = 1024


class RouteMetrics(BaseModel):
    distance_nm: float
    distance_km: float
    estimated_time_minutes: float
    estimated_fuel_kg: float
    estimated_co2_kg: float
    congestion_score: float  # 0.0 - 1.0
    objective_value: float


class RouteCandidate(BaseModel):
    route_id: str
    route_type: str  # "classical" | "quantum"
    waypoints: List[Dict[str, Any]]
    airway_segments: List[str]
    coordinates: List[List[float]]  # [[lat, lon], ...]
    metrics: RouteMetrics
    is_valid: bool
    validation_status: str  # "Valid Continuous Route" | "Infeasible - Graph Discontinuity" | "Classically Repaired"
    validation_notes: List[str] = []
    # Quantum execution specifics
    raw_bitstring: Optional[str] = None
    qubit_count: Optional[int] = None
    circuit_depth: Optional[int] = None
    shots: Optional[int] = None
    execution_time_ms: Optional[float] = None
    post_processing_applied: bool = False


class BackendExecutionDetails(BaseModel):
    mode_requested: str  # auto, ibm, aer
    active_backend: str  # e.g. "Qiskit Aer — Local Quantum Circuit Simulation" or "ibm_kyiv"
    backend_type: str    # "simulator" or "hardware"
    qubit_count: int
    circuit_depth: int
    shots: int
    execution_time_ms: float
    job_id: Optional[str] = None
    fallback_occurred: bool = False
    fallback_reason: Optional[str] = None
    top_bitstrings: List[Dict[str, Any]] = []


class DataProvenance(BaseModel):
    dataset_name: str
    provider: str
    source_url_or_doc: str
    dataset_version: str
    retrieval_timestamp: str
    effective_date: str
    expiration_date: Optional[str] = None
    geographic_coverage: str
    validation_status: str  # "Authoritative published data", "Data source unavailable", "Live data not configured", etc.
    live_connected: bool = False
    notes: Optional[str] = None


class MetricsComparison(BaseModel):
    distance_delta_nm: float
    distance_delta_pct: float
    fuel_delta_kg: float
    fuel_delta_pct: float
    co2_delta_kg: float
    co2_delta_pct: float
    time_delta_min: float
    time_delta_pct: float
    objective_delta: float
    quantum_feasible: bool
    summary_verdict: str


class OptimizationResponse(BaseModel):
    success: bool
    request_id: str
    timestamp: str
    origin: Airport
    destination: Airport
    aircraft: AircraftPerformance
    classical_route: RouteCandidate
    quantum_route: RouteCandidate
    metrics_comparison: MetricsComparison
    backend_execution: BackendExecutionDetails
    data_provenances: List[DataProvenance]
    disclaimer: str
    error_message: Optional[str] = None


class BackendStatusResponse(BaseModel):
    configured_token_present: bool
    instance_configured: bool
    current_mode: str
    active_backend_name: str
    backend_type: str
    supported_backends: List[Dict[str, Any]]
    aer_available: bool
    ibm_available: bool
    message: str
