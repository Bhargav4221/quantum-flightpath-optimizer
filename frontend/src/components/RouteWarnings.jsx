import React from 'react';
import { ShieldAlert, AlertTriangle, Info } from 'lucide-react';

export default function RouteWarnings({ disclaimer, quantumRoute, classicalRoute }) {
  const notes = quantumRoute?.validation_notes || [];

  return (
    <div className="space-y-3">
      {/* Prominent Safety Disclaimer Banner */}
      <div className="bg-amber-950/30 border border-amber-800/60 rounded-xl p-3.5 shadow-md flex items-start gap-3">
        <ShieldAlert className="w-5 h-5 text-amber-400 shrink-0 mt-0.5" />
        <div className="text-xs text-amber-200/90 leading-relaxed">
          <span className="font-bold text-amber-300 block mb-0.5 uppercase tracking-wide text-[11px]">
            Aviation Safety & Regulatory Disclaimer
          </span>
          {disclaimer ||
            'This application provides research and decision-support recommendations based on available aeronautical information. Its output is not an ATC clearance, certified operational flight plan, or authorization to operate an aircraft. Actual flight routing remains subject to applicable aviation regulations, current aeronautical information, weather, aircraft capability, operational constraints, and ATC authorization.'}
        </div>
      </div>

      {/* Validation Notes & Classical Post-Processing Disclosures */}
      {notes.length > 0 && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-xl p-3 shadow-md">
          <div className="flex items-center gap-1.5 text-xs font-semibold text-slate-300 mb-2">
            <Info className="w-4 h-4 text-cyan-400" />
            <span>Route Validation & Quantum Sampling Disclosures</span>
          </div>
          <ul className="space-y-1.5 text-xs text-slate-400 list-disc list-inside">
            {notes.map((note, idx) => (
              <li key={idx} className="leading-snug">
                {note}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
