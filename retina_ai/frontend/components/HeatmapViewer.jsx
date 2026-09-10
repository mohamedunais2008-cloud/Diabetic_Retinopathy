import React, { useState } from 'react';

export default function HeatmapViewer({ rawUrl, prepUrl, gradcamUrl }) {
  const [viewMode, setViewMode] = useState('gradcam'); // 'gradcam', 'side', 'clahe'
  const [alpha, setAlpha] = useState(50);

  return (
    <div className="bg-white rounded-xl shadow-sm border border-slate-200 p-4 space-y-3">
      <div className="flex items-center justify-between border-b border-slate-100 pb-2.5">
        <div className="flex items-center space-x-2">
          <span className="font-bold text-xs text-slate-700">Display Mode:</span>
          <div className="inline-flex rounded-md shadow-sm">
            <button
              onClick={() => setViewMode('gradcam')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-l-lg ${
                viewMode === 'gradcam' ? 'bg-sky-600 text-white' : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              Grad-CAM Overlay
            </button>
            <button
              onClick={() => setViewMode('side')}
              className={`px-2.5 py-1 text-xs font-semibold ${
                viewMode === 'side' ? 'bg-sky-600 text-white' : 'bg-white text-slate-700 hover:bg-slate-50 border-t border-b border-slate-200'
              }`}
            >
              Side-by-Side
            </button>
            <button
              onClick={() => setViewMode('clahe')}
              className={`px-2.5 py-1 text-xs font-semibold rounded-r-lg ${
                viewMode === 'clahe' ? 'bg-sky-600 text-white' : 'bg-white text-slate-700 hover:bg-slate-50 border border-slate-200'
              }`}
            >
              Green CLAHE
            </button>
          </div>
        </div>

        {viewMode === 'gradcam' && (
          <div className="flex items-center space-x-2">
            <span className="text-[11px] font-semibold text-slate-500">Heatmap Alpha:</span>
            <input
              type="range"
              min="0"
              max="100"
              value={alpha}
              onChange={(e) => setAlpha(e.target.value)}
              className="w-20 h-1.5 bg-slate-200 rounded-lg appearance-none cursor-pointer accent-sky-600"
            />
            <span className="text-[11px] font-bold text-slate-600">{alpha}%</span>
          </div>
        )}
      </div>

      {/* Stage */}
      <div className="relative rounded-lg overflow-hidden bg-black flex items-center justify-center min-h-[300px]">
        {viewMode === 'gradcam' && (
          <div className="relative w-full max-w-[420px] aspect-square mx-auto">
            <img src={rawUrl} alt="Base Fundus" className="absolute inset-0 w-full h-full object-contain" />
            <img
              src={gradcamUrl}
              alt="GradCAM Overlay"
              style={{ opacity: alpha / 100 }}
              className="absolute inset-0 w-full h-full object-contain mix-blend-screen transition-opacity"
            />
          </div>
        )}

        {viewMode === 'side' && (
          <div className="grid grid-cols-2 gap-2 w-full p-2">
            <div className="text-center space-y-1">
              <img src={rawUrl} alt="Raw" className="w-full aspect-square object-contain bg-slate-900 rounded" />
              <span className="text-[10px] text-slate-300 font-semibold">Raw Fundus Photo</span>
            </div>
            <div className="text-center space-y-1">
              <img src={gradcamUrl} alt="GradCAM" className="w-full aspect-square object-contain bg-slate-900 rounded" />
              <span className="text-[10px] text-amber-300 font-semibold">Grad-CAM Attention Heatmap</span>
            </div>
          </div>
        )}

        {viewMode === 'clahe' && (
          <div className="relative w-full max-w-[420px] aspect-square mx-auto">
            <img src={prepUrl} alt="Green CLAHE" className="w-full h-full object-contain" />
          </div>
        )}
      </div>
    </div>
  );
}
