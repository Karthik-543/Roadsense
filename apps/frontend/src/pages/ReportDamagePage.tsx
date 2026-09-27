import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Upload, MapPin, Camera, Image as ImageIcon, PlusCircle, ArrowRight, AlertCircle } from 'lucide-react';
import * as api from '../services/api';
import { Assessment } from '../types';
import { BoundingBoxViewer } from '../components/BoundingBoxViewer';
import { ProcessingOverlay } from '../components/ProcessingOverlay';

export const ReportDamagePage: React.FC = () => {
  const navigate = useNavigate();

  const [firstFile, setFirstFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  const [latitude, setLatitude] = useState<number | null>(null);
  const [longitude, setLongitude] = useState<number | null>(null);
  const [locating, setLocating] = useState<boolean>(false);

  const [assessment, setAssessment] = useState<Assessment | null>(null);
  const [processing, setProcessing] = useState<boolean>(false);
  const [currentStage, setCurrentStage] = useState<number>(0);

  const [showAdditionalPrompt, setShowAdditionalPrompt] = useState<boolean>(false);
  const [additionalFiles, setAdditionalFiles] = useState<File[]>([]);
  const [uploadingAdditional, setUploadingAdditional] = useState<boolean>(false);

  const [error, setError] = useState<string | null>(null);

  // Auto capture GPS on mount
  useEffect(() => {
    handleGetLocation();
  }, []);

  const handleGetLocation = () => {
    if ('geolocation' in navigator) {
      setLocating(true);
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          setLatitude(pos.coords.latitude);
          setLongitude(pos.coords.longitude);
          setLocating(false);
        },
        (err) => {
          console.warn('Geolocation error:', err);
          // Default fallback coordinates (e.g. Bangalore Corridor)
          setLatitude(12.9716);
          setLongitude(77.5946);
          setLocating(false);
        },
        { timeout: 10000 }
      );
    } else {
      setLatitude(12.9716);
      setLongitude(77.5946);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0];
      setFirstFile(file);
      setPreviewUrl(URL.createObjectURL(file));
      setError(null);
    }
  };

  const handleSubmitInitial = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!firstFile) {
      setError('Please select or capture a road damage image.');
      return;
    }

    setError(null);
    setProcessing(true);
    setCurrentStage(0);

    try {
      // Stage animation simulation
      const timer1 = setTimeout(() => setCurrentStage(1), 800);
      const timer2 = setTimeout(() => setCurrentStage(2), 1600);
      const timer3 = setTimeout(() => setCurrentStage(3), 2400);

      const res = await api.createAssessment(firstFile, latitude, longitude, 0.3);

      clearTimeout(timer1);
      clearTimeout(timer2);
      clearTimeout(timer3);

      setCurrentStage(7);
      setAssessment(res);
      setProcessing(false);
      setShowAdditionalPrompt(true);
    } catch (err: any) {
      setProcessing(false);
      setError(err.message || 'Failed to process road damage assessment.');
    }
  };

  const handleAddAdditionalFile = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0] && assessment) {
      const file = e.target.files[0];
      setUploadingAdditional(true);
      try {
        const updated = await api.addAdditionalImage(assessment.assessmentId, file, 0.3);
        setAssessment(updated);
        setAdditionalFiles((prev) => [...prev, file]);
      } catch (err: any) {
        setError(err.message || 'Failed to upload additional image');
      } finally {
        setUploadingAdditional(false);
      }
    }
  };

  const handleFinishAssessment = () => {
    if (assessment) {
      navigate(`/assessment/${assessment.assessmentId}`);
    }
  };

  return (
    <div className="max-w-4xl mx-auto py-8 px-4 sm:px-6 lg:px-8 space-y-8">
      {processing && <ProcessingOverlay currentStage={currentStage} />}

      <div className="text-center space-y-2">
        <h1 className="text-3xl font-extrabold text-white">Report Road Damage</h1>
        <p className="text-xs text-slate-400 max-w-xl mx-auto">
          Upload an image of road distress (potholes, longitudinal/transverse/alligator cracking). The system will run RF-DETR detection, synthesize OSM location, weather, and traffic context, and run Evidence-Aware Adaptive RAG.
        </p>
      </div>

      {error && (
        <div className="bg-rose-500/10 border border-rose-500/30 rounded-xl p-4 flex items-center space-x-3 text-rose-300 text-xs">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {!assessment ? (
        <form onSubmit={handleSubmitInitial} className="space-y-8">
          {/* Step 1: Upload First Image */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-300">
              1. Upload or Capture Primary Image
            </h2>

            <div className="border-2 border-dashed border-slate-800 hover:border-blue-500/50 rounded-xl p-8 text-center transition cursor-pointer relative bg-slate-950/50">
              <input
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer w-full h-full"
              />
              {previewUrl ? (
                <div className="space-y-3">
                  <img src={previewUrl} alt="Preview" className="max-h-64 mx-auto rounded-lg shadow-lg" />
                  <p className="text-xs text-blue-400 font-medium">Click or drag to change image</p>
                </div>
              ) : (
                <div className="space-y-3">
                  <div className="w-12 h-12 bg-blue-600/20 text-blue-400 rounded-xl flex items-center justify-center mx-auto">
                    <Upload className="w-6 h-6" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-white">Click or drag image to upload</p>
                    <p className="text-xs text-slate-400 mt-1">JPEG, PNG, or WEBP up to 15MB</p>
                  </div>
                </div>
              )}
            </div>
          </div>

          {/* Step 2: GPS Location Selection */}
          <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider text-slate-300">
                2. Capture or Adjust GPS Location
              </h2>
              <button
                type="button"
                onClick={handleGetLocation}
                disabled={locating}
                className="text-xs text-blue-400 hover:text-blue-300 font-semibold flex items-center space-x-1"
              >
                <MapPin className="w-3.5 h-3.5" />
                <span>{locating ? 'Acquiring GPS...' : 'Refetch GPS'}</span>
              </button>
            </div>

            <div className="grid sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Latitude</label>
                <input
                  type="number"
                  step="any"
                  value={latitude !== null ? latitude : ''}
                  onChange={(e) => setLatitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                  placeholder="12.9716"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-slate-400 mb-1">Longitude</label>
                <input
                  type="number"
                  step="any"
                  value={longitude !== null ? longitude : ''}
                  onChange={(e) => setLongitude(parseFloat(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 rounded-xl px-4 py-2.5 text-sm text-white focus:outline-none focus:border-blue-500"
                  placeholder="77.5946"
                />
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={!firstFile}
            className="w-full bg-blue-600 hover:bg-blue-500 text-white font-bold py-4 rounded-xl transition shadow-xl shadow-blue-600/30 flex items-center justify-center space-x-2 text-base disabled:opacity-50"
          >
            <span>Run AI Damage Assessment</span>
            <ArrowRight className="w-5 h-5" />
          </button>
        </form>
      ) : (
        /* Multi-Image Prompt & Summary after initial detection */
        <div className="space-y-8 bg-slate-900 border border-slate-800 rounded-2xl p-8">
          <div className="border-b border-slate-800 pb-6 space-y-2 text-center">
            <span className="px-3 py-1 bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 text-xs font-semibold rounded-full">
              Primary Detection Complete
            </span>
            <h2 className="text-2xl font-bold text-white">Detection & Initial Context</h2>
            <p className="text-xs text-slate-400">
              Assessment ID: <code className="text-blue-400 font-mono">{assessment.assessmentId}</code>
            </p>
          </div>

          {/* Primary Detection Bounding Box Viewer */}
          {assessment.images.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-xs font-bold uppercase tracking-wider text-slate-400">
                Primary Image Detection ({assessment.images[0].detections.length} detections)
              </h3>
              <BoundingBoxViewer
                imageUrl={assessment.images[0].storagePath}
                detections={assessment.images[0].detections}
                width={assessment.images[0].width}
                height={assessment.images[0].height}
              />
            </div>
          )}

          {/* Prompt for Additional Images */}
          <div className="bg-slate-950 border border-slate-800 rounded-xl p-6 space-y-4">
            <div className="flex items-start space-x-3">
              <Camera className="w-6 h-6 text-cyan-400 flex-shrink-0 mt-0.5" />
              <div className="space-y-1">
                <h4 className="text-sm font-bold text-white">
                  Do you have additional images of this road damage from different angles?
                </h4>
                <p className="text-xs text-slate-400">
                  You can upload multiple supplementary images. All images will be aggregated into this single assessment.
                </p>
              </div>
            </div>

            <div className="flex flex-col sm:flex-row items-center gap-4 pt-2">
              <label className="w-full sm:w-auto px-5 py-2.5 bg-slate-800 hover:bg-slate-700 border border-slate-700 text-white rounded-xl text-xs font-bold transition cursor-pointer flex items-center justify-center space-x-2">
                <PlusCircle className="w-4 h-4 text-cyan-400" />
                <span>{uploadingAdditional ? 'Uploading...' : 'Add Additional Image'}</span>
                <input
                  type="file"
                  accept="image/*"
                  onChange={handleAddAdditionalFile}
                  disabled={uploadingAdditional}
                  className="hidden"
                />
              </label>

              <button
                type="button"
                onClick={handleFinishAssessment}
                className="w-full sm:w-auto px-6 py-2.5 bg-blue-600 hover:bg-blue-500 text-white font-bold rounded-xl text-xs transition shadow-lg shadow-blue-600/20 flex items-center justify-center space-x-2"
              >
                <span>Proceed to Grounded Report ({assessment.images.length} Image{assessment.images.length > 1 ? 's' : ''})</span>
                <ArrowRight className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
