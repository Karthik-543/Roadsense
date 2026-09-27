import React from 'react';
import { Link } from 'react-router-dom';
import { ShieldAlert, PlusCircle, MessageSquare, Cpu, Database, CheckCircle2, FileText } from 'lucide-react';

export const HomePage: React.FC = () => {
  return (
    <div className="space-y-16 pb-16">
      {/* Hero Section */}
      <section className="relative overflow-hidden pt-12 pb-16 px-4 sm:px-6 lg:px-8 max-w-7xl mx-auto text-center">
        <div className="inline-flex items-center space-x-2 px-3 py-1 bg-blue-500/10 border border-blue-500/30 rounded-full text-xs font-semibold text-blue-400 mb-6">
          <Cpu className="w-3.5 h-3.5" />
          <span>Evidence-Aware Adaptive RAG Subsystem Active</span>
        </div>

        <h1 className="text-4xl sm:text-6xl font-extrabold text-white tracking-tight leading-tight max-w-4xl mx-auto">
          AI-Powered Road Damage Assessment & Decision Support
        </h1>

        <p className="mt-6 text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed">
          RoadSense AI integrates RF-DETR computer vision damage detection with spatial, environmental, and traffic operational contexts to deliver grounded engineering assessments and verifiable citation provenance.
        </p>

        <div className="mt-8 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/report"
            className="w-full sm:w-auto px-8 py-4 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl shadow-xl shadow-blue-600/30 transition flex items-center justify-center space-x-3 text-base"
          >
            <PlusCircle className="w-5 h-5" />
            <span>Report Road Damage</span>
          </Link>

          <Link
            to="/ask"
            className="w-full sm:w-auto px-8 py-4 bg-slate-800 hover:bg-slate-700 text-white font-semibold rounded-xl border border-slate-700 transition flex items-center justify-center space-x-3 text-base"
          >
            <MessageSquare className="w-5 h-5 text-cyan-400" />
            <span>Ask RoadSense AI</span>
          </Link>
        </div>

        <div className="mt-12 bg-slate-900/60 border border-slate-800 rounded-2xl p-4 max-w-3xl mx-auto text-xs text-slate-400 leading-relaxed">
          <span className="font-bold text-slate-300">Research Disclaimer:</span> RoadSense AI is an AI-powered research prototype. It does not replace formal municipal engineering inspections or guarantee physical repairs.
        </div>
      </section>

      {/* Core Technical Pillars */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <h2 className="text-2xl font-bold text-white text-center mb-8">
          Evidence-Aware Infrastructure Engineering Pipeline
        </h2>

        <div className="grid md:grid-cols-3 gap-8">
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="w-12 h-12 bg-blue-600/20 border border-blue-500/30 rounded-xl flex items-center justify-center text-blue-400">
              <Cpu className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">RF-DETR Medium Detection</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Fine-tuned Transformer detection architecture classifying longitudinal cracks, transverse cracks, alligator cracks, and potholes with bounding box bounding box localization.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="w-12 h-12 bg-cyan-600/20 border border-cyan-500/30 rounded-xl flex items-center justify-center text-cyan-400">
              <Database className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Multi-Source Context Integration</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Synthesizes OpenStreetMap mapped infrastructure, Open-Meteo 7-day precipitation, and Google Routes API traffic-aware congestion metrics.
            </p>
          </div>

          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="w-12 h-12 bg-emerald-600/20 border border-emerald-500/30 rounded-xl flex items-center justify-center text-emerald-400">
              <CheckCircle2 className="w-6 h-6" />
            </div>
            <h3 className="text-lg font-bold text-white">Grounded Citation Provenance</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Performs evidence evaluation, claim verification against 18 MoRTH/NHAI/IRC standard documents, and attaches page-level inline citations.
            </p>
          </div>
        </div>
      </section>
    </div>
  );
};
