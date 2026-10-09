import React, { useState } from 'react';
import { Navigation, MapPin } from 'lucide-react';

export default function RouteDetails({ classicalRoute, quantumRoute }) {
  const [selectedRouteType, setSelectedRouteType] = useState('quantum');

  const activeRoute = selectedRouteType === 'quantum' ? quantumRoute : classicalRoute;
  if (!activeRoute?.waypoints) return null;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Navigation className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Waypoint Navigation Log & Airway Sequence
          </h3>
        </div>

        {/* Toggle between Classical and Quantum Route Log */}
        <div className="flex rounded-lg border border-slate-800 p-0.5 bg-slate-950 text-xs">
          <button
            type="button"
            onClick={() => setSelectedRouteType('quantum')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              selectedRouteType === 'quantum'
                ? 'bg-cyan-950 text-cyan-300 font-semibold border border-cyan-800'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Quantum Route ({quantumRoute?.waypoints?.length || 0} fixes)
          </button>
          <button
            type="button"
            onClick={() => setSelectedRouteType('classical')}
            className={`px-2.5 py-1 rounded-md font-medium transition-colors ${
              selectedRouteType === 'classical'
                ? 'bg-emerald-950 text-emerald-300 font-semibold border border-emerald-800'
                : 'text-slate-400 hover:text-slate-200'
            }`}
          >
            Classical Route ({classicalRoute?.waypoints?.length || 0} fixes)
          </button>
        </div>
      </div>

      {/* Airway Sequence Tag Chain */}
      <div className="flex flex-wrap items-center gap-1.5 mb-3 p-2 bg-slate-950/70 rounded-lg border border-slate-800/80">
        <span className="text-[11px] font-semibold text-slate-400">Airway Chain:</span>
        {activeRoute.airway_segments?.map((seg, idx) => (
          <span
            key={idx}
            className="px-2 py-0.5 bg-slate-800 text-cyan-300 rounded font-mono text-[11px] border border-slate-700"
          >
            {seg}
          </span>
        ))}
      </div>

      {/* Navigation Waypoints Table */}
      <div className="overflow-x-auto max-h-60 overflow-y-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400 sticky top-0 bg-slate-900">
              <th className="py-2 px-2 font-medium">Seq</th>
              <th className="py-2 px-2 font-medium">Fix / Navaid</th>
              <th className="py-2 px-2 font-medium">Name</th>
              <th className="py-2 px-2 font-medium">Coordinates</th>
              <th className="py-2 px-2 font-medium">Type</th>
              <th className="py-2 px-2 font-medium">Source</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-slate-200">
            {activeRoute.waypoints.map((wp, i) => (
              <tr key={i} className="hover:bg-slate-800/40">
                <td className="py-2 px-2 text-slate-400">{wp.sequence}</td>
                <td className="py-2 px-2 font-bold text-cyan-400">{wp.identifier}</td>
                <td className="py-2 px-2 font-sans text-slate-300">{wp.name}</td>
                <td className="py-2 px-2 text-slate-400 text-[11px]">
                  {wp.latitude.toFixed(3)}°, {wp.longitude.toFixed(3)}°
                </td>
                <td className="py-2 px-2">
                  <span className="px-1.5 py-0.5 bg-slate-800 text-slate-300 rounded text-[10px]">
                    {wp.node_type}
                  </span>
                </td>
                <td className="py-2 px-2 text-[10px] text-slate-500 font-sans">{wp.source}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
