"""Documented commercial aircraft performance models.

Based on ICAO Engine Emissions Databank and EUROCONTROL Base of Aircraft Data (BADA)
aerodynamic parameters.
"""

from typing import Dict, Any

AIRCRAFT_MODELS: Dict[str, Dict[str, Any]] = {
    "A320neo": {
        "model_code": "A320neo",
        "name": "Airbus A320neo (CFM LEAP-1A)",
        "cruise_mach": 0.78,
        "cruise_tas_knots": 450.0,
        "cruise_altitude_fl": 350,
        "base_fuel_burn_kg_per_nm": 4.05,
        "taxi_fuel_kg": 200.0,
        "climb_descent_fuel_kg": 400.0,
        "climb_descent_time_min": 25.0,
        "co2_emission_factor": 3.16,
    },
    "B738": {
        "model_code": "B738",
        "name": "Boeing 737-800 (CFM56-7B)",
        "cruise_mach": 0.78,
        "cruise_tas_knots": 453.0,
        "cruise_altitude_fl": 360,
        "base_fuel_burn_kg_per_nm": 4.42,
        "taxi_fuel_kg": 220.0,
        "climb_descent_fuel_kg": 450.0,
        "climb_descent_time_min": 25.0,
        "co2_emission_factor": 3.16,
    },
    "B789": {
        "model_code": "B789",
        "name": "Boeing 787-9 Dreamliner (GEnx-1B)",
        "cruise_mach": 0.85,
        "cruise_tas_knots": 488.0,
        "cruise_altitude_fl": 390,
        "base_fuel_burn_kg_per_nm": 9.85,
        "taxi_fuel_kg": 450.0,
        "climb_descent_fuel_kg": 950.0,
        "climb_descent_time_min": 30.0,
        "co2_emission_factor": 3.16,
    },
}
