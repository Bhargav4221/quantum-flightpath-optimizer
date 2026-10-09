import React, { useEffect, useState } from 'react';
import {
  MapContainer,
  TileLayer,
  Polyline,
  CircleMarker,
  Marker,
  Popup,
  Polygon,
  useMap,
} from 'react-leaflet';
import L from 'leaflet';
import { Layers, ShieldAlert, Compass, Navigation } from 'lucide-react';

// Custom Map Auto-Fitter
function MapAutoFit({ bounds }) {
  const map = useMap();
  useEffect(() => {
    if (bounds && bounds.length >= 2) {
      try {
        map.fitBounds(bounds, { padding: [50, 50], maxZoom: 8 });
      } catch (e) {
        console.error('Fit bounds error:', e);
      }
    }
  }, [bounds, map]);
  return null;
}

// Custom airport icon
const createAirportIcon = (color, label) =>
  L.divIcon({
    className: 'custom-airport-marker',
    html: `
      <div style="background-color: ${color}; width: 26px; height: 26px; border-radius: 50%; border: 2px solid white; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 10px ${color}; color: white; font-weight: bold; font-size: 10px; font-family: monospace;">
        ${label}
      </div>
    `,
    iconSize: [26, 26],
    iconAnchor: [13, 13],
  });

export default function MapView({
  origin,
  destination,
  classicalRoute,
  quantumRoute,
  airwaysNetwork,
  restrictedAirspaces,
}) {
  const [showAirways, setShowAirways] = useState(true);
  const [showRestricted, setShowRestricted] = useState(true);

  // Compute map center and bounding box
  const defaultCenter = [20.5937, 78.9629]; // Center of India
  const defaultZoom = 5;

  let bounds = [];
  if (origin) bounds.push([origin.latitude, origin.longitude]);
  if (destination) bounds.push([destination.latitude, destination.longitude]);
  if (classicalRoute?.coordinates) {
    classicalRoute.coordinates.forEach((coord) => bounds.push(coord));
  }
  if (quantumRoute?.coordinates) {
    quantumRoute.coordinates.forEach((coord) => bounds.push(coord));
  }

  return (
    <div className="relative w-full h-[520px] rounded-xl overflow-hidden border border-slate-800 shadow-2xl bg-slate-950">
      {/* Floating Map Controls & Layer Toggles */}
      <div className="absolute top-3 right-3 z-[1000] flex flex-col gap-2 bg-slate-900/90 border border-slate-700/80 rounded-lg p-2 backdrop-blur-md shadow-xl text-xs">
        <div className="flex items-center gap-1.5 font-semibold text-slate-200 border-b border-slate-800 pb-1">
          <Layers className="w-3.5 h-3.5 text-cyan-400" />
          <span>Aeronautical Layers</span>
        </div>
        <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-white">
          <input
            type="checkbox"
            checked={showAirways}
            onChange={(e) => setShowAirways(e.target.checked)}
            className="accent-cyan-400 rounded"
          />
          <span>Published ATS Airways</span>
        </label>
        <label className="flex items-center gap-2 cursor-pointer text-slate-300 hover:text-white">
          <input
            type="checkbox"
            checked={showRestricted}
            onChange={(e) => setShowRestricted(e.target.checked)}
            className="accent-amber-500 rounded"
          />
          <span>Restricted Airspace (ENR 5.1)</span>
        </label>
      </div>

      {/* Floating Map Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-slate-900/90 border border-slate-700/80 rounded-lg p-3 backdrop-blur-md shadow-xl text-xs pointer-events-auto">
        <h4 className="font-semibold text-slate-200 text-[11px] uppercase tracking-wider mb-2 flex items-center gap-1">
          <Compass className="w-3.5 h-3.5 text-cyan-400" /> Map Legend
        </h4>
        <div className="space-y-1.5 text-[11px]">
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 bg-emerald-400 rounded" />
            <span className="text-slate-300">Classical Baseline Route (Dijkstra)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-1 bg-cyan-400 border-dashed rounded" />
            <span className="text-slate-300">Quantum QAOA Candidate Route</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-4 h-0.5 bg-slate-600 rounded" />
            <span className="text-slate-400">Published ATS Airways (AAI AIP)</span>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-3 h-3 bg-amber-500/20 border border-amber-500 rounded-sm" />
            <span className="text-slate-400">Restricted / Prohibited Airspace</span>
          </div>
        </div>
      </div>

      <MapContainer
        center={defaultCenter}
        zoom={defaultZoom}
        scrollWheelZoom={true}
        className="w-full h-full"
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          className="dark-tiles"
        />

        {bounds.length >= 2 && <MapAutoFit bounds={bounds} />}

        {/* 1. PUBLISHED AIRWAY NETWORK LAYER */}
        {showAirways &&
          airwaysNetwork?.segments?.map((seg, idx) => (
            <Polyline
              key={`airway-${idx}-${seg.airway_id}`}
              positions={[seg.from_coords, seg.to_coords]}
              pathOptions={{
                color: '#334155',
                weight: 1.5,
                opacity: 0.6,
                dashArray: '2, 4',
              }}
            >
              <Popup>
                <div className="text-xs">
                  <div className="font-bold text-cyan-400">{seg.airway_id} Airway</div>
                  <div className="text-slate-300">
                    {seg.from_point} → {seg.to_point}
                  </div>
                  <div className="text-[11px] text-slate-400 mt-1">
                    Distance: {seg.distance_nm} NM ({seg.distance_km} km)
                  </div>
                  <div className="text-[10px] text-slate-500 mt-0.5">
                    Source: {seg.source}
                  </div>
                </div>
              </Popup>
            </Polyline>
          ))}

        {/* 2. PUBLISHED WAYPOINTS LAYER */}
        {showAirways &&
          airwaysNetwork?.waypoints &&
          Object.entries(airwaysNetwork.waypoints).map(([id, wp]) => (
            <CircleMarker
              key={`wp-${id}`}
              center={[wp.lat, wp.lon]}
              radius={2.5}
              pathOptions={{
                color: '#64748b',
                fillColor: '#94a3b8',
                fillOpacity: 0.8,
                weight: 1,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <span className="font-mono font-bold text-cyan-400">{id}</span>
                  <p className="text-slate-300 font-medium">{wp.name}</p>
                  <p className="text-[11px] text-slate-400">
                    Type: {wp.type} • {wp.lat.toFixed(2)}°, {wp.lon.toFixed(2)}°
                  </p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Source: {wp.source}</p>
                </div>
              </Popup>
            </CircleMarker>
          ))}

        {/* 3. RESTRICTED AIRSPACES LAYER */}
        {showRestricted &&
          restrictedAirspaces?.map((space) => (
            <Polygon
              key={space.identifier}
              positions={space.polygon}
              pathOptions={{
                color: space.airspace_type === 'Prohibited' ? '#ef4444' : '#f59e0b',
                fillColor: space.airspace_type === 'Prohibited' ? '#ef4444' : '#f59e0b',
                fillOpacity: 0.15,
                weight: 1.5,
              }}
            >
              <Popup>
                <div className="text-xs">
                  <div className="font-bold text-amber-400 flex items-center gap-1">
                    <ShieldAlert className="w-3.5 h-3.5" />
                    <span>{space.identifier} ({space.airspace_type})</span>
                  </div>
                  <p className="text-slate-200 mt-1 font-medium">{space.name}</p>
                  <p className="text-[11px] text-slate-400 mt-0.5">
                    Limits: {space.lower_limit} to {space.upper_limit}
                  </p>
                  <p className="text-[10px] text-slate-500 mt-0.5">Source: {space.source}</p>
                </div>
              </Popup>
            </Polygon>
          ))}

        {/* 4. CLASSICAL CANDIDATE ROUTE POLYLINE */}
        {classicalRoute?.coordinates && (
          <Polyline
            positions={classicalRoute.coordinates}
            pathOptions={{
              color: '#10b981',
              weight: 4,
              opacity: 0.85,
            }}
          >
            <Popup>
              <div className="text-xs">
                <div className="font-bold text-emerald-400">Classical Baseline Route</div>
                <div className="text-slate-200 mt-1">
                  Distance: {classicalRoute.metrics.distance_nm} NM
                </div>
                <div className="text-slate-300">
                  Est. Fuel: {classicalRoute.metrics.estimated_fuel_kg} kg
                </div>
                <div className="text-slate-300">
                  Est. CO₂: {classicalRoute.metrics.estimated_co2_kg} kg
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Computed via classical Dijkstra graph search.
                </div>
              </div>
            </Popup>
          </Polyline>
        )}

        {/* 5. QUANTUM QAOA CANDIDATE ROUTE POLYLINE */}
        {quantumRoute?.coordinates && (
          <Polyline
            positions={quantumRoute.coordinates}
            pathOptions={{
              color: '#00f2fe',
              weight: 3.5,
              opacity: 0.95,
              dashArray: '6, 6',
            }}
          >
            <Popup>
              <div className="text-xs">
                <div className="font-bold text-cyan-400">Quantum QAOA Candidate Route</div>
                <div className="text-slate-200 mt-1">
                  Distance: {quantumRoute.metrics.distance_nm} NM
                </div>
                <div className="text-slate-300">
                  Est. Fuel: {quantumRoute.metrics.estimated_fuel_kg} kg
                </div>
                <div className="text-slate-300">
                  Est. CO₂: {quantumRoute.metrics.estimated_co2_kg} kg
                </div>
                <div className="text-slate-300">
                  Status: {quantumRoute.validation_status}
                </div>
                <div className="text-[10px] text-slate-400 mt-1">
                  Bitstring: {quantumRoute.raw_bitstring || 'N/A'} • {quantumRoute.shots} shots
                </div>
              </div>
            </Popup>
          </Polyline>
        )}

        {/* 6. ORIGIN AIRPORT MARKER */}
        {origin && (
          <Marker
            position={[origin.latitude, origin.longitude]}
            icon={createAirportIcon('#38bdf8', origin.iata || 'DEP')}
          >
            <Popup>
              <div className="text-xs">
                <div className="font-bold text-cyan-400">Departure Airport</div>
                <div className="text-slate-100 font-semibold">{origin.name}</div>
                <div className="text-slate-400">
                  {origin.city}, {origin.country} ({origin.icao})
                </div>
                <div className="text-slate-400">Elevation: {origin.elevation_ft} ft</div>
              </div>
            </Popup>
          </Marker>
        )}

        {/* 7. DESTINATION AIRPORT MARKER */}
        {destination && (
          <Marker
            position={[destination.latitude, destination.longitude]}
            icon={createAirportIcon('#10b981', destination.iata || 'ARR')}
          >
            <Popup>
              <div className="text-xs">
                <div className="font-bold text-emerald-400">Destination Airport</div>
                <div className="text-slate-100 font-semibold">{destination.name}</div>
                <div className="text-slate-400">
                  {destination.city}, {destination.country} ({destination.icao})
                </div>
                <div className="text-slate-400">Elevation: {destination.elevation_ft} ft</div>
              </div>
            </Popup>
          </Marker>
        )}
      </MapContainer>
    </div>
  );
}
