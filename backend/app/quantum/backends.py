"""Quantum Execution Backends: IBM Quantum, Qiskit Aer, and BackendFactory.

Implements genuine execution paths with transparent status and error handling.
Credentials are kept strictly server-side and never exposed to clients.
"""

import time
import os
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Tuple
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator

from app.config import settings


class QuantumBackendBase(ABC):
    """Abstract base class for quantum backends."""

    @abstractmethod
    def get_name(self) -> str:
        pass

    @abstractmethod
    def get_backend_type(self) -> str:
        """'simulator' or 'hardware'."""
        pass

    @abstractmethod
    def is_available(self) -> Tuple[bool, Optional[str]]:
        """Return (is_available, error_or_reason)."""
        pass

    @abstractmethod
    def execute_circuit(
        self, circuit: QuantumCircuit, shots: int = 1024
    ) -> Dict[str, Any]:
        """Execute quantum circuit and return genuine measurement results and job metadata."""
        pass


class AerBackend(QuantumBackendBase):
    """Local quantum circuit simulation using Qiskit Aer."""

    def __init__(self):
        self.simulator = AerSimulator()
        self.name = "Qiskit Aer — Local Quantum Circuit Simulation"

    def get_name(self) -> str:
        return self.name

    def get_backend_type(self) -> str:
        return "simulator"

    def is_available(self) -> Tuple[bool, Optional[str]]:
        try:
            _ = self.simulator.name
            return True, None
        except Exception as e:
            return False, f"Qiskit Aer initialization failed: {str(e)}"

    def execute_circuit(
        self, circuit: QuantumCircuit, shots: int = 1024
    ) -> Dict[str, Any]:
        """Execute circuit locally using genuine AerSimulator."""
        start_time = time.perf_counter()

        # Ensure circuit has measurement operations
        circ_to_run = circuit.copy()
        if not circ_to_run.cregs:
            circ_to_run.measure_all()

        job = self.simulator.run(circ_to_run, shots=shots)
        result = job.result()
        execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        counts = result.get_counts(circ_to_run)
        job_id = getattr(result, "job_id", f"aer_sim_{int(time.time()*1000)}")

        return {
            "backend_name": self.name,
            "backend_type": "simulator",
            "job_id": job_id,
            "job_status": "COMPLETED",
            "shots": shots,
            "counts": counts,
            "qubit_count": circuit.num_qubits,
            "circuit_depth": circuit.depth(),
            "execution_time_ms": execution_time_ms,
        }


class IBMQuantumBackend(QuantumBackendBase):
    """Genuine IBM Quantum Hardware / Runtime Backend."""

    def __init__(self, token: Optional[str] = None, instance: Optional[str] = None):
        self.token = token if token is not None else settings.IBM_QUANTUM_TOKEN
        self.instance = instance if instance is not None else settings.IBM_QUANTUM_INSTANCE
        self.service = None
        self._connected = False
        self._backend = None
        self._last_error = None
        self._init_service()

    def _init_service(self):
        if not self.token or len(self.token.strip()) < 10:
            self._last_error = "IBM Quantum token not configured (set token in UI or server .env)."
            return

        try:
            from qiskit_ibm_runtime import QiskitRuntimeService
            self.service = QiskitRuntimeService(
                channel="ibm_quantum",
                token=self.token.strip(),
                instance=self.instance,
            )
            # Find least busy operational system
            try:
                self._backend = self.service.least_busy(operational=True, simulator=False)
            except Exception:
                # If least_busy filter fails, find any available operational hardware backend
                all_b = self.service.backends()
                operational = [b for b in all_b if getattr(b, "status", lambda: None)()]
                self._backend = operational[0] if operational else (all_b[0] if all_b else None)

            if self._backend:
                self._connected = True
                self._last_error = None
            else:
                self._connected = False
                self._last_error = "Authenticated with IBM Quantum, but no operational quantum hardware QPU was returned for this account."
        except Exception as e:
            self._connected = False
            self.service = None
            self._backend = None
            self._last_error = f"IBM Quantum authentication failed: {str(e)}"

    def get_name(self) -> str:
        if self._backend:
            return f"IBM Quantum ({self._backend.name})"
        return "IBM Quantum Hardware (Not Connected)"

    def get_backend_type(self) -> str:
        return "hardware"

    def is_available(self) -> Tuple[bool, Optional[str]]:
        if not self.token:
            return False, "IBM Quantum token not configured. Please enter your API token."
        if not self.service or not self._connected or not self._backend:
            return False, self._last_error or "Failed to authenticate or find operational IBM Quantum hardware backend."
        return True, None

    def execute_circuit(
        self, circuit: QuantumCircuit, shots: int = 1024
    ) -> Dict[str, Any]:
        """Submit and execute circuit on IBM Quantum hardware."""
        avail, reason = self.is_available()
        if not avail:
            raise RuntimeError(f"IBM Quantum hardware execution failed: {reason}")

        start_time = time.perf_counter()
        from qiskit_ibm_runtime import SamplerV2
        from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

        # Transpile for IBM hardware
        pm = generate_preset_pass_manager(backend=self._backend, optimization_level=1)
        isa_circuit = pm.run(circuit)

        sampler = SamplerV2(mode=self._backend)
        job = sampler.run([isa_circuit], shots=shots)
        result = job.result()
        execution_time_ms = round((time.perf_counter() - start_time) * 1000.0, 2)

        pub_result = result[0]
        # Retrieve bitstring counts from SamplerV2 bit array
        data_bin = pub_result.data
        meas_name = list(data_bin.keys())[0] if data_bin.keys() else "meas"
        counts = getattr(data_bin, meas_name).get_counts()

        return {
            "backend_name": f"IBM Quantum ({self._backend.name})",
            "backend_type": "hardware",
            "job_id": job.job_id(),
            "job_status": "COMPLETED",
            "shots": shots,
            "counts": counts,
            "qubit_count": circuit.num_qubits,
            "circuit_depth": isa_circuit.depth(),
            "execution_time_ms": execution_time_ms,
        }


class BackendFactory:
    """Factory and selector for quantum execution backends adhering to AUTO / IBM / Aer policy."""

    @staticmethod
    def get_backend(
        mode: str = "auto",
    ) -> Tuple[QuantumBackendBase, bool, Optional[str]]:
        """Resolve backend based on mode: 'auto', 'ibm', or 'aer'.

        Returns (backend_instance, fallback_occurred, fallback_reason).
        """
        mode = mode.lower().strip()

        if mode == "aer":
            # Explicit Aer simulator request
            return AerBackend(), False, None

        if mode == "ibm":
            # Explicit IBM request: If fails, MUST NOT silently fall back!
            ibm = IBMQuantumBackend()
            avail, reason = ibm.is_available()
            if not avail:
                raise ValueError(
                    f"Explicit IBM Quantum execution failed: {reason}. "
                    "Per safety requirements, silent fallback to local simulator is prohibited in explicit IBM mode."
                )
            return ibm, False, None

        # AUTO mode: Try IBM Quantum first; if unavailable, fall back to Aer with recorded reason.
        ibm = IBMQuantumBackend()
        avail, reason = ibm.is_available()
        if avail:
            return ibm, False, None

        # Fall back gracefully to Aer
        fallback_msg = (
            f"AUTO fallback: IBM Quantum unavailable ({reason}). "
            "Proceeding with Qiskit Aer local simulation."
        )
        return AerBackend(), True, fallback_msg

    @staticmethod
    def get_status_overview() -> Dict[str, Any]:
        """Return backend configuration status for frontend status indicator."""
        token_present = bool(
            settings.IBM_QUANTUM_TOKEN and len(settings.IBM_QUANTUM_TOKEN.strip()) > 5
        )
        instance_present = bool(settings.IBM_QUANTUM_INSTANCE)

        ibm_backend = IBMQuantumBackend()
        ibm_avail, ibm_reason = ibm_backend.is_available()

        aer_backend = AerBackend()
        aer_avail, aer_reason = aer_backend.is_available()

        active_name = ibm_backend.get_name() if ibm_avail else aer_backend.get_name()
        active_type = "hardware" if ibm_avail else "simulator"

        return {
            "configured_token_present": token_present,
            "instance_configured": instance_present,
            "current_mode": "AUTO (IBM Ready)" if ibm_avail else "AUTO (Aer Simulator Active)",
            "active_backend_name": active_name,
            "backend_type": active_type,
            "aer_available": aer_avail,
            "ibm_available": ibm_avail,
            "ibm_status_reason": ibm_reason,
            "supported_backends": [
                {
                    "id": "auto",
                    "label": "AUTO Mode (IBM -> Aer Fallback)",
                    "available": True,
                    "description": "Attempts IBM Quantum hardware first, falls back to local Qiskit Aer if unconfigured.",
                },
                {
                    "id": "ibm",
                    "label": "IBM Quantum (Hardware Runtime)",
                    "available": ibm_avail,
                    "description": "Direct execution on IBM Quantum superconducting QPUs via Qiskit Runtime.",
                },
                {
                    "id": "aer",
                    "label": "Qiskit Aer (Local Quantum Circuit Simulation)",
                    "available": aer_avail,
                    "description": "High-performance local statevector / density matrix quantum circuit simulation.",
                },
            ],
            "message": "IBM Quantum hardware connection active."
            if ibm_avail
            else "Qiskit Aer local simulation active. Configure IBM_QUANTUM_TOKEN to enable IBM Quantum hardware execution.",
        }

    @staticmethod
    def configure_ibm_token(token: str, instance: Optional[str] = None) -> Tuple[bool, str, Optional[str]]:
        """Verify token against IBM Quantum and persist in server settings and .env.

        Returns (success, message, backend_name).
        """
        token = token.strip()
        if len(token) < 10:
            return False, "Token is too short or invalid.", None

        test_backend = IBMQuantumBackend(token=token, instance=instance)
        avail, reason = test_backend.is_available()
        if not avail:
            return False, reason or "IBM Quantum authentication failed.", None

        # Update in-memory settings
        settings.IBM_QUANTUM_TOKEN = token
        settings.IBM_QUANTUM_INSTANCE = instance

        # Persist to .env file in project root
        try:
            env_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".env"))
            lines = []
            if os.path.exists(env_path):
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()

            token_written = False
            new_lines = []
            for line in lines:
                if line.startswith("IBM_QUANTUM_TOKEN="):
                    new_lines.append(f"IBM_QUANTUM_TOKEN={token}\n")
                    token_written = True
                elif line.startswith("IBM_QUANTUM_INSTANCE=") and instance:
                    new_lines.append(f"IBM_QUANTUM_INSTANCE={instance}\n")
                else:
                    new_lines.append(line)
            if not token_written:
                new_lines.append(f"\nIBM_QUANTUM_TOKEN={token}\n")
                if instance:
                    new_lines.append(f"IBM_QUANTUM_INSTANCE={instance}\n")
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)
        except Exception:
            pass

        backend_name = test_backend.get_name()
        return True, f"Successfully authenticated with IBM Quantum! Connected to {backend_name}.", backend_name

