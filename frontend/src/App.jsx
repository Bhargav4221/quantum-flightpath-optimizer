import React, { useState, useEffect } from 'react';
import {
  Compass,
  Cpu,
  Plane,
  AlertCircle,
  Play,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  ExternalLink,
} from 'lucide-react';

import AirportSelector from './components/AirportSelector';
import RouteConfiguration from './components/RouteConfiguration';
import BackendStatus from './components/BackendStatus';
import MapView from './components/MapView';
import ResultsComparison from './components/ResultsComparison';
import MetricsCards from './components/MetricsCards';
import QuantumCircuitStats from './components/QuantumCircuitStats';
import RouteDetails from './components/RouteDetails';
import RouteWarnings from './components/RouteWarnings';
import DataProvenance from './components/DataProvenance';

import {
  getAirport,
  getBackendStatus,
  getDataProvenance,
  getAirwaysNetwork,
  getRestrictedAirspaces,
  optimizeRoute,
} from './api';

export default function App() {
  // Airport state (defaults to Delhi VIDP and Hyderabad VOHS)
  const [origin, setOrigin] = useState(null);
  const [destination, setDestination] = useState(null);

  // Optimization settings
  const [objective, setObjective] = useState('balanced');
  const [weights, setWeights] = useState({
    distance: 20,
    fuel: 25,
    co2: 30,
    time: 15,
    congestion: 10,
  });
  const [aircraftType, setAircraftType] = useState('A320neo');
  const [backendMode, setBackendMode] = useState('auto');
  const [shots, setShots] = useState(1024);

  // Data & execution state
  const [backendStatus, setBackendStatus] = useState(null);
  const [dataProvenances, setDataProvenances] = useState([]);
  const [airwaysNetwork, setAirwaysNetwork] = useState(null);
  const [restrictedAirspaces, setRestrictedAirspaces] = useState([]);

  // Result state
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState(null);
  const [optimizationResult, setOptimizationResult] = useState(null);

  // Initialize data on mount
  useEffect(() => {
    const initApp = async () => {
      try {
        const [delhiApt, hydApt, bStatus, provs, airways, restricted] = await Promise.all([
          getAirport('DEL'),
          getAirport('HYD'),
          getBackendStatus(),
          getDataProvenance(),
          getAirwaysNetwork(),
          getRestrictedAirspaces(),
        ]);

        setOrigin(delhiApt);
        setDestination(hydApt);
        setBackendStatus(bStatus);
        setDataProvenances(provs);
        setAirwaysNetwork(airways);
        setRestrictedAirspaces(restricted);
      } catch (err) {
        console.error('Initialization error:', err);
      }
    };
    initApp();
  }, []);

  const handleRefreshStatus = async () => {
    try {
      const bStatus = await getBackendStatus();
      setBackendStatus(bStatus);
    } catch (err) {
      console.error(err);
    }
  };

  const handleOptimize = async () => {
    if (!origin || !destination) {
      setErrorMessage('Please select both departure and destination airports.');
      return;
    }

    if (origin.icao === destination.icao) {
      setErrorMessage('Departure and destination airports cannot be identical.');
      return;
    }

    const totalWeight =
      weights.distance + weights.fuel + weights.co2 + weights.time + weights.congestion;
    if (totalWeight !== 100) {
      setErrorMessage(`Weights must sum to 100%. Current sum is ${totalWeight}%.`);
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    try {
      const payload = {
        origin: origin.icao,
        destination: destination.icao,
        objective,
        weights: {
          distance: weights.distance / 100.0,
          fuel: weights.fuel / 100.0,
          co2: weights.co2 / 100.0,
          time: weights.time / 100.0,
          congestion: weights.congestion / 100.0,
        },
        aircraft_type: aircraftType,
        backend: backendMode,
        shots,
      };

      const result = await optimizeRoute(payload);
      setOptimizationResult(result);
    } catch (err) {
      setErrorMessage(err.message || 'Route optimization failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080d1a] text-slate-100 flex flex-col font-sans">
      {/* TOP AVIONICS NAVIGATION BAR */}
      <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur-md sticky top-0 z-50 px-4 py-3">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row sm:items-center justify-between gap-3">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-cyan-400 p-0.5 flex items-center justify-center shadow-lg shadow-cyan-500/20">
              <div className="w-full h-full bg-[#080d1a] rounded-[7px] flex items-center justify-center">
                <Compass className="w-5 h-5 text-cyan-400 animate-spin-slow" />
              </div>
            </div>
            <div>
              <div className="flex items-center gap-2">
                <h1 className="text-base font-bold tracking-wider text-white">
                  QUANTUM FLIGHTPATH OPTIMIZER
                </h1>
                <span className="px-1.5 py-0.5 text-[9px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-700 rounded font-semibold">
                  QISKIT 2.5
                </span>
              </div>
              <p className="text-xs text-slate-400">
                Quantum-Assisted Aviation Route and Emissions Optimization
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <div className="flex items-center gap-2 px-3 py-1 bg-slate-900 border border-slate-800 rounded-lg text-xs font-mono">
              <span className="w-2 h-2 rounded-full bg-emerald-400 animate-pulse" />
              <span className="text-slate-300">
                {backendStatus?.active_backend_name || 'Qiskit Aer Ready'}
              </span>
            </div>
            <a
              href="/docs"
              target="_blank"
              rel="noreferrer"
              className="text-xs text-slate-400 hover:text-cyan-400 flex items-center gap-1 transition-colors"
            >
              API Docs <ExternalLink className="w-3 h-3" />
            </a>
          </div>
        </div>
      </header>

      {/* REGULATORY DISCLAIMER STRIP */}
      <div className="bg-amber-950/40 border-b border-amber-900/60 px-4 py-2">
        <div className="max-w-7xl mx-auto flex items-center gap-2 text-[11px] text-amber-300/90 font-medium">
          <ShieldAlert className="w-3.5 h-3.5 text-amber-400 shrink-0" />
          <span>
            Research & Decision-Support System: Outputs do not constitute ATC clearances or certified operational flight plans.
          </span>
        </div>
      </div>

      {/* MAIN COCKPIT WORKSPACE */}
      <main className="max-w-7xl mx-auto w-full px-4 py-6 flex-1 space-y-6">
        {/* TOP CONTROLS GRID */}
        <section className="space-y-4">
          {/* Airport Selectors */}
          <AirportSelector
            origin={origin}
            destination={destination}
            onSelectOrigin={setOrigin}
            onSelectDestination={setDestination}
          />

          {/* Configuration and Quantum Backend */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
            <RouteConfiguration
              objective={objective}
              setObjective={setObjective}
              weights={weights}
              setWeights={setWeights}
              aircraftType={aircraftType}
              setAircraftType={setAircraftType}
              shots={shots}
              setShots={setShots}
            />

            <BackendStatus
              backendMode={backendMode}
              setBackendMode={setBackendMode}
              statusData={backendStatus}
              onRefreshStatus={handleRefreshStatus}
            />
          </div>

          {/* Error Banner */}
          {errorMessage && (
            <div className="p-3 bg-rose-950/60 border border-rose-800 rounded-xl text-xs text-rose-200 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
          )}

          {/* Optimize Route Execution Button */}
          <div className="flex justify-end">
            <button
              type="button"
              disabled={loading}
              onClick={handleOptimize}
              className="w-full sm:w-auto px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-slate-950 font-bold rounded-xl shadow-lg shadow-cyan-500/25 flex items-center justify-center gap-2 text-sm transition-all transform active:scale-95 disabled:opacity-50"
            >
              {loading ? (
                <>
                  <Sparkles className="w-4 h-4 animate-spin" />
                  <span>Formulating QUBO & Executing QAOA...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4 fill-current" />
                  <span>OPTIMIZE ROUTE (Classical & Quantum)</span>
                </>
              )}
            </button>
          </div>
        </section>

        {/* INTERACTIVE GEOGRAPHIC MAP */}
        <section className="space-y-2">
          <div className="flex items-center justify-between text-xs text-slate-400">
            <span className="font-semibold uppercase tracking-wider text-slate-300">
              Interactive Aeronautical Map (OpenStreetMap & AAI Published Airway Network)
            </span>
            <span>
              {origin && destination
                ? `${origin.iata || origin.icao} ➔ ${destination.iata || destination.icao}`
                : 'Select route'}
            </span>
          </div>

          <MapView
            origin={origin}
            destination={destination}
            classicalRoute={optimizationResult?.classical_route}
            quantumRoute={optimizationResult?.quantum_route}
            airwaysNetwork={airwaysNetwork}
            restrictedAirspaces={restrictedAirspaces}
          />
        </section>

        {/* RESULTS & SCIENTIFIC COMPARISON (WHEN OPTIMIZED) */}
        {optimizationResult && (
          <section className="space-y-6 pt-2 animate-fade-in">
            {/* High-level Delta Metrics */}
            <MetricsCards
              classicalRoute={optimizationResult.classical_route}
              quantumRoute={optimizationResult.quantum_route}
              backendExecution={optimizationResult.backend_execution}
            />

            {/* Scientific Side-by-Side Comparison Table */}
            <ResultsComparison
              classicalRoute={optimizationResult.classical_route}
              quantumRoute={optimizationResult.quantum_route}
              metricsComparison={optimizationResult.metrics_comparison}
              backendExecution={optimizationResult.backend_execution}
            />

            {/* Quantum Circuit Execution Statistics & Histogram */}
            <QuantumCircuitStats
              backendExecution={optimizationResult.backend_execution}
              quantumRoute={optimizationResult.quantum_route}
            />

            {/* Waypoint-by-Waypoint Navigation Log */}
            <RouteDetails
              classicalRoute={optimizationResult.classical_route}
              quantumRoute={optimizationResult.quantum_route}
            />

            {/* Validation Notes & Regulatory Disclaimers */}
            <RouteWarnings
              disclaimer={optimizationResult.disclaimer}
              quantumRoute={optimizationResult.quantum_route}
              classicalRoute={optimizationResult.classical_route}
            />
          </section>
        )}

        {/* AUTHORITATIVE DATA PROVENANCE REGISTRY */}
        <section className="pt-4">
          <DataProvenance provenances={dataProvenances} />
        </section>
      </main>

      {/* FOOTER */}
      <footer className="border-t border-slate-800 bg-slate-950/80 px-4 py-4 text-xs text-slate-500 mt-auto">
        <div className="max-w-7xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-2 text-center sm:text-left">
          <p>
            Quantum FlightPath Optimizer • Research Decision-Support System
          </p>
          <p className="font-mono text-[11px]">
            Powered by Qiskit & Qiskit Aer • Published ATS Airway Network
          </p>
        </div>
      </footer>
    </div>
  );
}
