"""Unit tests for aircraft aerodynamic fuel and CO2 emissions model."""

import pytest
from app.models.schemas import AircraftPerformance, OptimizationWeights
from app.metrics.fuel_emissions import FuelEmissionsCalculator


@pytest.fixture
def a320():
    return AircraftPerformance(
        model_code="A320neo",
        name="Airbus A320neo",
        cruise_mach=0.78,
        cruise_tas_knots=450.0,
        base_fuel_burn_kg_per_nm=4.05,
        climb_descent_fuel_kg=400.0,
        climb_descent_time_min=25.0,
        co2_emission_factor=3.16,
    )


@pytest.fixture
def b789():
    return AircraftPerformance(
        model_code="B789",
        name="Boeing 787-9 Dreamliner",
        cruise_mach=0.85,
        cruise_tas_knots=488.0,
        base_fuel_burn_kg_per_nm=9.85,
        climb_descent_fuel_kg=950.0,
        climb_descent_time_min=30.0,
        co2_emission_factor=3.16,
    )


def test_segment_metrics_co2_ratio(a320):
    metrics = FuelEmissionsCalculator.calculate_segment_metrics(
        distance_nm=200.0, aircraft=a320, congestion_score=0.2
    )
    # CO2 must equal Fuel * 3.16 within rounding
    expected_co2 = metrics["fuel_kg"] * 3.16
    assert abs(metrics["co2_kg"] - expected_co2) < 2.0
    assert metrics["distance_km"] == round(200.0 * 1.852, 2)


def test_full_route_metrics_incorporates_terminal_phase(a320):
    weights = OptimizationWeights(distance=0.2, fuel=0.25, co2=0.3, time=0.15, congestion=0.1)
    route_m = FuelEmissionsCalculator.calculate_full_route_metrics(
        total_distance_nm=700.0,
        aircraft=a320,
        avg_congestion=0.3,
        weights=weights,
    )

    # Total fuel must be > cruise fuel alone (700 * 4.05 = 2835) because of climb/descent + taxi
    assert route_m.estimated_fuel_kg > (700.0 * 4.05)
    # Estimated time must be > cruise time (700/450 * 60 = 93.3 min) because of climb/descent
    assert route_m.estimated_time_minutes > 93.3
    # Objective value must be positive
    assert route_m.objective_value > 0


def test_widebody_consumes_more_fuel_than_narrowbody(a320, b789):
    weights = OptimizationWeights(distance=0.2, fuel=0.25, co2=0.3, time=0.15, congestion=0.1)
    m_a320 = FuelEmissionsCalculator.calculate_full_route_metrics(
        total_distance_nm=800.0, aircraft=a320, avg_congestion=0.2, weights=weights
    )
    m_b789 = FuelEmissionsCalculator.calculate_full_route_metrics(
        total_distance_nm=800.0, aircraft=b789, avg_congestion=0.2, weights=weights
    )

    assert m_b789.estimated_fuel_kg > m_a320.estimated_fuel_kg * 1.8
    assert m_b789.estimated_co2_kg > m_a320.estimated_co2_kg * 1.8


def test_weights_normalization():
    w = OptimizationWeights(distance=0.4, fuel=0.3, co2=0.1, time=0.1, congestion=0.1)
    norm = w.normalized()
    total = sum(norm.values())
    assert abs(total - 1.0) < 0.001
