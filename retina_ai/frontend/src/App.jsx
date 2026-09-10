import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import ScreeningDashboard from '../pages/ScreeningDashboard';
import PatientDirectory from '../pages/PatientDirectory';
import ResourceSimulatorPage from '../pages/ResourceSimulatorPage';
import PatientForm from '../components/PatientForm';

export default function App() {
  const [activeTab, setActiveTab] = useState('screening');
  const [patients, setPatients] = useState([]);
  const [activePatient, setActivePatient] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);

  const fetchPatients = async () => {
    try {
      const res = await fetch('/api/patients');
      const data = await res.json();
      setPatients(data);
      if (data.length > 0 && !activePatient) {
        setActivePatient(data[0]);
      }
    } catch (err) {
      console.error("Failed to load patients", err);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, []);

  const handlePatientCreated = (newPatient) => {
    setPatients(prev => [newPatient, ...prev]);
    setActivePatient(newPatient);
    setActiveTab('screening');
  };

  const handleSelectPatientForScreening = (patient) => {
    setActivePatient(patient);
    setActiveTab('screening');
  };

  return (
    <div className="min-h-screen flex flex-col bg-slate-50 font-sans">
      <Navbar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenPatientModal={() => setIsModalOpen(true)}
      />

      <main className="flex-1 max-w-7xl w-full mx-auto p-4 sm:p-6 lg:p-8">
        {activeTab === 'screening' && (
          <ScreeningDashboard
            patients={patients}
            activePatient={activePatient}
            setActivePatient={setActivePatient}
          />
        )}

        {activeTab === 'patients' && (
          <PatientDirectory
            patients={patients}
            onSelectPatientForScreening={handleSelectPatientForScreening}
            onOpenPatientModal={() => setIsModalOpen(true)}
          />
        )}

        {activeTab === 'simulation' && (
          <ResourceSimulatorPage />
        )}

        {activeTab === 'ml-hub' && (
          <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-6 space-y-6">
            <span className="px-2.5 py-0.5 rounded-full bg-purple-100 text-purple-800 text-xs font-bold uppercase">
              ML Model Contract
            </span>
            <h2 className="text-lg font-black text-slate-800">Machine Learning Integration Hub</h2>
            <p className="text-xs text-slate-600 leading-relaxed">
              Place exported ONNX models in <code className="bg-slate-100 px-1 py-0.5 rounded font-mono">retina_ai/models/exported/dr_model.onnx</code>. The backend will automatically switch to neural network inference.
            </p>
          </div>
        )}
      </main>

      <PatientForm
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onPatientCreated={handlePatientCreated}
      />

      <footer className="bg-white border-t border-slate-200 py-4 text-center text-xs text-slate-500">
        RetinaAI &bull; Problem Statement 26038 (MathWorks) &bull; Explainable AI for Rural India
      </footer>
    </div>
  );
}
