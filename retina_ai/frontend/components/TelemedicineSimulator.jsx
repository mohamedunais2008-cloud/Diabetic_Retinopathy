import React, { useState, useEffect } from 'react';
import { Sliders, Play, CheckCircle2 } from 'lucide-react';

export default function TelemedicineSimulator() {
  const [pop, setPop] = useState(100000);
  const [phc, setPhc] = useState(50);
  const [bw, setBw] = useState(2.0);
  const [doc, setDoc] = useState(5);
  const [simResult, setSimResult] = useState(null);

  const runSim = async () => {
    try {
      const res = await fetch('/api/simulation/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          annual_population: pop,
          num_phcs: phc,
          bandwidth_mbps: bw,
          doctor_count: doc
        })
      });
      const data = await res.json();
      setSimResult(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    runSim();
  }, []);

  return (
    <div className="space-y-6">
      <div className="bg-slate-900 rounded-xl p-6 text-white shadow-sm space-y-2">
        <span className="px-2.5 py-0.5 rounded-full bg-sky-400/20 text-sky-300 border border-sky-400/30 text-xs font-bold uppercase">
          MathWorks PS 26038 Requirement
        </span>
        <h2 className="text-xl font-black">District-Level Telemedicine Screening Pipeline Simulator</h2>
        <p className="text-xs text-slate-300 max-w-3xl leading-relaxed">
          Simulates image acquisition rates, 2G/3G bandwidth constraints, Edge AI processing throughput, and specialist review capacity to optimize resource allocation for district programs screening 100,000+ patients annually.
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5 bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
          <h3 className="font-bold text-sm text-slate-800 flex items-center space-x-1.5 border-b border-slate-100 pb-2">
            <Sliders className="w-4 h-4 text-sky-600" />
            <span>Simulation Parameters</span>
          </h3>

          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-700">Annual Target Cohort:</label>
              <span className="font-bold text-sky-700">{pop.toLocaleString()} patients</span>
            </div>
            <input
              type="range"
              min="10000"
              max="300000"
              step="10000"
              value={pop}
              onChange={(e) => setPop(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg accent-sky-600"
            />
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-700">Primary Health Centres (PHCs):</label>
              <span className="font-bold text-sky-700">{phc} centres</span>
            </div>
            <input
              type="range"
              min="10"
              max="150"
              step="5"
              value={phc}
              onChange={(e) => setPhc(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg accent-sky-600"
            />
          </div>

          <div className="space-y-1">
            <label className="block text-xs font-semibold text-slate-700">Rural Cellular Bandwidth:</label>
            <select
              value={bw}
              onChange={(e) => setBw(parseFloat(e.target.value))}
              className="w-full text-xs p-2.5 rounded-lg border border-slate-300 bg-slate-50 font-medium"
            >
              <option value="0.5">2G / GPRS (0.5 Mbps) - Extreme rural latency</option>
              <option value="2.0">3G Cellular (2.0 Mbps) - Standard rural PHC</option>
              <option value="8.0">4G LTE (8.0 Mbps) - Block CHC</option>
              <option value="40.0">Fibre / Broadband (40.0 Mbps) - District Hospital</option>
            </select>
          </div>

          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <label className="font-semibold text-slate-700">District Ophthalmologists Available:</label>
              <span className="font-bold text-sky-700">{doc} doctors</span>
            </div>
            <input
              type="range"
              min="1"
              max="15"
              step="1"
              value={doc}
              onChange={(e) => setDoc(parseInt(e.target.value))}
              className="w-full h-1.5 bg-slate-200 rounded-lg accent-sky-600"
            />
          </div>

          <button
            onClick={runSim}
            className="w-full py-2.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold text-xs shadow-sm transition-all flex items-center justify-center space-x-1.5"
          >
            <Play className="w-3.5 h-3.5" />
            <span>Re-compute Model</span>
          </button>
        </div>

        {simResult && (
          <div className="lg:col-span-7 space-y-4">
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-3 text-center">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Daily Screening</span>
                <span className="text-lg font-black text-slate-800">{Math.round(simResult.daily_screening_capacity)}</span>
                <span className="text-[10px] text-slate-500 block">patients / day</span>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-3 text-center">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Uplink Latency</span>
                <span className="text-lg font-black text-sky-700">{simResult.transfer_latency_sec}s</span>
                <span className="text-[10px] text-slate-500 block">per fundus pair</span>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-3 text-center">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Specialist Filter</span>
                <span className="text-lg font-black text-emerald-600">{simResult.workload_reduction_percent}%</span>
                <span className="text-[10px] text-emerald-700 block">workload cut</span>
              </div>
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-3 text-center">
                <span className="text-[10px] font-semibold text-slate-400 uppercase tracking-wider block">Doctors Needed</span>
                <span className="text-lg font-black text-slate-800">{simResult.doctors_needed}</span>
                <span className="text-[10px] text-slate-500 block">ophthalmologist</span>
              </div>
            </div>

            <div className="rounded-xl p-4 border bg-emerald-50 border-emerald-200 text-emerald-900 space-y-1">
              <div className="flex items-center space-x-2 font-bold text-sm text-emerald-800">
                <CheckCircle2 className="w-4 h-4" />
                <span>Simulink Queue Triage Status</span>
              </div>
              <p className="text-xs text-slate-600 leading-relaxed">{simResult.simulink_queue_status}</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
