"""Genuine Qiskit QAOA Circuit Builder and Quantum Execution Engine."""

import math
from typing import Dict, Any, Tuple
import numpy as np
from qiskit import QuantumCircuit
from qiskit.circuit import Parameter

from app.quantum.qubo_formulation import FlightRouteQUBO
from app.quantum.backends import QuantumBackendBase


class FlightRouteQAOASolver:
    """Builds and executes genuine parameterized QAOA quantum circuits for route optimization."""

    @staticmethod
    def build_qaoa_circuit(
        qubo: FlightRouteQUBO,
        p_layers: int = 1,
        gamma_val: float = 0.5,
        beta_val: float = 0.8,
    ) -> QuantumCircuit:
        """Construct QAOA quantum circuit from QUBO Ising Hamiltonian terms.

        H_C = sum_i h_i Z_i + sum_{i < j} J_{ij} Z_i Z_j
        H_M = sum_i X_i
        """
        n_qubits = qubo.num_vars
        if n_qubits < 1:
            raise ValueError("QUBO problem has 0 variables.")

        pauli_dict, offset = qubo.to_ising_pauli_terms()
        qc = QuantumCircuit(n_qubits, n_qubits)

        # 1. Initial State: Equal Superposition |+>^n
        qc.h(range(n_qubits))

        # 2. Alternating QAOA Layers
        for layer in range(p_layers):
            # Cost Hamiltonian Unitary U(H_C, gamma)
            # Two-qubit interaction terms J_ij Z_i Z_j
            for key, coeff in pauli_dict.items():
                parts = key.split()
                if len(parts) == 2 and parts[0].startswith("Z_") and parts[1].startswith("Z_"):
                    q1 = int(parts[0].replace("Z_", ""))
                    q2 = int(parts[1].replace("Z_", ""))
                    angle = 2.0 * gamma_val * coeff
                    # RZZ(angle) implemented as CX -> RZ -> CX
                    qc.cx(q1, q2)
                    qc.rz(angle, q2)
                    qc.cx(q1, q2)

            # Single-qubit terms h_i Z_i
            for key, coeff in pauli_dict.items():
                parts = key.split()
                if len(parts) == 1 and parts[0].startswith("Z_"):
                    q = int(parts[0].replace("Z_", ""))
                    angle = 2.0 * gamma_val * coeff
                    qc.rz(angle, q)

            # Mixer Hamiltonian Unitary U(H_M, beta) = exp(-i beta sum X_i)
            # RX(2 * beta) on every qubit
            for q in range(n_qubits):
                qc.rx(2.0 * beta_val, q)

        # 3. Measurement
        qc.measure(range(n_qubits), range(n_qubits))
        return qc

    @classmethod
    def execute_qaoa(
        cls,
        qubo: FlightRouteQUBO,
        backend: QuantumBackendBase,
        shots: int = 1024,
        p_layers: int = 1,
    ) -> Dict[str, Any]:
        """Build and execute the QAOA circuit, returning genuine execution metrics."""
        circuit = cls.build_qaoa_circuit(qubo, p_layers=p_layers)
        exec_result = backend.execute_circuit(circuit, shots=shots)

        counts = exec_result["counts"]
        # Format counts into sorted list of top bitstrings with energy evaluation
        top_candidates = []
        for bitstr, count in sorted(counts.items(), key=lambda item: item[1], reverse=True)[:10]:
            # Convert Qiskit little-endian or standard bit ordering to variable mapping
            # Qiskit returns bitstrings where rightmost character is qubit 0.
            # Reverse to match index 0 = edge 0.
            canonical_bitstr = bitstr[::-1]
            energy = qubo.evaluate_bitstring_energy(canonical_bitstr)
            top_candidates.append({
                "bitstring": canonical_bitstr,
                "raw_bitstring": bitstr,
                "counts": count,
                "probability": round(count / shots, 4),
                "qubo_energy": energy,
            })

        exec_result["top_bitstrings"] = top_candidates
        return exec_result
