import React, { useRef } from 'react';
import { Camera, UploadCloud, Sparkles, Microscope } from 'lucide-react';

export default function FundusUploader({
  selectedFile,
  setSelectedFile,
  activeEye,
  setActiveEye,
  ashaNotes,
  setAshaNotes,
  onRunScreening,
  loading
}) {
  const fileInputRef = useRef(null);

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
    }
  };

  const loadSampleFundus = () => {
    const canvas = document.createElement("canvas");
    canvas.width = 512;
    canvas.height = 512;
    const ctx = canvas.getContext("2d");

    ctx.fillStyle = "#0a0a0c";
    ctx.fillRect(0, 0, 512, 512);

    const grad = ctx.createRadialGradient(256, 256, 40, 256, 256, 230);
    grad.addColorStop(0, "#d35400");
    grad.addColorStop(0.5, "#b93e0b");
    grad.addColorStop(0.85, "#801d00");
    grad.addColorStop(1.0, "#0a0a0c");

    ctx.beginPath();
    ctx.arc(256, 256, 230, 0, Math.PI * 2);
    ctx.fillStyle = grad;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(380, 250, 36, 0, Math.PI * 2);
    ctx.fillStyle = "#f39c12";
    ctx.fill();

    ctx.strokeStyle = "#4a0000";
    ctx.lineWidth = 3.5;
    ctx.beginPath();
    ctx.moveTo(380, 250);
    ctx.bezierCurveTo(320, 160, 240, 140, 160, 180);
    ctx.moveTo(380, 250);
    ctx.bezierCurveTo(320, 340, 240, 360, 160, 320);
    ctx.stroke();

    canvas.toBlob((blob) => {
      const file = new File([blob], "sample_idrid_fundus.jpg", { type: "image/jpeg" });
      setSelectedFile(file);
    }, "image/jpeg");
  };

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-5 space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-bold text-slate-800 flex items-center space-x-2 text-sm">
          <Camera className="w-4 h-4 text-sky-600" />
          <span>Fundus Image Acquisition</span>
        </h3>
        <button
          type="button"
          onClick={loadSampleFundus}
          className="text-xs px-2.5 py-1 rounded-md border border-sky-300 text-sky-700 bg-sky-50 hover:bg-sky-100 font-medium flex items-center space-x-1"
        >
          <Sparkles className="w-3 h-3" />
          <span>Sample IDRiD</span>
        </button>
      </div>

      {/* Eye Selector */}
      <div className="flex items-center space-x-2 bg-slate-100 p-1 rounded-lg border border-slate-200">
        <span className="text-xs font-semibold text-slate-500 px-2">Eye:</span>
        <button
          type="button"
          onClick={() => setActiveEye('OD')}
          className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${
            activeEye === 'OD' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          OD (Right Eye)
        </button>
        <button
          type="button"
          onClick={() => setActiveEye('OS')}
          className={`flex-1 py-1 text-xs font-bold rounded-md transition-all ${
            activeEye === 'OS' ? 'bg-white text-sky-700 shadow-sm' : 'text-slate-600 hover:text-slate-900'
          }`}
        >
          OS (Left Eye)
        </button>
      </div>

      {/* Dropzone */}
      <div
        onClick={() => fileInputRef.current?.click()}
        className="border-2 border-dashed border-slate-300 hover:border-sky-500 rounded-xl p-6 text-center cursor-pointer transition-all bg-slate-50/50 hover:bg-sky-50/30 flex flex-col items-center justify-center min-h-[200px]"
      >
        <input
          ref={fileInputRef}
          type="file"
          accept="image/*"
          className="hidden"
          onChange={handleFileChange}
        />
        {selectedFile ? (
          <img
            src={URL.createObjectURL(selectedFile)}
            alt="Preview"
            className="max-h-[200px] w-auto object-contain rounded-lg shadow-sm"
          />
        ) : (
          <div className="space-y-2">
            <div className="w-12 h-12 mx-auto rounded-full bg-sky-100 text-sky-600 flex items-center justify-center">
              <UploadCloud className="w-6 h-6" />
            </div>
            <div className="text-xs text-slate-600">
              <span className="font-bold text-sky-600">Click to upload</span> or drag & drop fundus photo
            </div>
            <p className="text-[11px] text-slate-400">Standard 45° macula-centered view</p>
          </div>
        )}
      </div>

      {/* ASHA Notes */}
      <div>
        <label className="block text-xs font-semibold text-slate-600 mb-1">ASHA Worker / Camp Notes:</label>
        <textarea
          value={ashaNotes}
          onChange={(e) => setAshaNotes(e.target.value)}
          rows={2}
          placeholder="e.g., Vision blurring for 2 months, known diabetic for 7 years."
          className="w-full text-xs p-2.5 rounded-lg border border-slate-300 focus:ring-sky-500 focus:border-sky-500 bg-slate-50"
        />
      </div>

      <button
        onClick={onRunScreening}
        disabled={loading}
        className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-sky-600 to-sky-700 hover:from-sky-500 hover:to-sky-600 text-white font-bold text-sm shadow-md transition-all flex items-center justify-center space-x-2 disabled:opacity-50"
      >
        <Microscope className="w-4 h-4" />
        <span>{loading ? 'Analyzing Microvasculature & Heatmap...' : 'Run Explainable AI Screening'}</span>
      </button>
    </div>
  );
}
