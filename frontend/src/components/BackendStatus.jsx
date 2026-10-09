import React, { useState } from 'react';
import { Cpu, CheckCircle2, AlertTriangle, ShieldCheck, Zap, RefreshCw } from 'lucide-react';
import { testQuantumBackend } from '../api';

export default function BackendStatus({
  backendMode,
  setBackendMode,
  statusData,
  onRefreshStatus,
}) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  const handleTestPath = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testQuantumBackend(backendMode);
      setTestResult({
        success: true,
        message: `Circuit executed on ${res.backend_tested} (${res.execution_time_ms} ms, ${res.test_shots} shots).`,
      });
    } catch (err) {
      setTestResult({
        success: false,
        message: err.message,
      });
    } finally {
      setTesting(false);
    }
  };

  const isHardware = statusData?.backend_type === 'hardware';

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Quantum Execution Backend
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={onRefreshStatus}
            title="Refresh backend status"
            className="text-slate-400 hover:text-slate-200 transition-colors"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Backend Selection Radio Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-3">
        {/* AUTO MODE */}
        <button
          type="button"
          onClick={() => setBackendMode('auto')}
          className={`p-2.5 rounded-lg text-left border transition-all ${
            backendMode === 'auto'
              ? 'border-cyan-400 bg-cyan-950/40 text-cyan-200 ring-1 ring-cyan-400'
              : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-100">AUTO Mode</span>
            <span className="px-1.5 py-0.5 text-[9px] font-mono bg-cyan-900/50 text-cyan-300 rounded">
              Recommended
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Checks IBM Quantum hardware first; transparently falls back to local Aer simulator if credentials absent.
          </p>
        </button>

        {/* IBM QUANTUM HARDWARE */}
        <button
          type="button"
          onClick={() => setBackendMode('ibm')}
          className={`p-2.5 rounded-lg text-left border transition-all ${
            backendMode === 'ibm'
              ? 'border-cyan-400 bg-cyan-950/40 text-cyan-200 ring-1 ring-cyan-400'
              : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-100">IBM Quantum</span>
            <span
              className={`px-1.5 py-0.5 text-[9px] font-mono rounded ${
                statusData?.ibm_available
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              {statusData?.ibm_available ? 'Connected' : 'Token Required'}
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Direct QPU hardware execution via Qiskit Runtime. Strict error if token is unconfigured (no silent fallback).
          </p>
        </button>

        {/* LOCAL QISKIT AER */}
        <button
          type="button"
          onClick={() => setBackendMode('aer')}
          className={`p-2.5 rounded-lg text-left border transition-all ${
            backendMode === 'aer'
              ? 'border-cyan-400 bg-cyan-950/40 text-cyan-200 ring-1 ring-cyan-400'
              : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-100">Qiskit Aer Simulator</span>
            <span className="px-1.5 py-0.5 text-[9px] font-mono bg-emerald-950 text-emerald-400 border border-emerald-800 rounded">
              Ready
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Genuine local quantum circuit simulation using Qiskit Aer statevector & noise models.
          </p>
        </button>
      </div>

      {/* Active Backend Status Banner */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between p-2.5 bg-slate-950/80 rounded-lg border border-slate-800/80 gap-2">
        <div className="flex items-center gap-2">
          {isHardware ? (
            <Zap className="w-4 h-4 text-cyan-400 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0" />
          )}
          <div>
            <div className="text-xs font-medium text-slate-200 flex items-center gap-2">
              <span>Active Target:</span>
              <span className="text-cyan-300 font-mono font-bold">
                {statusData?.active_backend_name || 'Detecting backend...'}
              </span>
            </div>
            <p className="text-[10px] text-slate-400">
              {statusData?.message || 'Server environment ready.'}
            </p>
          </div>
        </div>

        <button
          type="button"
          disabled={testing}
          onClick={handleTestPath}
          className="px-3 py-1 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-slate-200 rounded text-xs font-medium transition-colors shrink-0 disabled:opacity-50"
        >
          {testing ? 'Verifying Path...' : 'Test Quantum Execution'}
        </button>
      </div>

      {/* Test Result Feedback */}
      {testResult && (
        <div
          className={`mt-2 p-2 rounded text-xs flex items-center gap-2 ${
            testResult.success
              ? 'bg-emerald-950/40 text-emerald-300 border border-emerald-800'
              : 'bg-rose-950/40 text-rose-300 border border-rose-800'
          }`}
        >
          {testResult.success ? (
            <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
          ) : (
            <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
          )}
          <span>{testResult.message}</span>
        </div>
      )}
    </div>
  );
}
