"""Unit tests for airport search, retrieval, and validation."""

import pytest
from app.providers.airport_provider import DefaultAirportDataProvider


@pytest.fixture
def provider():
    return DefaultAirportDataProvider()


def test_search_airports_by_city(provider):
    results = provider.search_airports("Hyderabad")
    assert len(results) >= 1
    hyd = results[0]
    assert hyd.icao == "VOHS"
    assert hyd.iata == "HYD"
    assert "Rajiv Gandhi" in hyd.name


def test_search_airports_by_iata(provider):
    results = provider.search_airports("DEL")
    assert len(results) >= 1
    assert any(a.icao == "VIDP" for a in results)


def test_search_airports_by_icao(provider):
    results = provider.search_airports("VOBL")
    assert len(results) >= 1
    assert results[0].city == "Bengaluru"


def test_get_airport_by_code_case_insensitive(provider):
    apt_upper = provider.get_airport_by_code("bom")
    assert apt_upper is not None
    assert apt_upper.icao == "VABB"
    assert apt_upper.iata == "BOM"


def test_get_nonexistent_airport(provider):
    apt = provider.get_airport_by_code("NONEXISTENT_ICAO")
    assert apt is None


def test_airport_coordinates_and_elevation(provider):
    delhi = provider.get_airport_by_code("VIDP")
    assert delhi is not None
    assert 28.0 < delhi.latitude < 29.0
    assert 77.0 < delhi.longitude < 78.0
    assert delhi.elevation_ft > 0
    assert delhi.runways_count >= 1


def test_airport_provenance_metadata(provider):
    prov = provider.get_provenance()
    assert prov.provider != ""
    assert prov.dataset_version != ""
    assert prov.validation_status == "Authoritative published data"
    assert prov.live_connected is False
