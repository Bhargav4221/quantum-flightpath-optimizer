import React from 'react';
import { Cloud, Fuel, Compass, Cpu, TrendingDown, TrendingUp, Minus } from 'lucide-react';

export default function MetricsCards({ classicalRoute, quantumRoute, backendExecution }) {
  if (!classicalRoute || !quantumRoute) return null;

  const c_m = classicalRoute.metrics;
  const q_m = quantumRoute.metrics;

  const co2_delta = q_m.estimated_co2_kg - c_m.estimated_co2_kg;
  const fuel_delta = q_m.estimated_fuel_kg - c_m.estimated_fuel_kg;
  const dist_delta = q_m.distance_nm - c_m.distance_nm;

  const renderBadge = (delta, unit) => {
    if (Math.abs(delta) < 0.1) {
      return (
        <span className="flex items-center gap-1 text-[11px] font-mono text-slate-400">
          <Minus className="w-3 h-3" /> 0.0 {unit}
        </span>
      );
    }
    const isSaved = delta < 0;
    return (
      <span
        className={`flex items-center gap-0.5 text-[11px] font-mono px-1.5 py-0.5 rounded ${
          isSaved ? 'bg-emerald-950 text-emerald-300' : 'bg-amber-950 text-amber-300'
        }`}
      >
        {isSaved ? <TrendingDown className="w-3 h-3" /> : <TrendingUp className="w-3 h-3" />}
        {delta > 0 ? `+${delta.toFixed(1)}` : delta.toFixed(1)} {unit}
      </span>
    );
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-3">
      {/* CO2 EMISSIONS CARD */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 text-emerald-400">
            <Cloud className="w-4 h-4" /> Est. CO₂ Emissions
          </span>
          {renderBadge(co2_delta, 'kg')}
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
          {q_m.estimated_co2_kg.toLocaleString()}{' '}
          <span className="text-xs font-normal text-slate-400 font-sans">kg CO₂</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
          <span>Classical: {c_m.estimated_co2_kg.toLocaleString()} kg</span>
          <span>Factor: 3.16 kg/kg</span>
        </div>
      </div>

      {/* FUEL CONSUMPTION CARD */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 text-amber-400">
            <Fuel className="w-4 h-4" /> Est. Fuel Burn
          </span>
          {renderBadge(fuel_delta, 'kg')}
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
          {q_m.estimated_fuel_kg.toLocaleString()}{' '}
          <span className="text-xs font-normal text-slate-400 font-sans">kg Jet-A1</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
          <span>Classical: {c_m.estimated_fuel_kg.toLocaleString()} kg</span>
          <span>Climb/Taxi incl.</span>
        </div>
      </div>

      {/* DISTANCE CARD */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 text-cyan-400">
            <Compass className="w-4 h-4" /> En-Route Distance
          </span>
          {renderBadge(dist_delta, 'NM')}
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
          {q_m.distance_nm}{' '}
          <span className="text-xs font-normal text-slate-400 font-sans">NM</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
          <span>{q_m.distance_km} km</span>
          <span>Time: {q_m.estimated_time_minutes} min</span>
        </div>
      </div>

      {/* QUANTUM HARDWARE PROFILE CARD */}
      <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3.5 shadow-lg backdrop-blur-md">
        <div className="flex items-center justify-between text-slate-400 mb-1">
          <span className="text-xs font-semibold uppercase tracking-wider flex items-center gap-1.5 text-purple-400">
            <Cpu className="w-4 h-4" /> Quantum Circuit
          </span>
          <span className="px-1.5 py-0.5 text-[9px] font-mono bg-purple-950 text-purple-300 rounded border border-purple-800">
            {backendExecution?.backend_type === 'hardware' ? 'QPU' : 'Simulator'}
          </span>
        </div>
        <div className="text-2xl font-bold font-mono text-slate-100 mt-1">
          {backendExecution?.qubit_count || 0}{' '}
          <span className="text-xs font-normal text-slate-400 font-sans">Qubits</span>
        </div>
        <div className="text-[11px] text-slate-400 mt-1 flex justify-between">
          <span>Depth: {backendExecution?.circuit_depth || 0}</span>
          <span>{backendExecution?.execution_time_ms} ms • {backendExecution?.shots} shots</span>
        </div>
      </div>
    </div>
  );
}
