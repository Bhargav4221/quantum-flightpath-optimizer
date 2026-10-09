import React, { useState } from 'react';
import { Database, ShieldCheck, AlertCircle, Radio, Clock, CheckCircle2 } from 'lucide-react';

export default function DataProvenance({ provenances }) {
  const [isOpen, setIsOpen] = useState(false);

  if (!provenances || provenances.length === 0) return null;

  const getStatusBadge = (status, isLive) => {
    if (isLive) {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-cyan-950 text-cyan-300 border border-cyan-700 flex items-center gap-1">
          <Radio className="w-2.5 h-2.5 animate-pulse" /> Live Data Connected
        </span>
      );
    }
    if (status === 'Authoritative published data') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-emerald-950 text-emerald-300 border border-emerald-800 flex items-center gap-1">
          <ShieldCheck className="w-2.5 h-2.5" /> Authoritative Published Data
        </span>
      );
    }
    if (status === 'Data source unavailable') {
      return (
        <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-slate-800 text-slate-400 border border-slate-700 flex items-center gap-1">
          <AlertCircle className="w-2.5 h-2.5" /> Data Source Unavailable
        </span>
      );
    }
    return (
      <span className="px-2 py-0.5 rounded text-[10px] font-mono bg-amber-950 text-amber-300 border border-amber-800">
        {status}
      </span>
    );
  };

  return (
    <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-4 shadow-lg backdrop-blur-md">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-2">
        <div className="flex items-center gap-2">
          <Database className="w-4 h-4 text-cyan-400" />
          <h3 className="text-xs font-semibold text-slate-200 uppercase tracking-wider">
            Aeronautical Data Provenance & Authoritative Sources
          </h3>
        </div>
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="text-xs text-cyan-400 hover:text-cyan-300 font-mono underline"
        >
          {isOpen ? 'Collapse Provenance Registry' : `View All (${provenances.length} Datasets)`}
        </button>
      </div>

      {/* Grid of datasets */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
        {(isOpen ? provenances : provenances.slice(0, 3)).map((item, idx) => (
          <div
            key={idx}
            className="p-3 bg-slate-950/70 border border-slate-800 rounded-lg flex flex-col justify-between space-y-2 text-xs"
          >
            <div>
              <div className="flex items-center justify-between gap-1 mb-1">
                <h4 className="font-semibold text-slate-100 text-xs truncate" title={item.dataset_name}>
                  {item.dataset_name}
                </h4>
              </div>
              <div className="mb-2">{getStatusBadge(item.validation_status, item.live_connected)}</div>

              <div className="space-y-1 text-[11px] text-slate-400">
                <p>
                  <strong className="text-slate-300">Provider:</strong> {item.provider}
                </p>
                <p>
                  <strong className="text-slate-300">Document/Cycle:</strong> {item.dataset_version}
                </p>
                <p>
                  <strong className="text-slate-300">Coverage:</strong> {item.geographic_coverage}
                </p>
                {item.effective_date && (
                  <p>
                    <strong className="text-slate-300">Effective:</strong>{' '}
                    {item.effective_date.split('T')[0]}
                  </p>
                )}
              </div>
            </div>

            {item.notes && (
              <p className="text-[10px] text-slate-500 border-t border-slate-800/80 pt-1.5 line-clamp-2">
                {item.notes}
              </p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
}
