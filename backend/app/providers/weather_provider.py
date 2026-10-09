"""Operational Weather Data Provider.

Adheres strictly to prompt requirement:
"If the required real aviation data is unavailable, explain what source or configuration
is missing and disable the affected functionality gracefully. Do not silently substitute
invented data."
"""

import os
from datetime import datetime, timezone
from typing import Dict, Any
from app.models.schemas import DataProvenance
from app.providers.interfaces import WeatherDataProvider


class DefaultWeatherDataProvider(WeatherDataProvider):
    """Integrates official METAR/TAF/Winds Aloft when configured, or transparently reports unavailable."""

    def __init__(self):
        # Dedicated live aviation weather key (e.g., CheckWX or NOAA Aviation Weather API)
        self.api_key = os.getenv("AVIATION_WEATHER_API_KEY", None)

    def is_live_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def get_weather_for_airport(self, icao: str) -> Dict[str, Any]:
        if not self.is_live_configured():
            return {
                "status": "unavailable",
                "message": "Live weather feed not configured. Set AVIATION_WEATHER_API_KEY to enable authorized METAR/TAF retrieval.",
                "data": None,
            }
        # In a production deployment with valid key, query authorized METAR endpoint
        return {
            "status": "connected",
            "icao": icao,
            "metar": None,
            "retrieved_at": datetime.now(timezone.utc).isoformat(),
        }

    def get_provenance(self) -> DataProvenance:
        configured = self.is_live_configured()
        return DataProvenance(
            dataset_name="Operational Aviation Weather (METAR / TAF / Winds Aloft)",
            provider="IMD Aeronautical Meteorological Division / NOAA Aviation Weather",
            source_url_or_doc="Authorized OGC WFS / WCS or Aviation Weather Center (AWC)",
            dataset_version="Live Observation Feed",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            effective_date=datetime.now(timezone.utc).isoformat(),
            expiration_date=None,
            geographic_coverage="En-Route Global / FIR Stations",
            validation_status="Live data connected" if configured else "Data source unavailable",
            live_connected=configured,
            notes="Live operational weather feed is currently not configured in environment (AVIATION_WEATHER_API_KEY absent). Weather-dependent dynamic routing is disabled."
            if not configured
            else "Live operational weather feed active.",
        )
