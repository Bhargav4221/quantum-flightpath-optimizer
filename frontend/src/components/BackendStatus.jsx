import React, { useState } from 'react';
import {
  Cpu,
  CheckCircle2,
  AlertTriangle,
  Zap,
  RefreshCw,
  Key,
  ExternalLink,
  Lock,
} from 'lucide-react';
import { testQuantumBackend, configureIBMToken } from '../api';

export default function BackendStatus({
  backendMode,
  setBackendMode,
  statusData,
  onRefreshStatus,
}) {
  const [testing, setTesting] = useState(false);
  const [testResult, setTestResult] = useState(null);

  // IBM Token Configuration Form state
  const [showTokenModal, setShowTokenModal] = useState(false);
  const [tokenInput, setTokenInput] = useState('');
  const [instanceInput, setInstanceInput] = useState('');
  const [savingToken, setSavingToken] = useState(false);
  const [tokenFeedback, setTokenFeedback] = useState(null);

  const handleTestPath = async () => {
    setTesting(true);
    setTestResult(null);
    try {
      const res = await testQuantumBackend(backendMode);
      setTestResult({
        success: true,
        message: `Circuit successfully executed on ${res.backend_tested} (${res.execution_time_ms} ms, ${res.test_shots} shots).`,
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

  const handleSaveToken = async (e) => {
    e.preventDefault();
    if (!tokenInput.trim()) {
      setTokenFeedback({ success: false, message: 'Please enter a valid IBM Quantum API Token.' });
      return;
    }

    setSavingToken(true);
    setTokenFeedback(null);
    try {
      const res = await configureIBMToken(tokenInput.trim(), instanceInput.trim() || null);
      setTokenFeedback({
        success: true,
        message: res.message || 'Authenticated successfully with IBM Quantum hardware!',
      });
      setTokenInput('');
      setInstanceInput('');
      // Switch active mode to IBM Quantum hardware
      setBackendMode('ibm');
      // Refresh status from server
      await onRefreshStatus();
      setTimeout(() => setShowTokenModal(false), 2500);
    } catch (err) {
      setTokenFeedback({
        success: false,
        message: err.message || 'Failed to authenticate with IBM Quantum.',
      });
    } finally {
      setSavingToken(false);
    }
  };

  const isHardware = statusData?.backend_type === 'hardware';
  const hasIBMToken = statusData?.configured_token_present || statusData?.ibm_available;

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      {/* HEADER */}
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Zap className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            IBM Quantum Hardware & Execution Backend
          </h3>
        </div>
        <div className="flex items-center gap-2">
          <button
            type="button"
            onClick={() => setShowTokenModal(!showTokenModal)}
            className={`text-xs px-2.5 py-1 rounded flex items-center gap-1 font-medium transition-colors ${
              hasIBMToken
                ? 'bg-emerald-950 text-emerald-300 border border-emerald-800 hover:bg-emerald-900'
                : 'bg-cyan-950 text-cyan-300 border border-cyan-800 hover:bg-cyan-900 ring-1 ring-cyan-500'
            }`}
          >
            <Key className="w-3 h-3" />
            <span>{hasIBMToken ? 'IBM Token Configured' : 'Configure IBM Token'}</span>
          </button>
          <button
            type="button"
            onClick={onRefreshStatus}
            title="Refresh backend status"
            className="text-slate-400 hover:text-slate-200 transition-colors p-1"
          >
            <RefreshCw className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* TOKEN CONFIGURATION PANEL */}
      {showTokenModal && (
        <form
          onSubmit={handleSaveToken}
          className="mb-3 p-3 bg-slate-950 border border-cyan-800/80 rounded-lg shadow-inner space-y-2.5 animate-fade-in"
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-cyan-300 flex items-center gap-1.5">
              <Key className="w-3.5 h-3.5 text-cyan-400" /> Add Your IBM Quantum API Token
            </span>
            <a
              href="https://quantum.ibm.com/"
              target="_blank"
              rel="noreferrer"
              className="text-[11px] text-cyan-400 hover:text-cyan-300 flex items-center gap-1 underline font-mono"
            >
              Get Token at quantum.ibm.com <ExternalLink className="w-3 h-3" />
            </a>
          </div>

          <p className="text-[11px] text-slate-400 leading-snug">
            Paste your IBM Quantum token below to enable genuine quantum execution on IBM QPUs via
            Qiskit Runtime. Your token is stored securely on the server and verified immediately.
          </p>

          <div>
            <label className="block text-[10px] font-mono text-slate-400 mb-1">
              IBM_QUANTUM_TOKEN *
            </label>
            <input
              type="password"
              placeholder="Paste your IBM Quantum API token here..."
              value={tokenInput}
              onChange={(e) => setTokenInput(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 font-mono placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div>
            <label className="block text-[10px] font-mono text-slate-400 mb-1">
              IBM_QUANTUM_INSTANCE (Optional CRN / Hub-Group-Project)
            </label>
            <input
              type="text"
              placeholder="Leave blank for standard open instance..."
              value={instanceInput}
              onChange={(e) => setInstanceInput(e.target.value)}
              className="w-full bg-slate-900 border border-slate-700 rounded px-2.5 py-1.5 text-xs text-slate-100 font-mono placeholder-slate-600 focus:outline-none focus:border-cyan-400"
            />
          </div>

          <div className="flex items-center justify-between pt-1">
            <button
              type="button"
              onClick={() => setShowTokenModal(false)}
              className="text-xs text-slate-400 hover:text-slate-300"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={savingToken}
              className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-bold text-xs rounded transition-colors disabled:opacity-50"
            >
              {savingToken ? 'Authenticating with IBM...' : 'Connect to IBM Quantum'}
            </button>
          </div>

          {tokenFeedback && (
            <div
              className={`p-2 rounded text-xs flex items-center gap-2 mt-2 ${
                tokenFeedback.success
                  ? 'bg-emerald-950/60 text-emerald-300 border border-emerald-800'
                  : 'bg-rose-950/60 text-rose-300 border border-rose-800'
              }`}
            >
              {tokenFeedback.success ? (
                <CheckCircle2 className="w-3.5 h-3.5 shrink-0" />
              ) : (
                <AlertTriangle className="w-3.5 h-3.5 shrink-0" />
              )}
              <span>{tokenFeedback.message}</span>
            </div>
          )}
        </form>
      )}

      {/* Backend Selection Radio Tiles */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-2 mb-3">
        {/* IBM QUANTUM HARDWARE (PRIMARY FOCUS) */}
        <button
          type="button"
          onClick={() => setBackendMode('ibm')}
          className={`p-2.5 rounded-lg text-left border transition-all ${
            backendMode === 'ibm'
              ? 'border-cyan-400 bg-cyan-950/50 text-cyan-200 ring-2 ring-cyan-400 shadow-md shadow-cyan-500/20'
              : 'border-slate-800 bg-slate-950/60 text-slate-400 hover:border-slate-700'
          }`}
        >
          <div className="flex items-center justify-between">
            <span className="text-xs font-bold text-slate-100 flex items-center gap-1">
              <Zap className="w-3.5 h-3.5 text-cyan-400" /> IBM Quantum QPU
            </span>
            <span
              className={`px-1.5 py-0.5 text-[9px] font-mono rounded font-semibold ${
                statusData?.ibm_available
                  ? 'bg-emerald-950 text-emerald-400 border border-emerald-800'
                  : 'bg-amber-950 text-amber-400 border border-amber-800'
              }`}
            >
              {statusData?.ibm_available ? 'Connected' : 'Token Required'}
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Direct circuit execution on real IBM Quantum superconducting QPUs via Qiskit Runtime.
          </p>
        </button>

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
              Adaptive
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Uses IBM Quantum hardware if connected; gracefully uses local Aer simulator if offline.
          </p>
        </button>

        {/* LOCAL QISKIT AER SIMULATOR */}
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
            <span className="text-xs font-bold text-slate-100">Qiskit Aer (Local)</span>
            <span className="px-1.5 py-0.5 text-[9px] font-mono bg-slate-800 text-slate-300 rounded">
              Simulation
            </span>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 leading-snug">
            Local statevector simulation runner for testing circuits offline.
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
