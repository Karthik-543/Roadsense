import React, { useEffect, useState } from 'react';
import { useParams, Link, useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  MapPin, 
  Calendar, 
  AlertTriangle, 
  CloudRain, 
  Car, 
  FileText, 
  BookOpen, 
  Upload, 
  MessageSquare, 
  Printer, 
  CheckCircle2, 
  HelpCircle, 
  Layers, 
  ExternalLink,
  Info,
  Clock
} from 'lucide-react';
import { getAssessmentDetails, addAdditionalImage } from '../services/api';
import { Assessment } from '../types';
import { BoundingBoxViewer } from '../components/BoundingBoxViewer';

export const AssessmentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [isUploading, setIsUploading] = useState(false);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'environment' | 'rag' | 'citations'>('overview');

  const fetchDetails = async () => {
    if (!id) return;
    setLoading(true);
    setError(null);
    try {
      const data = await getAssessmentDetails(id);
      setAssessment(data);
    } catch (err: any) {
      setError(err.message || 'Failed to fetch assessment details');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDetails();
  }, [id]);

  const handleAddImage = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (!e.target.files || e.target.files.length === 0 || !assessment) return;
    const file = e.target.files[0];
    setIsUploading(true);
    setUploadError(null);

    try {
      const updated = await addAdditionalImage(assessment.assessmentId || assessment.id, file);
      setAssessment(updated);
      setSelectedImageIndex((updated.images?.length || 1) - 1);
    } catch (err: any) {
      setUploadError(err.message || 'Failed to upload additional image');
    } finally {
      setIsUploading(false);
    }
  };

  if (loading) {
    return (
      <div className="max-w-7xl mx-auto px-4 py-16 text-center">
        <div className="animate-spin w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4"></div>
        <p className="text-slate-600 font-medium">Loading Road Assessment Data...</p>
      </div>
    );
  }

  if (error || !assessment) {
    return (
      <div className="max-w-4xl mx-auto px-4 py-16 text-center space-y-4">
        <div className="w-16 h-16 bg-red-100 text-red-600 rounded-full flex items-center justify-center mx-auto">
          <AlertTriangle className="w-8 h-8" />
        </div>
        <h2 className="text-2xl font-bold text-slate-900">Assessment Not Found</h2>
        <p className="text-slate-600">{error || 'The requested assessment could not be retrieved.'}</p>
        <Link
          to="/dashboard"
          className="inline-flex items-center gap-2 px-5 py-2.5 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition"
        >
          <ArrowLeft className="w-4 h-4" />
          Back to Dashboard
        </Link>
      </div>
    );
  }

  const currentImage = assessment.images?.[selectedImageIndex] || assessment.images?.[0];
  const allDetections = assessment.images?.flatMap(img => img.detections || []) || [];

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Top Bar */}
      <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
        <div className="flex items-center gap-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="p-2 border border-slate-200 text-slate-600 hover:bg-slate-50 rounded-lg transition"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          <div>
            <div className="flex items-center gap-3">
              <h1 className="text-2xl font-extrabold text-slate-900">
                Assessment #{assessment.assessmentId || assessment.id}
              </h1>
              <span className="px-2.5 py-1 text-xs font-semibold rounded-full bg-emerald-100 text-emerald-800">
                Verified Report
              </span>
            </div>
            <p className="text-sm text-slate-500 flex items-center gap-4 mt-1">
              <span className="flex items-center gap-1">
                <Calendar className="w-4 h-4 text-slate-400" />
                {assessment.createdAt ? new Date(assessment.createdAt).toLocaleString() : 'N/A'}
              </span>
              <span className="flex items-center gap-1">
                <MapPin className="w-4 h-4 text-rose-500" />
                {assessment.location?.road || assessment.location?.address || 'Recorded Location'}
              </span>
            </p>
          </div>
        </div>

        <div className="flex items-center gap-3 print:hidden">
          <button
            onClick={() => window.print()}
            className="px-4 py-2 border border-slate-200 text-slate-700 hover:bg-slate-50 font-medium rounded-lg text-sm transition flex items-center gap-2"
          >
            <Printer className="w-4 h-4" />
            Print Report
          </button>
          <Link
            to={`/ask?assessmentId=${assessment.assessmentId || assessment.id}`}
            className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg text-sm transition flex items-center gap-2 shadow-sm"
          >
            <MessageSquare className="w-4 h-4" />
            Ask AI Assistant
          </Link>
        </div>
      </div>

      {/* Main Grid: Left BoundingBox / Image Viewer, Right Overview / Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
        {/* Left Column: Image & Detections (7 cols) */}
        <div className="lg:col-span-7 space-y-6">
          <div className="bg-white rounded-xl border border-slate-200 p-4 shadow-sm space-y-4">
            <div className="flex items-center justify-between pb-3 border-b border-slate-100">
              <h3 className="font-bold text-slate-900 flex items-center gap-2 text-base">
                <Layers className="w-5 h-5 text-blue-600" />
                RF-DETR Visual Damage Detection
              </h3>
              <span className="text-xs text-slate-500 font-medium">
                {currentImage ? `${currentImage.width} × ${currentImage.height} px` : ''}
              </span>
            </div>

            {/* Bounding Box Viewer */}
            {currentImage ? (
              <BoundingBoxViewer
                imageUrl={`/api/files/${currentImage.storagePath.split('/').pop()}`}
                detections={currentImage.detections || []}
                imageWidth={currentImage.width}
                imageHeight={currentImage.height}
              />
            ) : (
              <div className="p-8 text-center text-slate-400">No image data available</div>
            )}

            {/* Thumbnails & Upload Multi-view */}
            <div className="flex items-center gap-3 pt-2 overflow-x-auto print:hidden">
              {assessment.images?.map((img, idx) => (
                <button
                  key={img.imageId || idx}
                  onClick={() => setSelectedImageIndex(idx)}
                  className={`w-16 h-16 rounded-lg overflow-hidden border-2 transition relative flex-shrink-0 ${
                    selectedImageIndex === idx ? 'border-blue-600 shadow-md' : 'border-slate-200 opacity-70 hover:opacity-100'
                  }`}
                >
                  <img
                    src={`/api/files/${img.storagePath.split('/').pop()}`}
                    alt={`View ${idx + 1}`}
                    className="w-full h-full object-cover"
                  />
                  <span className="absolute bottom-0 right-0 bg-slate-900/80 text-white text-[10px] px-1 font-mono">
                    #{idx + 1}
                  </span>
                </button>
              ))}

              <label className="w-16 h-16 rounded-lg border-2 border-dashed border-slate-300 hover:border-blue-500 flex flex-col items-center justify-center text-slate-400 hover:text-blue-600 cursor-pointer transition flex-shrink-0 bg-slate-50">
                <Upload className="w-5 h-5" />
                <span className="text-[9px] font-semibold mt-1">Add Image</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAddImage}
                  disabled={isUploading}
                  className="hidden"
                />
              </label>
            </div>

            {uploadError && (
              <div className="text-xs text-red-600 font-medium bg-red-50 p-2.5 rounded border border-red-200">
                {uploadError}
              </div>
            )}
          </div>

          {/* Detections Breakdown Table */}
          <div className="bg-white rounded-xl border border-slate-200 p-5 shadow-sm space-y-4">
            <h3 className="font-bold text-slate-900 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-500" />
              Detected Defects Log ({allDetections.length})
            </h3>

            {allDetections.length === 0 ? (
              <div className="text-sm text-slate-500 italic p-4 bg-slate-50 rounded-lg text-center">
                No damages were detected above confidence threshold 0.30.
              </div>
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm text-slate-700">
                  <thead className="bg-slate-50 text-slate-500 text-xs font-semibold uppercase border-b border-slate-200">
                    <tr>
                      <th className="py-2.5 px-3">Class</th>
                      <th className="py-2.5 px-3">Damage Type</th>
                      <th className="py-2.5 px-3">Confidence</th>
                      <th className="py-2.5 px-3">Bounding Box [ymin, xmin, ymax, xmax]</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100">
                    {allDetections.map((d, i) => (
                      <tr key={i} className="hover:bg-slate-50">
                        <td className="py-2.5 px-3 font-mono text-xs text-slate-500">ID #{d.classId}</td>
                        <td className="py-2.5 px-3 font-semibold text-slate-900 capitalize">
                          {d.damageType.replace('_', ' ')}
                        </td>
                        <td className="py-2.5 px-3">
                          <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-bold bg-blue-50 text-blue-700 border border-blue-200">
                            {(d.confidence * 100).toFixed(1)}%
                          </span>
                        </td>
                        <td className="py-2.5 px-3 font-mono text-xs text-slate-500">
                          [{d.boundingBox?.map(n => Math.round(n)).join(', ')}]
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right Column: Context & RAG Details (5 cols) */}
        <div className="lg:col-span-5 space-y-6">
          {/* Navigation Tabs */}
          <div className="flex border-b border-slate-200 text-sm font-medium gap-2">
            <button
              onClick={() => setActiveTab('overview')}
              className={`pb-3 border-b-2 font-semibold transition ${
                activeTab === 'overview'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              Overview
            </button>
            <button
              onClick={() => setActiveTab('environment')}
              className={`pb-3 border-b-2 font-semibold transition ${
                activeTab === 'environment'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              Environment Context
            </button>
            <button
              onClick={() => setActiveTab('rag')}
              className={`pb-3 border-b-2 font-semibold transition ${
                activeTab === 'rag'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              RAG Decision Report
            </button>
            <button
              onClick={() => setActiveTab('citations')}
              className={`pb-3 border-b-2 font-semibold transition ${
                activeTab === 'citations'
                  ? 'border-blue-600 text-blue-600'
                  : 'border-transparent text-slate-500 hover:text-slate-800'
              }`}
            >
              Citations ({assessment.rag?.citations?.length || 0})
            </button>
          </div>

          {/* TAB 1: OVERVIEW */}
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Executive Summary Card */}
              <div className="bg-gradient-to-br from-blue-900 to-slate-900 text-white p-6 rounded-xl shadow-md space-y-3">
                <div className="flex items-center justify-between text-blue-300 text-xs font-semibold uppercase tracking-wider">
                  <span>Executive Engineering Summary</span>
                  <span>{assessment.rag?.ragMode || 'ADAPTIVE RAG'}</span>
                </div>
                <p className="text-sm leading-relaxed font-light text-slate-100">
                  {assessment.rag?.executiveSummary || 'Assessment completed successfully. Detailed maintenance plan generated based on multi-source context synthesis.'}
                </p>
              </div>

              {/* Recommended Actions */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                  Recommended Repairs & Actions
                </h4>
                {assessment.rag?.recommendations && assessment.rag.recommendations.length > 0 ? (
                  <ul className="space-y-2 text-xs text-slate-700">
                    {assessment.rag.recommendations.map((rec, i) => (
                      <li key={i} className="flex items-start gap-2 bg-emerald-50/50 p-2.5 rounded border border-emerald-100">
                        <span className="w-5 h-5 rounded-full bg-emerald-100 text-emerald-800 flex items-center justify-center text-[10px] font-bold shrink-0 mt-0.5">
                          {i + 1}
                        </span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-xs text-slate-500 italic">No specific recommendations logged.</p>
                )}
              </div>

              {/* Uncertainties & Verification */}
              {assessment.rag?.uncertainties && assessment.rag.uncertainties.length > 0 && (
                <div className="bg-amber-50 p-5 rounded-xl border border-amber-200 shadow-sm space-y-3">
                  <h4 className="font-bold text-amber-900 text-sm flex items-center gap-2">
                    <HelpCircle className="w-4 h-4 text-amber-600" />
                    Uncertainties & Boundary Conditions
                  </h4>
                  <ul className="space-y-1.5 text-xs text-amber-800 list-disc list-inside">
                    {assessment.rag.uncertainties.map((u, i) => (
                      <li key={i}>{u}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}

          {/* TAB 2: ENVIRONMENT CONTEXT */}
          {activeTab === 'environment' && (
            <div className="space-y-6">
              {/* Location Context */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <MapPin className="w-4 h-4 text-rose-500" />
                  OSM & Overpass Location Context
                </h4>
                <div className="space-y-2 text-xs text-slate-700">
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Road Corridor:</span>
                    <span className="font-semibold text-slate-900">{assessment.location?.road || 'N/A'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Road Type:</span>
                    <span className="font-semibold text-slate-900 capitalize">{assessment.location?.roadType || 'Highway'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Coordinates:</span>
                    <span className="font-mono text-slate-900">
                      {assessment.location?.latitude?.toFixed(5)}, {assessment.location?.longitude?.toFixed(5)}
                    </span>
                  </div>
                </div>

                {assessment.location?.nearbyInfrastructure && assessment.location.nearbyInfrastructure.length > 0 && (
                  <div className="pt-2">
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                      Nearby Infrastructure
                    </div>
                    <div className="space-y-1">
                      {assessment.location.nearbyInfrastructure.map((fac, idx) => (
                        <div key={idx} className="flex justify-between text-xs bg-slate-50 p-2 rounded">
                          <span className="capitalize font-medium text-slate-800">{fac.name || fac.type}</span>
                          <span className="text-slate-500 font-mono">{fac.distanceMeters} m</span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Weather Context */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <CloudRain className="w-4 h-4 text-blue-500" />
                  Open-Meteo Weather Impact Analysis
                </h4>
                <p className="text-xs text-slate-600">
                  {assessment.weather?.environmentalNote || 'Subsurface moisture and rainfall history directly influence freeze-thaw cycles and structural deterioration rates.'}
                </p>

                {assessment.weather?.historical7Days && assessment.weather.historical7Days.length > 0 && (
                  <div className="pt-2 space-y-2">
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider">
                      7-Day Precipitation History & Forecast
                    </div>
                    <div className="grid grid-cols-7 gap-1 text-center">
                      {assessment.weather.historical7Days.slice(-7).map((d, i) => (
                        <div key={i} className="bg-blue-50/60 p-1.5 rounded text-[10px]">
                          <div className="text-slate-500 font-medium">{d.date?.slice(5)}</div>
                          <div className="font-bold text-blue-700 mt-1">{d.precipitationMm} mm</div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>

              {/* Traffic Context */}
              <div className="bg-white p-5 rounded-xl border border-slate-200 shadow-sm space-y-3">
                <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                  <Car className="w-4 h-4 text-indigo-500" />
                  Google Routes Traffic Congestion
                </h4>
                <div className="space-y-2 text-xs text-slate-700">
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Volume Level:</span>
                    <span className="font-bold text-indigo-700">{assessment.traffic?.trafficVolumeLevel || 'MODERATE'}</span>
                  </div>
                  <div className="flex justify-between py-1 border-b border-slate-100">
                    <span className="text-slate-500">Traffic Delay:</span>
                    <span className="font-mono text-slate-900">
                      {assessment.traffic?.trafficDelaySeconds ? `${Math.round(assessment.traffic.trafficDelaySeconds / 60)} mins` : 'Minimal'}
                    </span>
                  </div>
                  {assessment.traffic?.operationalNote && (
                    <p className="text-xs text-slate-600 pt-1 italic">
                      "{assessment.traffic.operationalNote}"
                    </p>
                  )}
                </div>
              </div>
            </div>
          )}

          {/* TAB 3: RAG DECISION REPORT */}
          {activeTab === 'rag' && (
            <div className="space-y-6">
              <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
                <div className="flex items-center justify-between pb-3 border-b border-slate-100">
                  <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                    <FileText className="w-4 h-4 text-blue-600" />
                    Evidence-Aware Engineering Synthesis
                  </h4>
                  {assessment.rag?.latencyMs && (
                    <span className="text-xs text-slate-400 flex items-center gap-1">
                      <Clock className="w-3 h-3" />
                      {assessment.rag.latencyMs} ms
                    </span>
                  )}
                </div>

                <div className="prose prose-sm text-slate-800 max-w-none text-xs leading-relaxed space-y-3">
                  <h5 className="font-bold text-slate-900 text-sm">Engineering Assessment Details</h5>
                  <p className="whitespace-pre-line text-slate-700 bg-slate-50 p-4 rounded-lg border border-slate-100 font-mono text-[11px]">
                    {assessment.rag?.engineeringAssessment || assessment.rag?.report || 'No detailed engineering text logged.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* TAB 4: CITATIONS & SOURCES */}
          {activeTab === 'citations' && (
            <div className="space-y-4">
              <h4 className="font-bold text-slate-900 text-sm flex items-center gap-2">
                <BookOpen className="w-4 h-4 text-purple-600" />
                Civil Engineering Standards & Manuals ({assessment.rag?.citations?.length || 0})
              </h4>

              {assessment.rag?.citations && assessment.rag.citations.length > 0 ? (
                <div className="space-y-3">
                  {assessment.rag.citations.map((cit, idx) => (
                    <div key={idx} className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm space-y-1 hover:border-purple-300 transition">
                      <div className="flex items-center justify-between text-xs">
                        <span className="font-bold text-purple-700 bg-purple-50 px-2 py-0.5 rounded border border-purple-100">
                          [{cit.sourceId || idx + 1}]
                        </span>
                        <span className="text-slate-400 font-mono text-[10px]">Page {cit.page || 1}</span>
                      </div>
                      <h5 className="font-semibold text-slate-900 text-xs">{cit.title || 'Road Infrastructure Standard'}</h5>
                      <div className="text-[10px] font-mono text-slate-400 truncate">Chunk: {cit.chunkId}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-xs text-slate-500 italic p-6 bg-slate-50 rounded-xl text-center border border-slate-200">
                  No explicit standard citations attached.
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
