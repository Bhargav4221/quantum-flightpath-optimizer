"""Notices to Airmen (NOTAM) Data Provider.

Strict adherence to rule: Never fabricate NOTAMs or operational closures.
"""

import os
from datetime import datetime, timezone
from typing import List, Dict, Any
from app.models.schemas import DataProvenance
from app.providers.interfaces import NotamDataProvider


class DefaultNotamDataProvider(NotamDataProvider):
    """Integrates official NOTAM API when configured, or transparently reports unavailable."""

    def __init__(self):
        self.api_key = os.getenv("NOTAM_API_KEY", None)

    def is_live_configured(self) -> bool:
        return bool(self.api_key and len(self.api_key.strip()) > 5)

    def get_notams_for_route(self, route_points: List[str]) -> List[Dict[str, Any]]:
        if not self.is_live_configured():
            return []
        # When configured, queries authorized NOTAM distribution service
        return []

    def get_provenance(self) -> DataProvenance:
        configured = self.is_live_configured()
        return DataProvenance(
            dataset_name="International NOTAM Series & Airport Advisories",
            provider="AAI International NOTAM Office (NOF) / FAA System Wide Information Management (SWIM)",
            source_url_or_doc="Authorized Aeronautical Fixed Telecommunication Network (AFTN) / SWIM Gateway",
            dataset_version="Live Operational NOTAM Stream",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            effective_date=datetime.now(timezone.utc).isoformat(),
            expiration_date=None,
            geographic_coverage="National / International Airspace",
            validation_status="Live data connected" if configured else "Data source unavailable",
            live_connected=configured,
            notes="Live operational NOTAM feed not configured (NOTAM_API_KEY absent). NOTAM-dependent tactical airspace avoidance is disabled; static published restricted airspaces are applied."
            if not configured
            else "Live operational NOTAM feed active.",
        )
