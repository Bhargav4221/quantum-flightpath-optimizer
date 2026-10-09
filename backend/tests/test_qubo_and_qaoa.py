"""Unit tests for programmatic QUBO formulation, QAOA circuit builder, and decoding."""

import pytest
import numpy as np
from app.quantum.qubo_formulation import FlightRouteQUBO
from app.quantum.qaoa_solver import FlightRouteQAOASolver
from app.quantum.backends import AerBackend
from app.quantum.decoder import QuantumResultDecoder
from app.models.schemas import Airport, AircraftPerformance, OptimizationWeights


@pytest.fixture
def sample_edges():
    return [
        {"u": "ORIG", "v": "W1", "cost": 0.5, "distance_nm": 100},
        {"u": "ORIG", "v": "W2", "cost": 0.7, "distance_nm": 140},
        {"u": "W1", "v": "DEST", "cost": 0.5, "distance_nm": 100},
        {"u": "W2", "v": "DEST", "cost": 0.4, "distance_nm": 80},
        {"u": "W1", "v": "W2", "cost": 0.2, "distance_nm": 40},
    ]


@pytest.fixture
def sample_nodes():
    return ["ORIG", "W1", "W2", "DEST"]


def test_qubo_matrix_dimensions_and_terms(sample_edges, sample_nodes):
    qubo = FlightRouteQUBO(
        candidate_edges=sample_edges,
        candidate_nodes=sample_nodes,
        origin_id="ORIG",
        dest_id="DEST",
        penalty_multiplier=3.0,
    )

    assert qubo.num_vars == 5
    assert qubo.Q.shape == (5, 5)
    # Check that diagonal has edge cost additions
    assert qubo.Q[0, 0] != 0.0


def test_qubo_evaluates_valid_vs_invalid_path(sample_edges, sample_nodes):
    qubo = FlightRouteQUBO(
        candidate_edges=sample_edges,
        candidate_nodes=sample_nodes,
        origin_id="ORIG",
        dest_id="DEST",
        penalty_multiplier=4.0,
    )

    # Valid path 1: ORIG->W1 (idx 0) and W1->DEST (idx 2) => "10100"
    energy_valid = qubo.evaluate_bitstring_energy("10100")

    # Invalid path: no edges selected => "00000" (violates origin and destination constraints)
    energy_empty = qubo.evaluate_bitstring_energy("00000")

    # Constraint violations must incur substantial penalty
    assert energy_empty > energy_valid


def test_ising_hamiltonian_conversion(sample_edges, sample_nodes):
    qubo = FlightRouteQUBO(
        candidate_edges=sample_edges,
        candidate_nodes=sample_nodes,
        origin_id="ORIG",
        dest_id="DEST",
    )
    pauli_dict, offset = qubo.to_ising_pauli_terms()

    assert len(pauli_dict) > 0
    # Must have both single-qubit Z_i and two-qubit Z_i Z_j terms
    single_z = [k for k in pauli_dict if len(k.split()) == 1]
    two_z = [k for k in pauli_dict if len(k.split()) == 2]
    assert len(single_z) > 0
    assert len(two_z) > 0


def test_qaoa_circuit_execution_on_aer(sample_edges, sample_nodes):
    qubo = FlightRouteQUBO(
        candidate_edges=sample_edges,
        candidate_nodes=sample_nodes,
        origin_id="ORIG",
        dest_id="DEST",
    )
    aer = AerBackend()
    result = FlightRouteQAOASolver.execute_qaoa(qubo, backend=aer, shots=512)

    assert result["qubit_count"] == 5
    assert result["circuit_depth"] > 0
    assert result["shots"] == 512
    assert len(result["counts"]) > 0
    assert len(result["top_bitstrings"]) > 0


def test_result_decoder_continuity_validation():
    # Test valid continuous path
    edges = [
        {"u": "DEL", "v": "DPN"},
        {"u": "DPN", "v": "ASARI"},
        {"u": "ASARI", "v": "HYD"},
    ]
    path, valid, msg = QuantumResultDecoder._verify_path_continuity(edges, "DEL", "HYD")
    assert valid is True
    assert path == ["DEL", "DPN", "ASARI", "HYD"]

    # Test discontinuous path
    broken_edges = [
        {"u": "DEL", "v": "DPN"},
        {"u": "BPL", "v": "HYD"},
    ]
    path, valid, msg = QuantumResultDecoder._verify_path_continuity(broken_edges, "DEL", "HYD")
    assert valid is False
