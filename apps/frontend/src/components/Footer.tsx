import React from 'react';

export const Footer: React.FC = () => {
  return (
    <footer className="bg-slate-950 border-t border-slate-800/80 py-8 px-4 sm:px-6 lg:px-8 mt-auto">
      <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4 text-xs text-slate-400">
        <div>
          <p className="font-semibold text-slate-300">
            RoadSense AI — Evidence-Aware Adaptive RAG Subsystem
          </p>
          <p className="mt-1 text-slate-400 max-w-2xl">
            <strong>Important Product Positioning:</strong> RoadSense AI is an AI-powered road damage assessment
            and decision-support research prototype. It is NOT an official municipal complaint system or government entity.
            All assessments provide evidence-grounded technical recommendations without implying guaranteed repairs.
          </p>
        </div>

        <div className="text-right">
          <p>Powered by RF-DETR Medium & ChromaDB RAG</p>
          <p className="mt-1 text-slate-400">© 2026 RoadSense AI Research Project</p>
        </div>
      </div>
    </footer>
  );
};
