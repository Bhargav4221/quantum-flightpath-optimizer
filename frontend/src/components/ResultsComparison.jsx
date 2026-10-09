import React from 'react';
import { GitCompare, CheckCircle2, AlertTriangle, Cpu, ArrowUpRight, ArrowDownRight, Minus } from 'lucide-react';

export default function ResultsComparison({
  classicalRoute,
  quantumRoute,
  metricsComparison,
  backendExecution,
}) {
  if (!classicalRoute || !quantumRoute) return null;

  const c_m = classicalRoute.metrics;
  const q_m = quantumRoute.metrics;
  const comp = metricsComparison;

  const renderDelta = (delta, deltaPct, isLowerBetter = true) => {
    if (Math.abs(delta) < 0.05) {
      return (
        <span className="flex items-center gap-1 text-slate-400 font-mono text-xs">
          <Minus className="w-3 h-3" /> Parity (0.0%)
        </span>
      );
    }
    const isImprovement = isLowerBetter ? delta < 0 : delta > 0;
    const color = isImprovement ? 'text-emerald-400' : 'text-amber-400';
    const Icon = delta > 0 ? ArrowUpRight : ArrowDownRight;

    return (
      <span className={`flex items-center gap-0.5 font-mono text-xs ${color}`}>
        <Icon className="w-3.5 h-3.5" />
        {delta > 0 ? `+${delta}` : delta} ({deltaPct > 0 ? `+${deltaPct}%` : `${deltaPct}%`})
      </span>
    );
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <GitCompare className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Scientific Comparison: Classical Baseline vs Quantum Candidate
          </h3>
        </div>
        <span
          className={`px-2 py-0.5 text-[10px] font-mono rounded border ${
            quantumRoute.is_valid
              ? 'bg-emerald-950/60 text-emerald-400 border-emerald-800'
              : 'bg-amber-950/60 text-amber-400 border-amber-800'
          }`}
        >
          {quantumRoute.validation_status}
        </span>
      </div>

      {/* Comparison Table */}
      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs">
          <thead>
            <tr className="border-b border-slate-800 text-slate-400">
              <th className="py-2 font-medium">Evaluated Route Metric</th>
              <th className="py-2 font-medium text-emerald-400">Classical Baseline (Dijkstra)</th>
              <th className="py-2 font-medium text-cyan-400">Quantum QAOA Candidate</th>
              <th className="py-2 font-medium">Variance (Delta)</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800/60 font-mono text-slate-200">
            <tr>
              <td className="py-2 text-slate-400 font-sans">Multi-Objective Cost</td>
              <td className="py-2 text-emerald-300 font-bold">{c_m.objective_value.toFixed(4)}</td>
              <td className="py-2 text-cyan-300 font-bold">{q_m.objective_value.toFixed(4)}</td>
              <td className="py-2">
                {renderDelta(comp?.objective_delta, ((comp?.objective_delta / c_m.objective_value) * 100).toFixed(1))}
              </td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">En-Route Distance</td>
              <td className="py-2">{c_m.distance_nm} NM ({c_m.distance_km} km)</td>
              <td className="py-2">{q_m.distance_nm} NM ({q_m.distance_km} km)</td>
              <td className="py-2">{renderDelta(comp?.distance_delta_nm, comp?.distance_delta_pct)}</td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">Estimated Fuel Burn</td>
              <td className="py-2">{c_m.estimated_fuel_kg.toLocaleString()} kg</td>
              <td className="py-2">{q_m.estimated_fuel_kg.toLocaleString()} kg</td>
              <td className="py-2">{renderDelta(comp?.fuel_delta_kg, comp?.fuel_delta_pct)}</td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">Estimated CO₂ Emissions</td>
              <td className="py-2">{c_m.estimated_co2_kg.toLocaleString()} kg</td>
              <td className="py-2">{q_m.estimated_co2_kg.toLocaleString()} kg</td>
              <td className="py-2">{renderDelta(comp?.co2_delta_kg, comp?.co2_delta_pct)}</td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">Estimated Flight Time</td>
              <td className="py-2">{c_m.estimated_time_minutes} min</td>
              <td className="py-2">{q_m.estimated_time_minutes} min</td>
              <td className="py-2">{renderDelta(comp?.time_delta_min, comp?.time_delta_pct)}</td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">Avg Airway Congestion</td>
              <td className="py-2">{(c_m.congestion_score * 100).toFixed(1)}%</td>
              <td className="py-2">{(q_m.congestion_score * 100).toFixed(1)}%</td>
              <td className="py-2 text-slate-400">
                {((q_m.congestion_score - c_m.congestion_score) * 100).toFixed(1)}%
              </td>
            </tr>

            <tr>
              <td className="py-2 text-slate-400 font-sans">Route Feasibility</td>
              <td className="py-2 text-emerald-400">Strictly Feasible</td>
              <td className="py-2">
                {quantumRoute.is_valid ? (
                  <span className="text-emerald-400 flex items-center gap-1">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Strictly Feasible
                  </span>
                ) : (
                  <span className="text-amber-400 flex items-center gap-1">
                    <AlertTriangle className="w-3.5 h-3.5" /> Classically Repaired
                  </span>
                )}
              </td>
              <td className="py-2 text-slate-400 text-[11px] font-sans">
                {quantumRoute.post_processing_applied ? 'Post-processed' : 'Direct quantum solution'}
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      {/* Summary scientific verdict banner */}
      <div className="mt-3 p-2.5 bg-slate-950/70 border border-slate-800 rounded-lg flex items-center justify-between text-xs">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400 shrink-0" />
          <span className="text-slate-300 font-medium">Evaluation Finding:</span>
          <span className="text-cyan-200">{comp?.summary_verdict}</span>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Target: {backendExecution?.active_backend}
        </div>
      </div>
    </div>
  );
}
