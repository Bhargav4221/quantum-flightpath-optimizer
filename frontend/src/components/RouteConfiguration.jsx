import React, { useState } from 'react';
import { Sliders, Compass, Fuel, Cloud, Clock, ShieldAlert, Cpu } from 'lucide-react';

const OBJECTIVE_PRESETS = [
  {
    id: 'balanced',
    label: 'Balanced Optimization',
    desc: 'Multi-objective composite (Distance 20%, Fuel 25%, CO2 30%, Time 15%, Congestion 10%)',
    weights: { distance: 20, fuel: 25, co2: 30, time: 15, congestion: 10 },
  },
  {
    id: 'distance',
    label: 'Minimum Distance',
    desc: 'Prioritizes shortest nautical mileage along published airways',
    weights: { distance: 80, fuel: 5, co2: 5, time: 5, congestion: 5 },
  },
  {
    id: 'fuel',
    label: 'Minimum Fuel Burn',
    desc: 'Optimizes fuel efficiency and throttle profiles',
    weights: { distance: 10, fuel: 70, co2: 10, time: 5, congestion: 5 },
  },
  {
    id: 'co2',
    label: 'Minimum CO₂ Emissions',
    desc: 'Minimizes carbon footprint using ICAO turbofan emissions factors',
    weights: { distance: 5, fuel: 20, co2: 65, time: 5, congestion: 5 },
  },
  {
    id: 'time',
    label: 'Minimum Flight Time',
    desc: 'Minimizes block time accounting for en-route cruising speeds',
    weights: { distance: 10, fuel: 5, co2: 5, time: 75, congestion: 5 },
  },
  {
    id: 'congestion',
    label: 'Minimum Congestion',
    desc: 'Avoids high-density airway corridors and bottleneck fixes',
    weights: { distance: 10, fuel: 5, co2: 5, time: 10, congestion: 70 },
  },
];

export default function RouteConfiguration({
  objective,
  setObjective,
  weights,
  setWeights,
  aircraftType,
  setAircraftType,
  shots,
  setShots,
}) {
  const [showCustomWeights, setShowCustomWeights] = useState(false);

  const handlePresetSelect = (preset) => {
    setObjective(preset.id);
    setWeights(preset.weights);
  };

  const handleWeightChange = (key, val) => {
    const num = Math.max(0, Math.min(100, parseInt(val) || 0));
    setWeights((prev) => ({ ...prev, [key]: num }));
  };

  const totalWeights =
    weights.distance + weights.fuel + weights.co2 + weights.time + weights.congestion;
  const isWeightValid = totalWeights === 100;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Sliders className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Optimization Objective & Weights
          </h3>
        </div>
        <button
          type="button"
          onClick={() => setShowCustomWeights(!showCustomWeights)}
          className="text-[11px] text-cyan-400 hover:text-cyan-300 font-mono underline"
        >
          {showCustomWeights ? 'Hide Custom Sliders' : 'Customize Weight Distribution'}
        </button>
      </div>

      {/* Preset Objective Chips */}
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 mb-3">
        {OBJECTIVE_PRESETS.map((p) => {
          const isActive = objective === p.id;
          return (
            <button
              key={p.id}
              type="button"
              onClick={() => handlePresetSelect(p)}
              className={`p-2 rounded-lg text-left border transition-all ${
                isActive
                  ? 'border-cyan-400 bg-cyan-950/40 text-cyan-200 shadow-sm shadow-cyan-500/20'
                  : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700 hover:text-slate-300'
              }`}
            >
              <div className="text-xs font-semibold">{p.label}</div>
              <div className="text-[10px] text-slate-500 line-clamp-1 mt-0.5">{p.desc}</div>
            </button>
          );
        })}
      </div>

      {/* Custom Weights Sliders */}
      {showCustomWeights && (
        <div className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg mb-3">
          <div className="flex items-center justify-between text-xs mb-2">
            <span className="text-slate-300 font-medium">Multi-Objective Weight Sliders</span>
            <span
              className={`font-mono font-bold text-xs ${
                isWeightValid ? 'text-emerald-400' : 'text-amber-400'
              }`}
            >
              Total: {totalWeights}% {isWeightValid ? '✓' : '(Must sum to 100%)'}
            </span>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-5 gap-3">
            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span className="flex items-center gap-1"><Compass className="w-3 h-3 text-cyan-400" /> Distance</span>
                <span className="font-mono text-cyan-300">{weights.distance}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.distance}
                onChange={(e) => handleWeightChange('distance', e.target.value)}
                className="w-full accent-cyan-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span className="flex items-center gap-1"><Fuel className="w-3 h-3 text-amber-400" /> Fuel</span>
                <span className="font-mono text-amber-300">{weights.fuel}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.fuel}
                onChange={(e) => handleWeightChange('fuel', e.target.value)}
                className="w-full accent-amber-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span className="flex items-center gap-1"><Cloud className="w-3 h-3 text-emerald-400" /> CO₂</span>
                <span className="font-mono text-emerald-300">{weights.co2}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.co2}
                onChange={(e) => handleWeightChange('co2', e.target.value)}
                className="w-full accent-emerald-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span className="flex items-center gap-1"><Clock className="w-3 h-3 text-purple-400" /> Time</span>
                <span className="font-mono text-purple-300">{weights.time}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.time}
                onChange={(e) => handleWeightChange('time', e.target.value)}
                className="w-full accent-purple-400 h-1 bg-slate-800 rounded"
              />
            </div>

            <div>
              <div className="flex justify-between text-[11px] text-slate-400 mb-1">
                <span className="flex items-center gap-1"><ShieldAlert className="w-3 h-3 text-rose-400" /> Traffic</span>
                <span className="font-mono text-rose-300">{weights.congestion}%</span>
              </div>
              <input
                type="range"
                min="0"
                max="100"
                value={weights.congestion}
                onChange={(e) => handleWeightChange('congestion', e.target.value)}
                className="w-full accent-rose-400 h-1 bg-slate-800 rounded"
              />
            </div>
          </div>
        </div>
      )}

      {/* Aircraft and Quantum Shots selectors */}
      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-1">
        <div>
          <label className="block text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">
            Aircraft Aerodynamic Profile
          </label>
          <select
            value={aircraftType}
            onChange={(e) => setAircraftType(e.target.value)}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-400"
          >
            <option value="A320neo">Airbus A320neo (CFM LEAP-1A • Narrowbody)</option>
            <option value="B738">Boeing 737-800 (CFM56-7B • Narrowbody)</option>
            <option value="B789">Boeing 787-9 Dreamliner (GEnx-1B • Widebody)</option>
          </select>
        </div>

        <div>
          <label className="block text-[11px] font-medium text-slate-400 uppercase tracking-wider mb-1">
            Quantum Sampling Shots
          </label>
          <select
            value={shots}
            onChange={(e) => setShots(parseInt(e.target.value))}
            className="w-full bg-slate-950 border border-slate-800 rounded-lg p-2 text-xs text-slate-200 font-mono focus:outline-none focus:border-cyan-400"
          >
            <option value={512}>512 Shots</option>
            <option value={1024}>1024 Shots (Standard)</option>
            <option value={2048}>2048 Shots (High Precision)</option>
          </select>
        </div>
      </div>
    </div>
  );
}
