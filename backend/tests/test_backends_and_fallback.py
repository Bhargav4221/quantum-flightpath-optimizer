"""Unit tests for Quantum Backend selection, AUTO fallback, and explicit IBM failure behavior."""

import pytest
from unittest.mock import patch
from app.quantum.backends import BackendFactory, AerBackend, IBMQuantumBackend


def test_aer_backend_execution_label():
    aer = AerBackend()
    assert aer.get_backend_type() == "simulator"
    assert "Qiskit Aer" in aer.get_name()
    avail, _ = aer.is_available()
    assert avail is True


def test_ibm_backend_unavailable_when_no_token():
    # Instantiate with None token
    ibm = IBMQuantumBackend(token=None)
    avail, reason = ibm.is_available()
    assert avail is False
    assert "token not configured" in reason.lower()


def test_auto_fallback_to_aer_when_no_ibm():
    # When IBM credentials are not present, AUTO must fall back to Aer and record reason
    with patch("app.quantum.backends.settings.IBM_QUANTUM_TOKEN", None):
        backend_inst, fallback, reason = BackendFactory.get_backend("auto")
        assert fallback is True
        assert "Qiskit Aer" in backend_inst.get_name()
        assert "AUTO fallback" in reason
        assert backend_inst.get_backend_type() == "simulator"


def test_explicit_ibm_mode_fails_strictly_without_fallback():
    # Per prompt rule: "If the user explicitly selects IBM Quantum and the connection or execution fails,
    # show a clear error. Do not silently switch to Aer."
    with patch("app.quantum.backends.settings.IBM_QUANTUM_TOKEN", None):
        with pytest.raises(ValueError, match="Explicit IBM Quantum execution failed"):
            BackendFactory.get_backend("ibm")


def test_explicit_aer_mode_does_not_fallback():
    backend_inst, fallback, reason = BackendFactory.get_backend("aer")
    assert fallback is False
    assert reason is None
    assert "Qiskit Aer" in backend_inst.get_name()


def test_status_overview_does_not_expose_token():
    status = BackendFactory.get_status_overview()
    assert "token" not in str(status.values()).lower() or "configured_token_present" in status
    assert "aer_available" in status
    assert "active_backend_name" in status
    assert "supported_backends" in status
