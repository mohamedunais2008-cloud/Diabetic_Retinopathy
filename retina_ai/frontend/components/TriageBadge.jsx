import React from 'react';
import { CheckCircle, AlertOctagon } from 'lucide-react';

export default function TriageBadge({ isReferable, gradeName, urgency, confidencePercent }) {
  if (isReferable) {
    return (
      <div className="rounded-xl p-4 border bg-red-50/80 border-red-200 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white bg-red-600 shadow-sm">
            <AlertOctagon className="w-6 h-6" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-black text-sm tracking-wide uppercase text-red-700">
                REFERABLE DR - SPECIALIST REVIEW REQUIRED
              </span>
              <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-red-200 text-red-900">
                {urgency}
              </span>
            </div>
            <h2 className="text-lg font-extrabold text-slate-800">{gradeName}</h2>
          </div>
        </div>
        <div className="text-right">
          <span className="text-[11px] text-slate-500 font-semibold block">Confidence</span>
          <span className="text-xl font-black text-slate-800">{confidencePercent}</span>
        </div>
      </div>
    );
  }

  return (
    <div className="rounded-xl p-4 border bg-emerald-50/80 border-emerald-200 flex items-center justify-between">
      <div className="flex items-center space-x-3">
        <div className="w-12 h-12 rounded-xl flex items-center justify-center text-white bg-emerald-600 shadow-sm">
          <CheckCircle className="w-6 h-6" />
        </div>
        <div>
          <div className="flex items-center space-x-2">
            <span className="font-black text-sm tracking-wide uppercase text-emerald-700">
              NON-REFERABLE (ROUTINE ANNUAL FOLLOW-UP)
            </span>
            <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-emerald-200 text-emerald-900">
              {urgency}
            </span>
          </div>
          <h2 className="text-lg font-extrabold text-slate-800">{gradeName}</h2>
        </div>
      </div>
      <div className="text-right">
        <span className="text-[11px] text-slate-500 font-semibold block">Confidence</span>
        <span className="text-xl font-black text-slate-800">{confidencePercent}</span>
      </div>
    </div>
  );
}
