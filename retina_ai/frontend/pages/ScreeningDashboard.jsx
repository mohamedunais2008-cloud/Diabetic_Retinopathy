import React, { useState } from 'react';
import FundusUploader from '../components/FundusUploader';
import HeatmapViewer from '../components/HeatmapViewer';
import TriageBadge from '../components/TriageBadge';
import { Download, FileText, Crosshair, AlertTriangle } from 'lucide-react';

export default function ScreeningDashboard({ patients, activePatient, setActivePatient }) {
  const [activeEye, setActiveEye] = useState('OD');
  const [selectedFile, setSelectedFile] = useState(null);
  const [ashaNotes, setAshaNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);

  const handleScreening = async () => {
    if (!activePatient) {
      alert("Please select a patient first.");
      return;
    }
    if (!selectedFile) {
      alert("Please upload a fundus photo or load sample.");
      return;
    }

    setLoading(true);
    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('patient_id', activePatient.id);
    formData.append('eye', activeEye);
    formData.append('asha_notes', ashaNotes);

    try {
      const res = await fetch('/api/predict', {
        method: 'POST',
        body: formData
      });
      if (!res.ok) throw new Error("Inference failed");
      const data = await res.json();
      setResult(data);
    } catch (err) {
      alert(err.message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Patient selector */}
      <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <label className="text-xs font-bold uppercase tracking-wider text-slate-500">Active Patient:</label>
          <select
            value={activePatient ? activePatient.id : ''}
            onChange={(e) => {
              const p = patients.find(x => x.id === parseInt(e.target.value));
              setActivePatient(p || null);
            }}
            className="bg-slate-50 border border-slate-300 text-slate-800 text-sm rounded-lg p-2 font-medium min-w-[280px]"
          >
            <option value="">-- Select Patient --</option>
            {patients.map(p => (
              <option key={p.id} value={p.id}>
                {p.full_name} ({p.patient_uid}) - {p.village}
              </option>
            ))}
          </select>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        <div className="lg:col-span-5">
          <FundusUploader
            selectedFile={selectedFile}
            setSelectedFile={setSelectedFile}
            activeEye={activeEye}
            setActiveEye={setActiveEye}
            ashaNotes={ashaNotes}
            setAshaNotes={setAshaNotes}
            onRunScreening={handleScreening}
            loading={loading}
          />
        </div>

        <div className="lg:col-span-7 space-y-4">
          {!result ? (
            <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-12 text-center text-slate-400">
              <h4 className="font-semibold text-slate-600 text-base">Awaiting Fundus Examination</h4>
              <p className="text-xs text-slate-400 max-w-md mx-auto mt-1">
                Upload a fundus photo or load sample IDRiD image and click Run Screening.
              </p>
            </div>
          ) : (
            <>
              <TriageBadge
                isReferable={result.is_referable}
                gradeName={result.grade_name}
                urgency={result.urgency}
                confidencePercent={result.confidence_percent}
              />

              <HeatmapViewer
                rawUrl={result.images.raw_url}
                prepUrl={result.images.preprocessed_url}
                gradcamUrl={result.images.gradcam_url}
              />

              {/* Sub-pixel lesion counts */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 space-y-2.5">
                <div className="flex items-center justify-between">
                  <h4 className="font-bold text-xs text-slate-800 uppercase tracking-wider flex items-center space-x-1.5">
                    <Crosshair className="w-3.5 h-3.5 text-sky-600" />
                    <span>Sub-Pixel Lesion Detection Summary</span>
                  </h4>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 text-center">
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Microaneurysms</span>
                    <span className="text-base font-extrabold text-slate-800">{result.pathology_findings.microaneurysms}</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Hemorrhages</span>
                    <span className="text-base font-extrabold text-slate-800">{result.pathology_findings.hemorrhages}</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Hard Exudates</span>
                    <span className="text-base font-extrabold text-slate-800">{result.pathology_findings.hard_exudates}</span>
                  </div>
                  <div className="p-2 bg-slate-50 rounded-lg border border-slate-100">
                    <span className="text-[10px] text-slate-500 block">Neovascularization</span>
                    <span className="text-xs font-extrabold text-slate-800">{result.pathology_findings.neovascularization}</span>
                  </div>
                </div>
              </div>

              {/* XAI & Clinical notes */}
              <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 space-y-3">
                <div>
                  <h4 className="text-xs font-bold text-slate-800 flex items-center space-x-1.5">
                    <FileText className="w-3.5 h-3.5 text-sky-600" />
                    <span>Explainable AI Saliency Rationale</span>
                  </h4>
                  <p className="text-xs text-slate-600 mt-1 leading-relaxed">{result.xai_summary}</p>
                </div>

                <div className="bg-amber-50/70 border border-amber-200/80 rounded-lg p-3">
                  <h5 className="text-xs font-bold text-amber-900 flex items-center space-x-1">
                    <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                    <span>ASHA Worker / PHC Action Directive:</span>
                  </h5>
                  <p className="text-xs text-amber-800 mt-0.5 font-medium">{result.asha_guidance}</p>
                </div>

                <div className="pt-2 flex items-center justify-between">
                  <span className="text-[11px] text-slate-400">Model: {result.model_source}</span>
                  <a
                    href={result.report_pdf_url}
                    target="_blank"
                    rel="noreferrer"
                    className="px-4 py-2 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold shadow-sm transition-all flex items-center space-x-1.5"
                  >
                    <Download className="w-4 h-4" />
                    <span>Download Referral PDF</span>
                  </a>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
