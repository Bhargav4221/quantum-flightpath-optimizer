"""Classical Route Optimizer using Dijkstra / A* over Validated Graph."""

from typing import Dict, Any, List
import networkx as nx

from app.models.schemas import (
    Airport,
    AircraftPerformance,
    OptimizationWeights,
    RouteCandidate,
    RouteMetrics,
)
from app.graph.builder import RouteGraphBuilder
from app.metrics.fuel_emissions import FuelEmissionsCalculator


class ClassicalRouteOptimizer:
    """Solves multi-objective optimal flight path classically using validated graph search."""

    def __init__(self, builder: RouteGraphBuilder):
        self.builder = builder

    def optimize(
        self,
        origin: Airport,
        destination: Airport,
        aircraft: AircraftPerformance,
        weights: OptimizationWeights,
    ) -> RouteCandidate:
        """Find the optimal flight path classically minimizing the multi-objective cost."""
        orig_id, dest_id, _ = self.builder.connect_airports(origin, destination)
        graph = self.builder.graph

        if not nx.has_path(graph, orig_id, dest_id):
            raise ValueError(
                f"No navigable airway path exists between {origin.icao} and {destination.icao} in the published network."
            )

        # Assign normalized multi-objective weight to every edge
        norm_w = weights.normalized()
        for u, v, d in graph.edges(data=True):
            dist_nm = d.get("distance_nm", 50.0)
            time_min = (dist_nm / aircraft.cruise_tas_knots) * 60.0
            fuel_kg = dist_nm * aircraft.base_fuel_burn_kg_per_nm
            co2_kg = fuel_kg * aircraft.co2_emission_factor
            cong = d.get("congestion_score", 0.3)

            # Combined weighted cost
            cost = (
                norm_w["distance"] * (dist_nm / 500.0)
                + norm_w["fuel"] * (fuel_kg / 2000.0)
                + norm_w["co2"] * (co2_kg / 6320.0)
                + norm_w["time"] * (time_min / 60.0)
                + norm_w["congestion"] * cong
            )
            d["weight"] = cost

        # Solve shortest path using Dijkstra algorithm
        path_nodes = nx.dijkstra_path(graph, orig_id, dest_id, weight="weight")

        # Compile route details
        waypoints_detail = []
        coordinates = []
        airway_segments = []
        total_dist_nm = 0.0
        congestion_sum = 0.0
        edge_count = 0

        for i, node_id in enumerate(path_nodes):
            node_data = graph.nodes[node_id]
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

            if i < len(path_nodes) - 1:
                next_id = path_nodes[i + 1]
                edge_data = graph[node_id][next_id]
                seg_id = edge_data.get("airway_id", "DIRECT")
                airway_segments.append(seg_id)
                seg_dist = edge_data.get("distance_nm", 0.0)
                total_dist_nm += seg_dist
                congestion_sum += edge_data.get("congestion_score", 0.3)
                edge_count += 1

        avg_congestion = (congestion_sum / edge_count) if edge_count > 0 else 0.3
        metrics = FuelEmissionsCalculator.calculate_full_route_metrics(
            total_dist_nm, aircraft, avg_congestion, weights
        )

        return RouteCandidate(
            route_id=f"classical_{origin.icao}_{destination.icao}",
            route_type="classical",
            waypoints=waypoints_detail,
            airway_segments=airway_segments,
            coordinates=coordinates,
            metrics=metrics,
            is_valid=True,
            validation_status="Valid Continuous Route",
            validation_notes=[
                "Optimal classical baseline computed via Dijkstra shortest path algorithm.",
                f"Airway sequence fully continuous across {len(airway_segments)} published segments.",
            ],
            post_processing_applied=False,
        )
