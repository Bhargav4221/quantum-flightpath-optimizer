"""Abstract provider interfaces for authoritative aeronautical information.

These interfaces define the contracts for integrating real aeronautical data sources
without rewriting the optimization engine.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from app.models.schemas import (
    Airport,
    AirwaySegment,
    RestrictedAirspace,
    AircraftPerformance,
    DataProvenance,
)


class AirportDataProvider(ABC):
    """Interface for authoritative aerodrome and airport data."""

    @abstractmethod
    def search_airports(self, query: str, limit: int = 10) -> List[Airport]:
        """Search airports by name, ICAO, IATA, city, or country."""
        pass

    @abstractmethod
    def get_airport_by_code(self, code: str) -> Optional[Airport]:
        """Retrieve verified airport details by ICAO or IATA code."""
        pass

    @abstractmethod
    def get_all_airports(self) -> List[Airport]:
        """Return all available verified airports."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return dataset provenance, source, validity and version."""
        pass


class AeronauticalRouteDataProvider(ABC):
    """Interface for published ATS routes, airways, waypoints, fixes, and procedures."""

    @abstractmethod
    def get_airway_segments(self) -> List[AirwaySegment]:
        """Return all published airway segments in the network."""
        pass

    @abstractmethod
    def get_terminal_transitions(self, airport_icao: str) -> List[Dict[str, Any]]:
        """Return published departure/arrival transition routes connecting airport to airway fixes."""
        pass

    @abstractmethod
    def get_waypoints(self) -> Dict[str, Dict[str, Any]]:
        """Return all published waypoints, fixes, and navaids."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return dataset provenance, source, validity and version."""
        pass


class AirspaceDataProvider(ABC):
    """Interface for controlled, restricted, and prohibited airspaces."""

    @abstractmethod
    def get_restricted_airspaces(self) -> List[RestrictedAirspace]:
        """Return active published restricted, prohibited, or danger areas."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return dataset provenance, source, validity and version."""
        pass


class WeatherDataProvider(ABC):
    """Interface for operational weather (METAR, TAF, en-route winds aloft)."""

    @abstractmethod
    def is_live_configured(self) -> bool:
        """Return True only if genuine live weather provider API is configured."""
        pass

    @abstractmethod
    def get_weather_for_airport(self, icao: str) -> Dict[str, Any]:
        """Retrieve weather observation or report unavailable."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return weather data source status and configuration."""
        pass


class NotamDataProvider(ABC):
    """Interface for Notices to Airmen (NOTAMs)."""

    @abstractmethod
    def is_live_configured(self) -> bool:
        """Return True only if genuine NOTAM provider is configured."""
        pass

    @abstractmethod
    def get_notams_for_route(self, route_points: List[str]) -> List[Dict[str, Any]]:
        """Retrieve applicable NOTAMs or report unavailable."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return NOTAM data source status and configuration."""
        pass


class CongestionDataProvider(ABC):
    """Interface for en-route traffic congestion information."""

    @abstractmethod
    def is_live_configured(self) -> bool:
        """Return True only if live radar/ADS-B traffic feed is configured."""
        pass

    @abstractmethod
    def get_edge_congestion(self, from_point: str, to_point: str) -> Dict[str, Any]:
        """Return congestion score and whether it is live or modelled."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return traffic/congestion data source status and configuration."""
        pass


class AircraftDataProvider(ABC):
    """Interface for documented aircraft aerodynamic and performance models."""

    @abstractmethod
    def get_aircraft(self, model_code: str) -> Optional[AircraftPerformance]:
        """Return aircraft performance parameters."""
        pass

    @abstractmethod
    def list_supported_aircraft(self) -> List[AircraftPerformance]:
        """Return list of supported aircraft models."""
        pass

    @abstractmethod
    def get_provenance(self) -> DataProvenance:
        """Return aircraft performance data source status."""
        pass
