"""Unit tests for route graph construction and candidate corridor extraction."""

import pytest
import networkx as nx
from app.providers.airport_provider import DefaultAirportDataProvider
from app.providers.airway_provider import DefaultAeronauticalRouteDataProvider
from app.graph.builder import RouteGraphBuilder
from app.graph.corridor import CandidateCorridorExtractor
from app.models.schemas import AircraftPerformance, OptimizationWeights


@pytest.fixture
def graph_builder():
    return RouteGraphBuilder()


@pytest.fixture
def airport_provider():
    return DefaultAirportDataProvider()


def test_graph_has_published_waypoints(graph_builder):
    g = graph_builder.graph
    # Verify core Indian en-route waypoints exist
    assert "DPN" in g
    assert "HIA" in g
    assert "BPL" in g
    assert "BBB" in g
    assert "NGP" in g
    assert g.nodes["DPN"]["node_type"] == "VOR"


def test_airway_segments_have_valid_metadata(graph_builder):
    g = graph_builder.graph
    edge_data = g.get_edge_data("DPN", "ASARI")
    assert edge_data is not None
    assert edge_data["airway_id"] == "W15"
    assert edge_data["distance_nm"] > 0
    assert "Authoritative published data" in edge_data["validation_status"]


def test_connect_airports_and_find_path(graph_builder, airport_provider):
    delhi = airport_provider.get_airport_by_code("VIDP")
    hyderabad = airport_provider.get_airport_by_code("VOHS")

    orig_id, dest_id, meta = graph_builder.connect_airports(delhi, hyderabad)
    assert orig_id == "VIDP"
    assert dest_id == "VOHS"
    assert nx.has_path(graph_builder.graph, "VIDP", "VOHS")


def test_candidate_corridor_extraction(graph_builder, airport_provider):
    delhi = airport_provider.get_airport_by_code("VIDP")
    hyderabad = airport_provider.get_airport_by_code("VOHS")
    orig_id, dest_id, _ = graph_builder.connect_airports(delhi, hyderabad)

    aircraft = AircraftPerformance(model_code="A320neo", name="A320neo")
    weights = OptimizationWeights(distance=0.2, fuel=0.25, co2=0.3, time=0.15, congestion=0.1)

    corridor = CandidateCorridorExtractor.extract_candidate_subgraph(
        graph_builder.graph,
        orig_id,
        dest_id,
        aircraft,
        weights,
        max_candidate_paths=4,
        max_edges=16,
    )

    assert corridor["qubit_count"] <= 16
    assert corridor["qubit_count"] >= 4
    assert corridor["origin"] == "VIDP"
    assert corridor["destination"] == "VOHS"
    assert len(corridor["candidate_paths"]) >= 1


def test_missing_route_raises_error(graph_builder, airport_provider):
    # An isolated node test
    g = graph_builder.graph
    g.add_node("ISOLATED_ORIG", lat=0, lon=0, node_type="AIRPORT")
    g.add_node("ISOLATED_DEST", lat=10, lon=10, node_type="AIRPORT")

    aircraft = AircraftPerformance(model_code="A320neo", name="A320neo")
    weights = OptimizationWeights(distance=0.2, fuel=0.25, co2=0.3, time=0.15, congestion=0.1)

    with pytest.raises(ValueError, match="No connected route found"):
        CandidateCorridorExtractor.extract_candidate_subgraph(
            g, "ISOLATED_ORIG", "ISOLATED_DEST", aircraft, weights
        )
