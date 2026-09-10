import React from 'react';
import { Eye, Activity, Users, Cpu, GitBranch, UserPlus } from 'lucide-react';

export default function Navbar({ activeTab, setActiveTab, onOpenPatientModal }) {
  return (
    <header className="bg-slate-900 text-white border-b border-slate-800 sticky top-0 z-50 shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 rounded-lg bg-sky-500/20 border border-sky-400/40 flex items-center justify-center text-sky-300">
              <Eye className="w-6 h-6" />
            </div>
            <div>
              <div className="flex items-center space-x-2">
                <span className="font-bold text-lg tracking-tight text-white">RetinaAI</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-sky-500/20 text-sky-300 border border-sky-400/30">PS 26038</span>
              </div>
              <p className="text-xs text-slate-300">Explainable AI for DR Screening in Rural India &bull; MathWorks</p>
            </div>
          </div>

          <nav className="hidden md:flex space-x-1">
            <button
              onClick={() => setActiveTab('screening')}
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'screening' ? 'bg-sky-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Activity className="w-4 h-4" />
              <span>Screening Station</span>
            </button>

            <button
              onClick={() => setActiveTab('patients')}
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'patients' ? 'bg-sky-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Users className="w-4 h-4" />
              <span>Patient Registry</span>
            </button>

            <button
              onClick={() => setActiveTab('simulation')}
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'simulation' ? 'bg-sky-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <Cpu className="w-4 h-4" />
              <span>Telemedicine (100k)</span>
            </button>

            <button
              onClick={() => setActiveTab('ml-hub')}
              className={`px-3.5 py-1.5 rounded-md text-sm font-medium transition-all flex items-center space-x-1.5 ${
                activeTab === 'ml-hub' ? 'bg-sky-600 text-white' : 'text-slate-300 hover:text-white hover:bg-slate-800'
              }`}
            >
              <GitBranch className="w-4 h-4" />
              <span>ML Integration</span>
            </button>
          </nav>

          <div className="flex items-center space-x-3">
            <button
              onClick={onOpenPatientModal}
              className="px-3 py-1.5 rounded-lg bg-sky-500 hover:bg-sky-400 text-white text-xs font-semibold shadow-sm transition-all flex items-center space-x-1"
            >
              <UserPlus className="w-4 h-4" />
              <span>+ Patient</span>
            </button>
          </div>

        </div>
      </div>
    </header>
  );
}
