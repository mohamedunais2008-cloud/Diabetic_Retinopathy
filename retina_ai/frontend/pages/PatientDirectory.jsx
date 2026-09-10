import React, { useState } from 'react';
import { Search, UserPlus } from 'lucide-react';

export default function PatientDirectory({ patients, onSelectPatientForScreening, onOpenPatientModal }) {
  const [search, setSearch] = useState('');

  const filtered = patients.filter(p =>
    p.full_name.toLowerCase().includes(search.toLowerCase()) ||
    p.patient_uid.toLowerCase().includes(search.toLowerCase()) ||
    p.village.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
      <div className="flex flex-col sm:flex-row items-center justify-between gap-4">
        <div>
          <h3 className="font-bold text-slate-800 text-base">Rural Patient Directory</h3>
          <p className="text-xs text-slate-500">Track screened patients and triage follow-ups</p>
        </div>

        <div className="flex items-center space-x-2 w-full sm:w-auto">
          <div className="relative w-full sm:w-64">
            <Search className="w-4 h-4 absolute left-3 top-2.5 text-slate-400" />
            <input
              type="text"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              placeholder="Search Name, Village, UID..."
              className="w-full pl-9 pr-3 py-1.5 text-xs rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
            />
          </div>
          <button
            onClick={onOpenPatientModal}
            className="px-3 py-1.5 rounded-lg bg-sky-600 hover:bg-sky-500 text-white text-xs font-semibold whitespace-nowrap"
          >
            + New Patient
          </button>
        </div>
      </div>

      <div className="overflow-x-auto">
        <table className="w-full text-left text-xs text-slate-600">
          <thead className="bg-slate-50 text-slate-500 uppercase tracking-wider font-bold border-y border-slate-200">
            <tr>
              <th className="py-3 px-4">Patient UID</th>
              <th className="py-3 px-4">Name</th>
              <th className="py-3 px-4">Age / Sex</th>
              <th className="py-3 px-4">Village / District</th>
              <th className="py-3 px-4">Diabetes Yrs</th>
              <th className="py-3 px-4">HbA1c</th>
              <th className="py-3 px-4 text-right">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {filtered.map(p => (
              <tr key={p.id} className="hover:bg-slate-50 border-b border-slate-100">
                <td className="py-3 px-4 font-mono font-bold text-sky-700">{p.patient_uid}</td>
                <td className="py-3 px-4 font-bold text-slate-800">{p.full_name}</td>
                <td className="py-3 px-4">{p.age} yrs / {p.gender}</td>
                <td className="py-3 px-4">{p.village}, {p.district}</td>
                <td className="py-3 px-4">{p.diabetes_years} yrs</td>
                <td className="py-3 px-4">{p.hba1c ? `${p.hba1c}%` : 'N/A'}</td>
                <td className="py-3 px-4 text-right">
                  <button
                    onClick={() => onSelectPatientForScreening(p)}
                    className="px-2.5 py-1 rounded bg-sky-50 text-sky-700 border border-sky-200 hover:bg-sky-100 font-semibold text-[11px]"
                  >
                    Screen Fundus
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
