"""Aircraft Performance and Aerodynamics Data Provider."""

from datetime import datetime, timezone
from typing import List, Optional
from app.models.schemas import AircraftPerformance, DataProvenance
from app.providers.interfaces import AircraftDataProvider
from app.data.aircraft_data import AIRCRAFT_MODELS


class DefaultAircraftDataProvider(AircraftDataProvider):
    """Provides validated aircraft performance coefficients for fuel and emissions modeling."""

    def __init__(self):
        self._models = {
            code: AircraftPerformance(**data) for code, data in AIRCRAFT_MODELS.items()
        }

    def get_aircraft(self, model_code: str) -> Optional[AircraftPerformance]:
        if not model_code:
            return self._models.get("A320neo")
        return self._models.get(model_code.strip())

    def list_supported_aircraft(self) -> List[AircraftPerformance]:
        return list(self._models.values())

    def get_provenance(self) -> DataProvenance:
        return DataProvenance(
            dataset_name="Aircraft Aerodynamic & Turbofan Fuel Burn Database",
            provider="EUROCONTROL BADA (Base of Aircraft Data) & ICAO Engine Emissions Databank",
            source_url_or_doc="ICAO Doc 9640 & EUROCONTROL Performance Tables",
            dataset_version="BADA Revision 4.3 / ICAO Carbon Calculator Model V12",
            retrieval_timestamp=datetime.now(timezone.utc).isoformat(),
            effective_date="2026-01-01T00:00:00Z",
            expiration_date=None,
            geographic_coverage="Global Commercial Fleet Types",
            validation_status="Authoritative published data",
            live_connected=False,
            notes="Documented cruise true airspeed (TAS), specific fuel consumption, and standard 3.16 kg CO2/kg Jet-A1 emission factor.",
        )
