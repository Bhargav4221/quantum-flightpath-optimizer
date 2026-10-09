import React from 'react';
import { BarChart3, Activity, Terminal } from 'lucide-react';

export default function QuantumCircuitStats({ backendExecution, quantumRoute }) {
  if (!backendExecution?.top_bitstrings || backendExecution.top_bitstrings.length === 0) {
    return null;
  }

  const bitstrings = backendExecution.top_bitstrings;
  const maxCounts = Math.max(...bitstrings.map((b) => b.counts));

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <BarChart3 className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Quantum Measurement Distribution & State Convergence
          </h3>
        </div>
        <div className="text-[11px] font-mono text-slate-400">
          Job ID: {backendExecution.job_id || 'local_aer_job'}
        </div>
      </div>

      {/* Bitstring Histogram */}
      <div className="space-y-2 mb-4">
        {bitstrings.slice(0, 5).map((item, idx) => {
          const widthPct = Math.max(5, (item.counts / maxCounts) * 100);
          const isSelected = item.raw_bitstring === quantumRoute?.raw_bitstring;
          return (
            <div key={idx} className="space-y-0.5">
              <div className="flex justify-between text-[11px] font-mono">
                <span className="flex items-center gap-2">
                  <span className={isSelected ? 'text-cyan-300 font-bold' : 'text-slate-300'}>
                    |{item.raw_bitstring}⟩
                  </span>
                  {isSelected && (
                    <span className="text-[9px] bg-cyan-950 text-cyan-400 border border-cyan-700 px-1 rounded">
                      Selected State
                    </span>
                  )}
                </span>
                <span className="text-slate-400">
                  {item.counts} shots ({(item.probability * 100).toFixed(1)}%) • Energy: {item.qubo_energy.toFixed(3)}
                </span>
              </div>
              <div className="w-full bg-slate-950 rounded-full h-2 overflow-hidden border border-slate-800">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${
                    isSelected ? 'bg-gradient-to-r from-cyan-500 to-cyan-300' : 'bg-slate-700'
                  }`}
                  style={{ width: `${widthPct}%` }}
                />
              </div>
            </div>
          );
        })}
      </div>

      {/* Circuit Parameters Details Bar */}
      <div className="p-2.5 bg-slate-950/70 border border-slate-800 rounded-lg grid grid-cols-2 sm:grid-cols-4 gap-2 text-[11px] font-mono">
        <div>
          <span className="text-slate-500 block">Qubits / Variables:</span>
          <span className="text-slate-200 font-bold">{backendExecution.qubit_count} Qubits</span>
        </div>
        <div>
          <span className="text-slate-500 block">Circuit Depth:</span>
          <span className="text-slate-200 font-bold">{backendExecution.circuit_depth} Gates</span>
        </div>
        <div>
          <span className="text-slate-500 block">Measurement Shots:</span>
          <span className="text-slate-200 font-bold">{backendExecution.shots} Shots</span>
        </div>
        <div>
          <span className="text-slate-500 block">Execution Latency:</span>
          <span className="text-cyan-300 font-bold">{backendExecution.execution_time_ms} ms</span>
        </div>
      </div>
    </div>
  );
}
