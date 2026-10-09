"""Programmatic QUBO Mathematical Formulation for Flight Route Optimization.

Mathematical Formulation:
Variables:
    x_e in {0, 1} for each candidate directed edge e in E_cand

Cost function:
    Minimize Cost = sum_{e in E_cand} c_e * x_e
    where c_e is the normalized multi-objective cost (distance, fuel, CO2, time, congestion).

Constraints with penalty parameter lambda:
    1. Origin departure constraint:
       ( sum_{e in out(s)} x_e - 1 )^2
    2. Destination arrival constraint:
       ( sum_{e in in(t)} x_e - 1 )^2
    3. Flow conservation for all intermediate waypoints v in V \ {s, t}:
       ( sum_{e in out(v)} x_e - sum_{e in in(v)} x_e )^2
    4. Node degree bound (preventing branching / multi-pass loops):
       sum_v ( sum_{e in out(v)} x_e ) * ( sum_{e in out(v)} x_e - 1 )

Total QUBO Objective:
    H(x) = sum_e c_e * x_e + lambda_source * P_source + lambda_sink * P_sink + lambda_flow * P_flow + lambda_degree * P_degree
"""

from typing import Dict, List, Any, Tuple
import numpy as np


class FlightRouteQUBO:
    """Constructs programmatic QUBO matrices and Ising representations for route selection."""

    def __init__(
        self,
        candidate_edges: List[Dict[str, Any]],
        candidate_nodes: List[str],
        origin_id: str,
        dest_id: str,
        penalty_multiplier: float = 3.5,
    ):
        self.candidate_edges = candidate_edges
        self.candidate_nodes = candidate_nodes
        self.origin_id = origin_id
        self.dest_id = dest_id
        self.num_vars = len(candidate_edges)
        self.penalty_multiplier = penalty_multiplier

        # Map edge to index
        self.edge_to_idx = {
            f"{e['u']}->{e['v']}": i for i, e in enumerate(candidate_edges)
        }
        self.idx_to_edge = {
            i: f"{e['u']}->{e['v']}" for i, e in enumerate(candidate_edges)
        }

        # Build Q matrix (num_vars x num_vars)
        self.Q = np.zeros((self.num_vars, self.num_vars), dtype=float)
        self.constant_offset = 0.0
        self._formulate_qubo()

    def _formulate_qubo(self):
        """Programmatically populate quadratic and linear QUBO terms."""
        # 1. Linear edge costs: sum_e c_e * x_e
        # Since x_e^2 = x_e for binary variables, linear terms go on the diagonal of Q.
        max_cost = 0.1
        for i, edge in enumerate(self.candidate_edges):
            cost = float(edge.get("cost", 1.0))
            self.Q[i, i] += cost
            if cost > max_cost:
                max_cost = cost

        # Penalty factor lambda > max_cost
        penalty = max_cost * self.penalty_multiplier

        # 2. Origin constraint: (sum_{e in out(s)} x_e - 1)^2
        # = sum_{e} x_e^2 + 2 sum_{e1 < e2} x_e1 x_e2 - 2 sum_e x_e + 1
        # = sum_e (-1) * x_e + 2 sum_{e1 < e2} x_e1 x_e2 + 1  (since x_e^2 = x_e)
        out_s_indices = [
            i for i, e in enumerate(self.candidate_edges) if e["u"] == self.origin_id
        ]
        if out_s_indices:
            self.constant_offset += penalty
            for i in out_s_indices:
                self.Q[i, i] += penalty * (-1.0)
            for idx1 in out_s_indices:
                for idx2 in out_s_indices:
                    if idx1 < idx2:
                        self.Q[idx1, idx2] += penalty * 2.0

        # 3. Destination constraint: (sum_{e in in(t)} x_e - 1)^2
        in_t_indices = [
            i for i, e in enumerate(self.candidate_edges) if e["v"] == self.dest_id
        ]
        if in_t_indices:
            self.constant_offset += penalty
            for i in in_t_indices:
                self.Q[i, i] += penalty * (-1.0)
            for idx1 in in_t_indices:
                for idx2 in in_t_indices:
                    if idx1 < idx2:
                        self.Q[idx1, idx2] += penalty * 2.0

        # 4. Flow conservation for intermediate nodes v in V \ {s, t}:
        # ( sum_{e in out(v)} x_e - sum_{e in in(v)} x_e )^2
        # = ( sum_{out} x_e )^2 + ( sum_{in} x_e )^2 - 2 ( sum_{out} x_e ) ( sum_{in} x_e )
        intermediate_nodes = [
            v for v in self.candidate_nodes if v not in (self.origin_id, self.dest_id)
        ]

        for v in intermediate_nodes:
            out_v = [i for i, e in enumerate(self.candidate_edges) if e["u"] == v]
            in_v = [i for i, e in enumerate(self.candidate_edges) if e["v"] == v]

            # (sum_{out} x_e)^2 = sum_out x_e + 2 sum_{out1 < out2} x_out1 x_out2
            for i in out_v:
                self.Q[i, i] += penalty * 1.0
            for idx1 in out_v:
                for idx2 in out_v:
                    if idx1 < idx2:
                        self.Q[idx1, idx2] += penalty * 2.0

            # (sum_{in} x_e)^2 = sum_in x_e + 2 sum_{in1 < in2} x_in1 x_in2
            for i in in_v:
                self.Q[i, i] += penalty * 1.0
            for idx1 in in_v:
                for idx2 in in_v:
                    if idx1 < idx2:
                        self.Q[idx1, idx2] += penalty * 2.0

            # -2 ( sum_{out} x_e ) ( sum_{in} x_e )
            for o_idx in out_v:
                for i_idx in in_v:
                    if o_idx < i_idx:
                        self.Q[o_idx, i_idx] -= penalty * 2.0
                    elif i_idx < o_idx:
                        self.Q[i_idx, o_idx] -= penalty * 2.0

    def evaluate_bitstring_energy(self, bitstring: str) -> float:
        """Compute QUBO energy H(x) = x^T Q x + offset for a given binary bitstring."""
        # Qiskit convention: bitstring is often little-endian or big-endian.
        # We assume x[0] corresponds to bitstring[0]
        x = np.array([int(b) for b in bitstring], dtype=float)
        energy = float(x.T @ self.Q @ x + self.constant_offset)
        return round(energy, 4)

    def get_qubo_dictionary(self) -> Dict[Tuple[int, int], float]:
        """Return upper triangular dictionary representation of QUBO matrix."""
        q_dict = {}
        n = self.num_vars
        for i in range(n):
            for j in range(i, n):
                val = self.Q[i, j]
                if abs(val) > 1e-6:
                    q_dict[(i, j)] = round(float(val), 4)
        return q_dict

    def to_ising_pauli_terms(self) -> Tuple[Dict[str, float], float]:
        """Convert QUBO to Ising Hamiltonian: x_i = (1 - Z_i)/2.

        Returns (pauli_dict, ising_offset) where pauli_dict has keys like 'Z_0', 'Z_0 Z_1'.
        """
        pauli_dict = {}
        offset = self.constant_offset

        # Linear and quadratic substitutions
        for i in range(self.num_vars):
            for j in range(i, self.num_vars):
                q_ij = self.Q[i, j]
                if abs(q_ij) < 1e-6:
                    continue

                if i == j:
                    # Q_ii * x_i = Q_ii * (1 - Z_i)/2 = Q_ii/2 - (Q_ii/2) Z_i
                    offset += q_ij / 2.0
                    key = f"Z_{i}"
                    pauli_dict[key] = pauli_dict.get(key, 0.0) - (q_ij / 2.0)
                else:
                    # Q_ij * x_i * x_j = Q_ij * (1 - Z_i)(1 - Z_j)/4
                    # = Q_ij/4 - (Q_ij/4) Z_i - (Q_ij/4) Z_j + (Q_ij/4) Z_i Z_j
                    offset += q_ij / 4.0
                    k_i = f"Z_{i}"
                    k_j = f"Z_{j}"
                    k_ij = f"Z_{i} Z_{j}"
                    pauli_dict[k_i] = pauli_dict.get(k_i, 0.0) - (q_ij / 4.0)
                    pauli_dict[k_j] = pauli_dict.get(k_j, 0.0) - (q_ij / 4.0)
                    pauli_dict[k_ij] = pauli_dict.get(k_ij, 0.0) + (q_ij / 4.0)

        return pauli_dict, round(offset, 4)
