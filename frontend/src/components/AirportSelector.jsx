import React, { useState, useEffect, useRef } from 'react';
import { PlaneTakeoff, PlaneLanding, Search, CheckCircle2, AlertCircle, MapPin } from 'lucide-react';
import { searchAirports } from '../api';

export default function AirportSelector({
  origin,
  destination,
  onSelectOrigin,
  onSelectDestination,
}) {
  const [originQuery, setOriginQuery] = useState('');
  const [destQuery, setDestQuery] = useState('');
  const [originResults, setOriginResults] = useState([]);
  const [destResults, setDestResults] = useState([]);
  const [showOriginMenu, setShowOriginMenu] = useState(false);
  const [showDestMenu, setShowDestMenu] = useState(false);
  const [loadingOrigin, setLoadingOrigin] = useState(false);
  const [loadingDest, setLoadingDest] = useState(false);

  const originRef = useRef(null);
  const destRef = useRef(null);

  // Search origin airports
  useEffect(() => {
    let active = true;
    const fetchApts = async () => {
      setLoadingOrigin(true);
      try {
        const res = await searchAirports(originQuery);
        if (active) setOriginResults(res);
      } catch (err) {
        console.error(err);
      } finally {
        if (active) setLoadingOrigin(false);
      }
    };
    const t = setTimeout(fetchApts, 200);
    return () => {
      active = false;
      clearTimeout(t);
    };
  }, [originQuery]);

  // Search dest airports
  useEffect(() => {
    let active = true;
    const fetchApts = async () => {
      setLoadingDest(true);
      try {
        const res = await searchAirports(destQuery);
        if (active) setDestResults(res);
      } catch (err) {
        console.error(err);
      } finally {
        if (active) setLoadingDest(false);
      }
    };
    const t = setTimeout(fetchApts, 200);
    return () => {
      active = false;
      clearTimeout(t);
    };
  }, [destQuery]);

  // Close menus on outside click
  useEffect(() => {
    const handleOutside = (e) => {
      if (originRef.current && !originRef.current.contains(e.target)) {
        setShowOriginMenu(false);
      }
      if (destRef.current && !destRef.current.contains(e.target)) {
        setShowDestMenu(false);
      }
    };
    document.addEventListener('mousedown', handleOutside);
    return () => document.removeEventListener('mousedown', handleOutside);
  }, []);

  const handleSelectOrigin = (apt) => {
    if (destination && destination.icao === apt.icao) {
      alert("Departure and destination airports cannot be the same.");
      return;
    }
    onSelectOrigin(apt);
    setShowOriginMenu(false);
    setOriginQuery('');
  };

  const handleSelectDest = (apt) => {
    if (origin && origin.icao === apt.icao) {
      alert("Departure and destination airports cannot be the same.");
      return;
    }
    onSelectDestination(apt);
    setShowDestMenu(false);
    setDestQuery('');
  };

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      {/* ORIGIN SELECTOR */}
      <div className="relative" ref={originRef}>
        <label className="flex items-center gap-2 text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1.5">
          <PlaneTakeoff className="w-4 h-4 text-cyan-400" />
          From Airport (Departure)
        </label>
        <div
          onClick={() => setShowOriginMenu(true)}
          className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
            showOriginMenu
              ? 'border-cyan-400 bg-slate-800/90 ring-1 ring-cyan-400'
              : 'border-slate-700 bg-slate-900/80 hover:border-slate-600'
          }`}
        >
          {origin ? (
            <div className="flex items-center gap-3">
              <span className="px-2 py-0.5 text-xs font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-700 rounded">
                {origin.iata || origin.icao}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-100">{origin.name}</p>
                <p className="text-xs text-slate-400">
                  {origin.city}, {origin.country} • {origin.icao} • {origin.elevation_ft} ft
                </p>
              </div>
            </div>
          ) : (
            <span className="text-sm text-slate-400">Search departure (e.g. DEL, Delhi)...</span>
          )}
          <Search className="w-4 h-4 text-slate-400" />
        </div>

        {/* Dropdown Menu */}
        {showOriginMenu && (
          <div className="absolute z-50 left-0 right-0 mt-1.5 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl overflow-hidden backdrop-blur-md">
            <div className="p-2 border-b border-slate-800">
              <div className="flex items-center gap-2 px-2.5 py-1.5 bg-slate-800 rounded border border-slate-700">
                <Search className="w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search city, IATA, ICAO..."
                  value={originQuery}
                  onChange={(e) => setOriginQuery(e.target.value)}
                  autoFocus
                  className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none font-mono"
                />
              </div>
            </div>
            <div className="max-h-60 overflow-y-auto divide-y divide-slate-800">
              {loadingOrigin ? (
                <div className="p-3 text-xs text-center text-slate-400">Searching authoritative registry...</div>
              ) : originResults.length === 0 ? (
                <div className="p-3 text-xs text-center text-slate-500">No matching airport found</div>
              ) : (
                originResults.map((apt) => {
                  const isSelected = origin?.icao === apt.icao;
                  const isOther = destination?.icao === apt.icao;
                  return (
                    <button
                      key={apt.icao}
                      type="button"
                      disabled={isOther}
                      onClick={() => handleSelectOrigin(apt)}
                      className={`w-full text-left p-2.5 flex items-center justify-between transition-colors ${
                        isOther
                          ? 'opacity-40 cursor-not-allowed bg-slate-950'
                          : isSelected
                          ? 'bg-cyan-950/40 text-cyan-300'
                          : 'hover:bg-slate-800/80 text-slate-200'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold font-mono text-cyan-400">
                            {apt.iata ? `${apt.iata} / ${apt.icao}` : apt.icao}
                          </span>
                          <span className="text-xs text-slate-300 font-medium">{apt.name}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-500" />
                          <span>{apt.city}, {apt.country}</span>
                          <span>•</span>
                          <span>{apt.latitude.toFixed(2)}°, {apt.longitude.toFixed(2)}°</span>
                        </div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />}
                      {isOther && <span className="text-[10px] text-amber-500">Selected as To</span>}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>

      {/* DESTINATION SELECTOR */}
      <div className="relative" ref={destRef}>
        <label className="flex items-center gap-2 text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-1.5">
          <PlaneLanding className="w-4 h-4 text-cyan-400" />
          To Airport (Destination)
        </label>
        <div
          onClick={() => setShowDestMenu(true)}
          className={`flex items-center justify-between p-3 rounded-lg border cursor-pointer transition-all ${
            showDestMenu
              ? 'border-cyan-400 bg-slate-800/90 ring-1 ring-cyan-400'
              : 'border-slate-700 bg-slate-900/80 hover:border-slate-600'
          }`}
        >
          {destination ? (
            <div className="flex items-center gap-3">
              <span className="px-2 py-0.5 text-xs font-mono font-bold bg-cyan-950 text-cyan-300 border border-cyan-700 rounded">
                {destination.iata || destination.icao}
              </span>
              <div>
                <p className="text-sm font-medium text-slate-100">{destination.name}</p>
                <p className="text-xs text-slate-400">
                  {destination.city}, {destination.country} • {destination.icao} • {destination.elevation_ft} ft
                </p>
              </div>
            </div>
          ) : (
            <span className="text-sm text-slate-400">Search destination (e.g. HYD, Hyderabad)...</span>
          )}
          <Search className="w-4 h-4 text-slate-400" />
        </div>

        {/* Dropdown Menu */}
        {showDestMenu && (
          <div className="absolute z-50 left-0 right-0 mt-1.5 bg-slate-900 border border-slate-700 rounded-lg shadow-2xl overflow-hidden backdrop-blur-md">
            <div className="p-2 border-b border-slate-800">
              <div className="flex items-center gap-2 px-2.5 py-1.5 bg-slate-800 rounded border border-slate-700">
                <Search className="w-3.5 h-3.5 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search city, IATA, ICAO..."
                  value={destQuery}
                  onChange={(e) => setDestQuery(e.target.value)}
                  autoFocus
                  className="w-full bg-transparent text-xs text-slate-100 placeholder-slate-500 focus:outline-none font-mono"
                />
              </div>
            </div>
            <div className="max-h-60 overflow-y-auto divide-y divide-slate-800">
              {loadingDest ? (
                <div className="p-3 text-xs text-center text-slate-400">Searching authoritative registry...</div>
              ) : destResults.length === 0 ? (
                <div className="p-3 text-xs text-center text-slate-500">No matching airport found</div>
              ) : (
                destResults.map((apt) => {
                  const isSelected = destination?.icao === apt.icao;
                  const isOther = origin?.icao === apt.icao;
                  return (
                    <button
                      key={apt.icao}
                      type="button"
                      disabled={isOther}
                      onClick={() => handleSelectDest(apt)}
                      className={`w-full text-left p-2.5 flex items-center justify-between transition-colors ${
                        isOther
                          ? 'opacity-40 cursor-not-allowed bg-slate-950'
                          : isSelected
                          ? 'bg-cyan-950/40 text-cyan-300'
                          : 'hover:bg-slate-800/80 text-slate-200'
                      }`}
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="text-xs font-bold font-mono text-cyan-400">
                            {apt.iata ? `${apt.iata} / ${apt.icao}` : apt.icao}
                          </span>
                          <span className="text-xs text-slate-300 font-medium">{apt.name}</span>
                        </div>
                        <div className="text-[11px] text-slate-400 flex items-center gap-2 mt-0.5">
                          <MapPin className="w-3 h-3 text-slate-500" />
                          <span>{apt.city}, {apt.country}</span>
                          <span>•</span>
                          <span>{apt.latitude.toFixed(2)}°, {apt.longitude.toFixed(2)}°</span>
                        </div>
                      </div>
                      {isSelected && <CheckCircle2 className="w-4 h-4 text-cyan-400 shrink-0" />}
                      {isOther && <span className="text-[10px] text-amber-500">Selected as From</span>}
                    </button>
                  );
                })
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
