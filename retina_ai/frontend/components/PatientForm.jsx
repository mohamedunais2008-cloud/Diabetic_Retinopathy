import React, { useState } from 'react';
import { UserPlus, X } from 'lucide-react';

export default function PatientForm({ isOpen, onClose, onPatientCreated }) {
  const [formData, setFormData] = useState({
    full_name: '',
    age: '',
    gender: 'Male',
    village: '',
    district: 'Madurai',
    diabetes_years: '',
    hba1c: '',
    phone: ''
  });
  const [loading, setLoading] = useState(false);

  if (!isOpen) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await fetch('/api/patients', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          ...formData,
          age: parseInt(formData.age),
          diabetes_years: parseFloat(formData.diabetes_years || '0'),
          hba1c: formData.hba1c ? parseFloat(formData.hba1c) : null,
          hypertension: false,
          smoker: false
        })
      });
      if (!res.ok) throw new Error('Registration failed');
      const newPatient = await res.json();
      onPatientCreated(newPatient);
      onClose();
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 bg-slate-900/60 backdrop-blur-sm flex items-center justify-center p-4">
      <div className="bg-white rounded-2xl max-w-lg w-full p-6 shadow-2xl space-y-4 border border-slate-100">
        <div className="flex items-center justify-between border-b border-slate-100 pb-3">
          <h3 className="font-bold text-base text-slate-800 flex items-center space-x-2">
            <UserPlus className="w-5 h-5 text-sky-600" />
            <span>Register Rural Screening Patient</span>
          </h3>
          <button onClick={onClose} className="text-slate-400 hover:text-slate-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-3 text-xs">
          <div>
            <label className="block font-semibold text-slate-700 mb-1">Full Name *</label>
            <input
              type="text"
              required
              value={formData.full_name}
              onChange={(e) => setFormData({ ...formData, full_name: e.target.value })}
              placeholder="e.g. Ramesh Kumar"
              className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
            />
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Age *</label>
              <input
                type="number"
                required
                min="1"
                max="115"
                value={formData.age}
                onChange={(e) => setFormData({ ...formData, age: e.target.value })}
                placeholder="54"
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Gender *</label>
              <select
                value={formData.gender}
                onChange={(e) => setFormData({ ...formData, gender: e.target.value })}
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              >
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
              </select>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Village / PHC Block *</label>
              <input
                type="text"
                required
                value={formData.village}
                onChange={(e) => setFormData({ ...formData, village: e.target.value })}
                placeholder="e.g. Alanganallur"
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">District *</label>
              <input
                type="text"
                required
                value={formData.district}
                onChange={(e) => setFormData({ ...formData, district: e.target.value })}
                placeholder="Madurai"
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="block font-semibold text-slate-700 mb-1">Diabetes Duration (Yrs)</label>
              <input
                type="number"
                step="0.5"
                value={formData.diabetes_years}
                onChange={(e) => setFormData({ ...formData, diabetes_years: e.target.value })}
                placeholder="8"
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
            <div>
              <label className="block font-semibold text-slate-700 mb-1">HbA1c (%)</label>
              <input
                type="number"
                step="0.1"
                value={formData.hba1c}
                onChange={(e) => setFormData({ ...formData, hba1c: e.target.value })}
                placeholder="8.2"
                className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
              />
            </div>
          </div>

          <div>
            <label className="block font-semibold text-slate-700 mb-1">Phone Number</label>
            <input
              type="tel"
              value={formData.phone}
              onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
              placeholder="+91 98421 11021"
              className="w-full p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500"
            />
          </div>

          <div className="pt-3 flex items-center justify-end space-x-2 border-t border-slate-100">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 rounded-lg border border-slate-300 text-slate-600 hover:bg-slate-50 font-semibold"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-5 py-2 rounded-lg bg-sky-600 hover:bg-sky-500 text-white font-bold shadow-sm"
            >
              {loading ? 'Saving...' : 'Register Patient'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
