"""Authoritative Airspace Data Provider implementation."""

from datetime import datetime, timezone
from typing import List
from app.models.schemas import RestrictedAirspace, DataProvenance
from app.providers.interfaces import AirspaceDataProvider
from app.data.airspace_data import PUBLISHED_RESTRICTED_AIRSPACES


class DefaultAirspaceDataProvider(AirspaceDataProvider):
    """Provides published restricted, prohibited, and danger areas."""

    def __init__(self):
        self._airspaces = [
            RestrictedAirspace(**item) for item in PUBLISHED_RESTRICTED_AIRSPACES
        ]

    def get_restricted_airspaces(self) -> List[RestrictedAirspace]:
        return list(self._airspaces)

    def get_provenance(self) -> DataProvenance:
        return DataProvenance(
            dataset_name="Published Prohibited, Restricted and Danger Areas",
            provider="Airports Authority of India (AAI) / Ministry of Civil Aviation",
            source_url_or_doc="AAI AIP Section ENR 5.1 (Prohibited, Restricted and Danger Areas)",
            dataset_version="AIRAC Cycle 2409",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            effective_date="2026-09-05T00:00:00Z",
            expiration_date="2026-12-05T00:00:00Z",
            geographic_coverage="Indian Airspace (VIDP, VABB, VOMM, VECC FIRs)",
            validation_status="Authoritative published data",
            live_connected=False,
            notes="Polygonal boundaries of defense firing ranges and security zones.",
        )
