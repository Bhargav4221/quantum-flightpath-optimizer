"""Integration tests for FastAPI endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "Quantum FlightPath Optimizer" in data["name"]
    assert "disclaimer" in data


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json()["status"] == "healthy"


def test_search_airports_api():
    res = client.get("/api/airports/search?q=delhi")
    assert res.status_code == 200
    airports = res.json()
    assert len(airports) >= 1
    assert airports[0]["icao"] == "VIDP"


def test_get_airport_by_code_valid():
    res = client.get("/api/airports/HYD")
    assert res.status_code == 200
    data = res.json()
    assert data["icao"] == "VOHS"
    assert data["city"] == "Hyderabad"


def test_get_airport_by_code_not_found():
    res = client.get("/api/airports/ZZZZ")
    assert res.status_code == 404
    assert "not found" in res.json()["detail"].lower()


def test_backend_status_endpoint():
    res = client.get("/api/backend/status")
    assert res.status_code == 200
    data = res.json()
    assert "active_backend_name" in data
    assert "supported_backends" in data
    assert data["aer_available"] is True


def test_data_provenance_endpoint():
    res = client.get("/api/data/provenance")
    assert res.status_code == 200
    provenance = res.json()
    assert len(provenance) >= 5
    names = [p["dataset_name"] for p in provenance]
    assert any("Aerodrome" in n for n in names)
    assert any("Airway Network" in n for n in names)


def test_optimize_same_airport_rejected():
    payload = {
        "origin": "DEL",
        "destination": "DEL",
        "objective": "balanced",
        "backend": "aer",
    }
    res = client.post("/api/optimize", json=payload)
    assert res.status_code == 400
    assert "cannot be identical" in res.json()["detail"]


def test_optimize_valid_delhi_to_hyderabad():
    payload = {
        "origin": "DEL",
        "destination": "HYD",
        "objective": "balanced",
        "backend": "aer",
        "aircraft_type": "A320neo",
        "shots": 256,
    }
    res = client.post("/api/optimize", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "classical_route" in data
    assert "quantum_route" in data
    assert "metrics_comparison" in data
    assert data["classical_route"]["metrics"]["distance_nm"] > 600.0
    assert data["quantum_route"]["metrics"]["distance_nm"] > 600.0
    assert "Qiskit Aer" in data["backend_execution"]["active_backend"]
    assert "disclaimer" in data


def test_optimize_explicit_ibm_failure_reported_cleanly():
    # Calling explicit IBM without token must return 400 with explanation
    payload = {
        "origin": "DEL",
        "destination": "HYD",
        "objective": "balanced",
        "backend": "ibm",
        "shots": 256,
    }
    res = client.post("/api/optimize", json=payload)
    assert res.status_code == 400
    assert "Explicit IBM Quantum execution failed" in res.json()["detail"]


def test_quantum_test_endpoint():
    res = client.post("/api/quantum/test?backend_mode=aer")
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    assert "counts" in data
    assert data["test_circuit_qubits"] == 2


def test_configure_token_short_rejected():
    res = client.post("/api/backend/configure-token", json={"token": "short"})
    assert res.status_code == 422  # Pydantic min_length validation error

