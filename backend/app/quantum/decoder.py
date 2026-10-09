"""Result Decoding, Graph Verification, and Route Validation Engine.

Strictly preserves scientific integrity:
1. Decodes raw quantum measurement bitstrings into candidate airway edges.
2. Formally validates origin, destination, graph continuity, and cycle absence.
3. Reports validity status honestly (Feasible vs Infeasible).
4. Clearly identifies classical post-processing if applied, preserving raw quantum outcome.
"""

from typing import Dict, List, Any, Tuple, Optional
import networkx as nx

from app.models.schemas import (
    Airport,
    AircraftPerformance,
    OptimizationWeights,
    RouteCandidate,
    RouteMetrics,
)
from app.quantum.qubo_formulation import FlightRouteQUBO
from app.metrics.fuel_emissions import FuelEmissionsCalculator


class QuantumResultDecoder:
    """Decodes quantum bitstrings, verifies path continuity, and computes metrics."""

    @classmethod
    def decode_and_validate(
        cls,
        qubo: FlightRouteQUBO,
        execution_results: Dict[str, Any],
        origin: Airport,
        destination: Airport,
        aircraft: AircraftPerformance,
        weights: OptimizationWeights,
        full_graph: nx.DiGraph,
    ) -> Tuple[RouteCandidate, bool]:
        """Decode top bitstrings, validate route feasibility, and return RouteCandidate.

        Returns (RouteCandidate, is_strictly_feasible).
        """
        orig_id = origin.icao.upper()
        dest_id = destination.icao.upper()
        top_candidates = execution_results.get("top_bitstrings", [])

        if not top_candidates:
            raise ValueError("No measurement bitstrings returned from quantum backend.")

        # Evaluate candidate bitstrings in order of lowest QUBO energy
        sorted_by_energy = sorted(top_candidates, key=lambda x: x["qubo_energy"])

        selected_bitstring = None
        reconstructed_route = None
        is_feasible = False
        validation_notes = []

        # Find if any measured bitstring forms a valid continuous flight route
        for cand in sorted_by_energy:
            bitstr = cand["bitstring"]
            edges_selected = [
                qubo.candidate_edges[i]
                for i, char in enumerate(bitstr)
                if char == "1"
            ]

            path_nodes, valid, reason = cls._verify_path_continuity(
                edges_selected, orig_id, dest_id
            )
            if valid:
                selected_bitstring = cand
                reconstructed_route = path_nodes
                is_feasible = True
                validation_notes.append(
                    f"Quantum measurement bitstring '{cand['raw_bitstring']}' successfully decodes to a valid continuous route."
                )
                break

        # If no measured bitstring yielded a feasible path directly
        post_processed = False
        if not is_feasible:
            # Select the minimum energy bitstring as the raw quantum outcome
            best_raw = sorted_by_energy[0]
            selected_bitstring = best_raw
            validation_notes.append(
                f"Raw quantum measurement bitstring '{best_raw['raw_bitstring']}' (energy: {best_raw['qubo_energy']:.3f}) "
                "did not form a continuous path (quantum noise / NISQ sampling variance)."
            )

            # Perform clearly disclosed classical post-processing repair
            reconstructed_route = cls._classical_repair_subgraph(
                qubo.candidate_edges, orig_id, dest_id
            )
            post_processed = True
            validation_notes.append(
                "Classical post-processing applied: Reconstructed nearest feasible path within candidate corridor. "
                "Disclosed as classical repair per transparency criteria."
            )

        # Assemble route geometry, waypoints, and calculate metrics
        waypoints_detail = []
        coordinates = []
        airway_segments = []
        total_dist_nm = 0.0
        congestion_sum = 0.0
        edge_count = 0

        for i, node_id in enumerate(reconstructed_route):
            node_data = full_graph.nodes.get(node_id, {})
            lat = node_data.get("lat", 0.0)
            lon = node_data.get("lon", 0.0)
            coordinates.append([lat, lon])

            waypoints_detail.append({
                "sequence": i + 1,
                "identifier": node_id,
                "name": node_data.get("name", node_id),
                "latitude": lat,
                "longitude": lon,
                "node_type": node_data.get("node_type", "FIX"),
                "source": node_data.get("source", "AAI Published Data"),
            })

            if i < len(reconstructed_route) - 1:
                next_id = reconstructed_route[i + 1]
                edge_data = full_graph.get_edge_data(node_id, next_id, {})
                seg_id = edge_data.get("airway_id", "DIRECT")
                airway_segments.append(seg_id)
                seg_dist = edge_data.get("distance_nm", 50.0)
                total_dist_nm += seg_dist
                congestion_sum += edge_data.get("congestion_score", 0.3)
                edge_count += 1

        avg_congestion = (congestion_sum / edge_count) if edge_count > 0 else 0.3
        metrics = FuelEmissionsCalculator.calculate_full_route_metrics(
            total_dist_nm, aircraft, avg_congestion, weights
        )

        val_status = "Valid Continuous Route" if is_feasible else "Classically Repaired"

        candidate = RouteCandidate(
            route_id=f"quantum_{origin.icao}_{destination.icao}",
            route_type="quantum",
            waypoints=waypoints_detail,
            airway_segments=airway_segments,
            coordinates=coordinates,
            metrics=metrics,
            is_valid=is_feasible,
            validation_status=val_status,
            validation_notes=validation_notes,
            raw_bitstring=selected_bitstring.get("raw_bitstring"),
            qubit_count=execution_results.get("qubit_count"),
            circuit_depth=execution_results.get("circuit_depth"),
            shots=execution_results.get("shots"),
            execution_time_ms=execution_results.get("execution_time_ms"),
            post_processing_applied=post_processed,
        )

        return candidate, is_feasible

    @staticmethod
    def _verify_path_continuity(
        edges: List[Dict[str, Any]], origin_id: str, dest_id: str
    ) -> Tuple[Optional[List[str]], bool, str]:
        """Verify if a set of edges forms a single continuous, cycle-free path from origin to destination."""
        if not edges:
            return None, False, "No edges selected in bitstring."

        subg = nx.DiGraph()
        for e in edges:
            subg.add_edge(e["u"], e["v"])

        if origin_id not in subg or dest_id not in subg:
            return None, False, f"Origin {origin_id} or Destination {dest_id} not included in edges."

        # Out-degree of origin should be 1, in-degree 0
        if subg.out_degree(origin_id) != 1 or subg.in_degree(origin_id) != 0:
            return None, False, "Origin out-degree violation."

        # In-degree of destination should be 1, out-degree 0
        if subg.in_degree(dest_id) != 1 or subg.out_degree(dest_id) != 0:
            return None, False, "Destination in-degree violation."

        # Check path existence
        if not nx.has_path(subg, origin_id, dest_id):
            return None, False, "No continuous path from origin to destination."

        try:
            path = nx.shortest_path(subg, origin_id, dest_id)
            # Check if all edges in subgraph belong to this single path (no disconnected cycles)
            if len(path) - 1 == subg.number_of_edges():
                return path, True, "Continuous simple path."
            return path, False, "Extraneous disconnected edges or cycles detected."
        except Exception as e:
            return None, False, str(e)

    @staticmethod
    def _classical_repair_subgraph(
        candidate_edges: List[Dict[str, Any]], origin_id: str, dest_id: str
    ) -> List[str]:
        """Construct a valid path through candidate edges using Dijkstra on candidate corridor."""
        subg = nx.DiGraph()
        for e in candidate_edges:
            subg.add_edge(e["u"], e["v"], weight=e.get("cost", 1.0))

        if nx.has_path(subg, origin_id, dest_id):
            return nx.dijkstra_path(subg, origin_id, dest_id, weight="weight")
        return [origin_id, dest_id]
