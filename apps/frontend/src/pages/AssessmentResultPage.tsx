import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { MapPin, CloudRain, Car, ShieldAlert, CheckCircle2, AlertTriangle, FileText, ArrowLeft, ExternalLink, Calendar } from 'lucide-react';
import * as api from '../services/api';
import { Assessment } from '../types';
import { BoundingBoxViewer } from '../components/BoundingBoxViewer';

export const AssessmentResultPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (id) {
      loadAssessment(id);
    }
  }, [id]);

  const loadAssessment = async (assessmentId: string) => {
    try {
      setLoading(true);
      const data = await api.getAssessmentDetails(assessmentId);
      setAssessment(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load assessment details.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-4xl mx-auto py-16 text-center space-y-4">
        <div className="w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto" />
        <p className="text-sm text-slate-400">Loading grounded road assessment report...</p>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="max-w-xl mx-auto py-16 text-center space-y-4 px-4">
        <div className="p-4 bg-rose-500/10 border border-rose-500/30 rounded-2xl text-rose-300 text-sm">
          {error || 'Assessment not found'}
        </div>
        <Link to="/dashboard" className="text-xs text-blue-400 hover:underline inline-flex items-center space-x-1">
          <ArrowLeft className="w-3.5 h-3.5" />
          <span>Return to Dashboard</span>
        </Link>
      </div>
    );
  }

  const totalDetections = assessment.images.reduce((sum, img) => sum + img.detections.length, 0);

  return (
    <div className="max-w-5xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 border-b border-slate-800 pb-6">
        <div>
          <div className="flex items-center space-x-2">
            <span className="px-3 py-1 bg-blue-600/20 border border-blue-500/30 text-blue-400 text-xs font-bold rounded-full">
              {assessment.rag?.ragMode || 'EVIDENCE_AWARE_ADAPTIVE_RAG'}
            </span>
            <span className="text-xs text-slate-400 flex items-center space-x-1">
              <Calendar className="w-3.5 h-3.5" />
              <span>{new Date(assessment.createdAt).toLocaleString()}</span>
            </span>
          </div>
          <h1 className="text-2xl font-extrabold text-white mt-2">
            Assessment #{assessment.assessmentId}
          </h1>
        </div>

        <div className="flex items-center space-x-3">
          <Link
            to={`/ask?assessmentId=${assessment.assessmentId}`}
            className="px-4 py-2 bg-slate-800 hover:bg-slate-700 text-white rounded-xl text-xs font-bold border border-slate-700 transition flex items-center space-x-1.5"
          >
            <span>Ask RoadSense AI</span>
          </Link>
          <button
            onClick={() => window.print()}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-500 text-white rounded-xl text-xs font-bold transition flex items-center space-x-1.5 shadow-lg shadow-blue-600/20"
          >
            <FileText className="w-4 h-4" />
            <span>Print / PDF Report</span>
          </button>
        </div>
      </div>

      {/* Grid Summary Cards */}
      <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <p className="text-[11px] font-semibold uppercase text-slate-400">Total Detections</p>
          <p className="text-2xl font-bold text-white">{totalDetections}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <p className="text-[11px] font-semibold uppercase text-slate-400">Images Evaluated</p>
          <p className="text-2xl font-bold text-cyan-400">{assessment.images.length}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <p className="text-[11px] font-semibold uppercase text-slate-400">Location</p>
          <p className="text-sm font-bold text-white truncate">{assessment.location?.road || 'Corridor'}</p>
        </div>

        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-1">
          <p className="text-[11px] font-semibold uppercase text-slate-400">Citations Cited</p>
          <p className="text-2xl font-bold text-emerald-400">{assessment.rag?.citations?.length || 0}</p>
        </div>
      </div>

      {/* Detection Results & Images */}
      <div className="space-y-6">
        <h2 className="text-lg font-bold text-white flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-blue-400" />
          <span>Observed Road Damage Imagery ({assessment.images.length})</span>
        </h2>

        <div className="grid md:grid-cols-2 gap-6">
          {assessment.images.map((img, idx) => (
            <div key={idx} className="bg-slate-900 border border-slate-800 rounded-2xl p-4 space-y-3">
              <div className="flex items-center justify-between text-xs text-slate-400">
                <span className="font-semibold text-slate-300">Image #{idx + 1}: {img.filename}</span>
                <span>{img.detections.length} Detection(s)</span>
              </div>
              <BoundingBoxViewer
                imageUrl={img.storagePath}
                detections={img.detections}
                width={img.width}
                height={img.height}
              />
            </div>
          ))}
        </div>
      </div>

      {/* Context Panels: Location, Weather, Traffic */}
      <div className="grid md:grid-cols-3 gap-6">
        {/* Location Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-blue-400 font-bold text-sm">
            <MapPin className="w-4 h-4" />
            <span>Location Context (OSM)</span>
          </div>
          <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
            <p><strong className="text-slate-400">Road:</strong> {assessment.location?.road}</p>
            <p><strong className="text-slate-400">Type:</strong> {assessment.location?.roadType}</p>
            <p className="truncate"><strong className="text-slate-400">Address:</strong> {assessment.location?.address}</p>
            {assessment.location?.nearbyInfrastructure?.map((fac, i) => (
              <p key={i} className="text-[11px] text-slate-400">
                • {fac.type}: <span className="text-slate-200">{fac.name}</span> (~{fac.distanceMeters}m)
              </p>
            ))}
          </div>
        </div>

        {/* Weather Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-cyan-400 font-bold text-sm">
            <CloudRain className="w-4 h-4" />
            <span>Weather Context (Open-Meteo)</span>
          </div>
          <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
            <p><strong className="text-slate-400">Historical 7-Day:</strong> {assessment.weather?.historical7Days?.length || 0} days recorded</p>
            <p><strong className="text-slate-400">Forecast 7-Day:</strong> {assessment.weather?.forecast7Days?.length || 0} days forecast</p>
            <p className="text-[11px] text-slate-400 mt-1 italic">{assessment.weather?.environmentalNote}</p>
          </div>
        </div>

        {/* Traffic Panel */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 space-y-3">
          <div className="flex items-center space-x-2 text-amber-400 font-bold text-sm">
            <Car className="w-4 h-4" />
            <span>Traffic Context (Google Routes)</span>
          </div>
          <div className="text-xs text-slate-300 space-y-1.5 leading-relaxed">
            <p><strong className="text-slate-400">Volume Category:</strong> {assessment.traffic?.trafficVolumeLevel || 'Moderate'}</p>
            <p><strong className="text-slate-400">Traffic Delay:</strong> {assessment.traffic?.trafficDelaySeconds || 0} seconds</p>
            <p className="text-[11px] text-slate-400 mt-1 italic">{assessment.traffic?.operationalNote}</p>
          </div>
        </div>
      </div>

      {/* Engineering Grounded Assessment Report */}
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-8 space-y-6">
        <h2 className="text-xl font-bold text-white flex items-center space-x-2 border-b border-slate-800 pb-4">
          <FileText className="w-6 h-6 text-blue-400" />
          <span>Grounded Engineering Assessment Report</span>
        </h2>

        <div className="prose prose-invert max-w-none text-slate-300 text-sm leading-relaxed whitespace-pre-wrap">
          {assessment.rag?.report}
        </div>

        {/* Citations List */}
        {assessment.rag?.citations && assessment.rag.citations.length > 0 && (
          <div className="border-t border-slate-800 pt-6 space-y-3">
            <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
              Evidence Citations & Provenance
            </h3>
            <div className="grid sm:grid-cols-2 gap-3">
              {assessment.rag.citations.map((cite, i) => (
                <div key={i} className="bg-slate-950 border border-slate-800 rounded-xl p-3 text-xs space-y-1">
                  <p className="font-bold text-blue-400">{cite.title}</p>
                  <p className="text-slate-400">Source ID: {cite.sourceId} | Page: {cite.page}</p>
                  <p className="text-[10px] text-slate-400 font-mono">Chunk: {cite.chunkId}</p>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Explicit Uncertainties */}
        {assessment.rag?.uncertainties && assessment.rag.uncertainties.length > 0 && (
          <div className="bg-amber-500/10 border border-amber-500/30 rounded-xl p-4 space-y-2 text-xs">
            <div className="flex items-center space-x-2 text-amber-400 font-bold">
              <AlertTriangle className="w-4 h-4" />
              <span>Explicit Assessment Limitations & Boundaries</span>
            </div>
            <ul className="list-disc list-inside space-y-1 text-slate-300">
              {assessment.rag.uncertainties.map((unc, i) => (
                <li key={i}>{unc}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
    </div>
  );
};
