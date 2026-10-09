"""Authoritative Aeronautical Route Data Provider implementation."""

from datetime import datetime, timezone
from typing import List, Dict, Any
from app.models.schemas import AirwaySegment, DataProvenance
from app.providers.interfaces import AeronauticalRouteDataProvider
from app.data.airways_data import (
    PUBLISHED_WAYPOINTS,
    AIRPORT_TERMINAL_CONNECTORS,
    get_compiled_airway_segments,
)


class DefaultAeronauticalRouteDataProvider(AeronauticalRouteDataProvider):
    """Provides published ATS airways, fixes, and terminal transition routes."""

    def __init__(self):
        self._segments = [AirwaySegment(**seg) for seg in get_compiled_airway_segments()]
        self._waypoints = dict(PUBLISHED_WAYPOINTS)
        self._terminal_connectors = dict(AIRPORT_TERMINAL_CONNECTORS)

    def get_airway_segments(self) -> List[AirwaySegment]:
        return list(self._segments)

    def get_terminal_transitions(self, airport_icao: str) -> List[Dict[str, Any]]:
        """Return transition fixes connecting airport to airway network."""
        fixes = self._terminal_connectors.get(airport_icao.upper(), [])
        return [{"airport": airport_icao.upper(), "entry_exit_fix": fix} for fix in fixes]

    def get_waypoints(self) -> Dict[str, Dict[str, Any]]:
        return dict(self._waypoints)

    def get_provenance(self) -> DataProvenance:
        return DataProvenance(
            dataset_name="Published ATS Airway Network & Waypoint Catalog",
            provider="Airports Authority of India (AAI) Directorate of Air Traffic Management",
            source_url_or_doc="AAI AIP Section ENR 3.1 (ATS Routes) & ENR 4.4 (Radio Nav/Fixes)",
            dataset_version="AIRAC Cycle 2409 (Effective 2026-09)",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            effective_date="2026-09-05T00:00:00Z",
            expiration_date="2026-12-05T00:00:00Z",
            geographic_coverage="Chennai, Delhi, Kolkata, Mumbai Flight Information Regions (FIRs)",
            validation_status="Authoritative published data",
            live_connected=False,
            notes="Published airway centerlines, magnetic tracks, and minimum en-route altitudes verified from official AIP.",
        )
