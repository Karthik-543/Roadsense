import React from 'react';
import { Loader2, CheckCircle2 } from 'lucide-react';

interface ProcessingOverlayProps {
  currentStage: number;
}

const STAGES = [
  'Uploading images',
  'Detecting road damage (RF-DETR Medium)',
  'Analyzing location context (OpenStreetMap)',
  'Collecting weather context (Open-Meteo)',
  'Analyzing traffic context (Google Routes API)',
  'Retrieving engineering evidence (ChromaDB Vector RAG)',
  'Verifying claims & citation provenance',
  'Generating grounded road assessment report',
];

export const ProcessingOverlay: React.FC<ProcessingOverlayProps> = ({ currentStage }) => {
  return (
    <div className="fixed inset-0 bg-slate-950/80 backdrop-blur-md z-50 flex items-center justify-center p-4">
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 max-w-lg w-full shadow-2xl space-y-6">
        <div className="text-center space-y-2">
          <div className="w-12 h-12 bg-blue-600/20 border border-blue-500/30 rounded-xl flex items-center justify-center mx-auto text-blue-400">
            <Loader2 className="w-6 h-6 animate-spin" />
          </div>
          <h3 className="text-lg font-bold text-white">AI Assessment Pipeline In Progress</h3>
          <p className="text-xs text-slate-400">
            Executing evidence-aware analysis combining visual detection and multi-source context.
          </p>
        </div>

        <div className="space-y-3">
          {STAGES.map((stage, idx) => {
            const isDone = idx < currentStage;
            const isCurrent = idx === currentStage;

            return (
              <div
                key={idx}
                className={`flex items-center space-x-3 p-2.5 rounded-lg border text-sm transition-all ${
                  isDone
                    ? 'bg-slate-800/40 border-slate-700/60 text-slate-300'
                    : isCurrent
                    ? 'bg-blue-600/10 border-blue-500/40 text-blue-300 shadow'
                    : 'bg-slate-900/40 border-slate-800/40 text-slate-400 opacity-40'
                }`}
              >
                {isDone ? (
                  <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />
                ) : isCurrent ? (
                  <Loader2 className="w-4 h-4 text-blue-400 animate-spin flex-shrink-0" />
                ) : (
                  <div className="w-4 h-4 rounded-full border border-slate-700 flex-shrink-0" />
                )}
                <span className="font-medium text-xs">{stage}</span>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
