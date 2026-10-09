/**
 * API client for Quantum FlightPath Optimizer backend.
 */

const API_BASE = '/api';

export async function searchAirports(query) {
  const res = await fetch(`${API_BASE}/airports/search?q=${encodeURIComponent(query || '')}`);
  if (!res.ok) throw new Error('Failed to search airports');
  return res.json();
}

export async function getAirport(code) {
  const res = await fetch(`${API_BASE}/airports/${encodeURIComponent(code)}`);
  if (!res.ok) throw new Error(`Airport ${code} not found`);
  return res.json();
}

export async function getBackendStatus() {
  const res = await fetch(`${API_BASE}/backend/status`);
  if (!res.ok) throw new Error('Failed to fetch quantum backend status');
  return res.json();
}

export async function configureIBMToken(token, instance = null) {
  const res = await fetch(`${API_BASE}/backend/configure-token`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token, instance }),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'IBM Quantum authentication failed');
  }
  return res.json();
}

export async function testQuantumBackend(mode = 'auto') {
  const res = await fetch(`${API_BASE}/quantum/test?backend_mode=${encodeURIComponent(mode)}`, {
    method: 'POST',
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Quantum test failed');
  }
  return res.json();
}

export async function getDataProvenance() {
  const res = await fetch(`${API_BASE}/data/provenance`);
  if (!res.ok) throw new Error('Failed to fetch data provenance');
  return res.json();
}

export async function getAirwaysNetwork() {
  const res = await fetch(`${API_BASE}/airways/network`);
  if (!res.ok) throw new Error('Failed to fetch airway network');
  return res.json();
}

export async function getRestrictedAirspaces() {
  const res = await fetch(`${API_BASE}/airspace/restricted`);
  if (!res.ok) throw new Error('Failed to fetch restricted airspace');
  return res.json();
}

export async function getAircraftTypes() {
  const res = await fetch(`${API_BASE}/aircraft/types`);
  if (!res.ok) throw new Error('Failed to fetch aircraft types');
  return res.json();
}

export async function optimizeRoute(payload) {
  const res = await fetch(`${API_BASE}/optimize`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Route optimization failed');
  }
  return res.json();
}
