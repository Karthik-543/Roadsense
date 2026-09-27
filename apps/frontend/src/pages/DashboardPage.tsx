import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  FileText, 
  Plus, 
  Search, 
  MapPin, 
  Calendar, 
  AlertTriangle, 
  ShieldAlert, 
  CheckCircle2, 
  CloudRain, 
  Car, 
  ChevronRight,
  Filter,
  RefreshCw
} from 'lucide-react';
import { getUserAssessments } from '../services/api';
import { Assessment } from '../types';

export const DashboardPage: React.FC = () => {
  const [assessments, setAssessments] = useState<Assessment[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedDamageFilter, setSelectedDamageFilter] = useState<string>('ALL');

  const fetchAssessments = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getUserAssessments();
      setAssessments(data);
    } catch (err: any) {
      setError(err.message || 'Failed to load assessments');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, []);

  const totalAssessments = assessments.length;
  const totalDetections = assessments.reduce((acc, curr) => {
    const imgDetections = curr.images?.reduce((sum, img) => sum + (img.detections?.length || 0), 0) || 0;
    return acc + imgDetections;
  }, 0);

  const filteredAssessments = assessments.filter(ass => {
    const matchesSearch = 
      ass.assessmentId.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ass.location?.address?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ass.location?.road?.toLowerCase().includes(searchTerm.toLowerCase()) ||
      ass.rag?.executiveSummary?.toLowerCase().includes(searchTerm.toLowerCase());

    if (selectedDamageFilter === 'ALL') return matchesSearch;

    const hasDamage = ass.images?.some(img => 
      img.detections?.some(d => d.damageType?.toUpperCase() === selectedDamageFilter)
    );

    return matchesSearch && hasDamage;
  });

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-slate-900 tracking-tight">
            Damage Assessment Dashboard
          </h1>
          <p className="mt-1 text-slate-600">
            View, track, and manage your AI-analyzed road infrastructure reports.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchAssessments}
            className="p-2.5 border border-slate-200 text-slate-600 hover:text-slate-900 hover:bg-slate-50 rounded-lg transition"
            title="Refresh list"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
          <Link
            to="/report"
            className="inline-flex items-center justify-center px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg shadow-sm transition gap-2"
          >
            <Plus className="w-5 h-5" />
            New Assessment
          </Link>
        </div>
      </div>

      {/* Stats Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
            <FileText className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalAssessments}</div>
            <div className="text-sm font-medium text-slate-500">Total Assessments</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-amber-50 text-amber-600 rounded-lg">
            <AlertTriangle className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">{totalDetections}</div>
            <div className="text-sm font-medium text-slate-500">Damages Detected</div>
          </div>
        </div>

        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex items-center gap-4">
          <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
            <CheckCircle2 className="w-6 h-6" />
          </div>
          <div>
            <div className="text-2xl font-bold text-slate-900">Adaptive RAG</div>
            <div className="text-sm font-medium text-slate-500">Evidence Verification Active</div>
          </div>
        </div>
      </div>

      {/* Filters & Search */}
      <div className="bg-white p-4 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="relative w-full sm:w-80">
          <Search className="w-5 h-5 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
          <input
            type="text"
            placeholder="Search road, ID, or summary..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border border-slate-200 rounded-lg text-slate-900 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
        </div>

        <div className="flex items-center gap-2 w-full sm:w-auto">
          <Filter className="w-4 h-4 text-slate-500" />
          <span className="text-sm text-slate-600 font-medium">Filter Damage:</span>
          <select
            value={selectedDamageFilter}
            onChange={(e) => setSelectedDamageFilter(e.target.value)}
            className="border border-slate-200 rounded-lg px-3 py-2 text-sm text-slate-800 bg-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="ALL">All Damage Types</option>
            <option value="POTHOLE">Pothole</option>
            <option value="ALLIGATOR_CRACK">Alligator Crack</option>
            <option value="TRANSVERSE_CRACK">Transverse Crack</option>
            <option value="LONGITUDINAL_CRACK">Longitudinal Crack</option>
          </select>
        </div>
      </div>

      {/* Assessment List */}
      {loading ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center text-slate-500">
          <RefreshCw className="w-8 h-8 animate-spin mx-auto text-blue-600 mb-3" />
          Loading your assessments...
        </div>
      ) : error ? (
        <div className="bg-red-50 p-6 rounded-xl border border-red-200 text-red-700 flex items-center justify-between">
          <span>{error}</span>
          <button
            onClick={fetchAssessments}
            className="px-4 py-2 bg-red-600 text-white font-medium text-sm rounded-lg hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      ) : filteredAssessments.length === 0 ? (
        <div className="bg-white p-12 rounded-xl border border-slate-200 text-center max-w-md mx-auto space-y-4">
          <div className="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto text-slate-400">
            <FileText className="w-8 h-8" />
          </div>
          <h3 className="text-lg font-bold text-slate-900">No assessments found</h3>
          <p className="text-sm text-slate-500">
            {searchTerm || selectedDamageFilter !== 'ALL'
              ? 'Try changing your search keywords or filter criteria.'
              : 'Start by uploading a road damage image for automated RF-DETR damage detection and RAG analysis.'}
          </p>
          <Link
            to="/report"
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white font-medium rounded-lg text-sm hover:bg-blue-700 transition"
          >
            Create Assessment
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAssessments.map((ass) => {
            const firstImg = ass.images && ass.images[0];
            const detections = ass.images?.flatMap(img => img.detections || []) || [];

            return (
              <div
                key={ass.id || ass.assessmentId}
                className="bg-white rounded-xl border border-slate-200 shadow-sm hover:shadow-md transition flex flex-col overflow-hidden"
              >
                {/* Header / ID */}
                <div className="p-4 bg-slate-50 border-b border-slate-100 flex items-center justify-between">
                  <div className="font-mono text-xs text-blue-700 font-bold bg-blue-50 px-2.5 py-1 rounded border border-blue-100">
                    {ass.assessmentId || ass.id}
                  </div>
                  <div className="flex items-center text-xs text-slate-500 gap-1">
                    <Calendar className="w-3.5 h-3.5 text-slate-400" />
                    {ass.createdAt ? new Date(ass.createdAt).toLocaleDateString() : 'Recent'}
                  </div>
                </div>

                {/* Content */}
                <div className="p-5 flex-1 space-y-4">
                  {/* Location info */}
                  <div className="flex items-start gap-2 text-sm text-slate-700">
                    <MapPin className="w-4 h-4 text-rose-500 shrink-0 mt-0.5" />
                    <span className="font-medium line-clamp-1">
                      {ass.location?.road || ass.location?.address || 'Location Recorded'}
                    </span>
                  </div>

                  {/* Damage Badges */}
                  <div>
                    <div className="text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2">
                      Detected Damage ({detections.length})
                    </div>
                    {detections.length === 0 ? (
                      <span className="text-xs text-slate-400 italic">No defects detected</span>
                    ) : (
                      <div className="flex flex-wrap gap-1.5">
                        {Array.from(new Set(detections.map(d => d.damageType))).map((type) => (
                          <span
                            key={type}
                            className="inline-flex items-center gap-1 text-xs font-semibold px-2 py-0.5 rounded-md bg-amber-50 text-amber-800 border border-amber-200"
                          >
                            <AlertTriangle className="w-3 h-3 text-amber-600" />
                            {type.replace('_', ' ')}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>

                  {/* Context Badges */}
                  <div className="flex items-center gap-3 text-xs text-slate-500 pt-2 border-t border-slate-100">
                    {ass.weather?.available && (
                      <span className="flex items-center gap-1 text-slate-600">
                        <CloudRain className="w-3.5 h-3.5 text-blue-500" />
                        Weather Context
                      </span>
                    )}
                    {ass.traffic?.available && (
                      <span className="flex items-center gap-1 text-slate-600">
                        <Car className="w-3.5 h-3.5 text-indigo-500" />
                        Traffic Context
                      </span>
                    )}
                  </div>

                  {/* Executive Summary Snippet */}
                  {ass.rag?.executiveSummary && (
                    <p className="text-xs text-slate-600 line-clamp-2 bg-slate-50 p-2.5 rounded border border-slate-100 italic">
                      "{ass.rag.executiveSummary}"
                    </p>
                  )}
                </div>

                {/* Footer Action */}
                <div className="p-4 bg-slate-50/50 border-t border-slate-100 flex items-center justify-between">
                  <span className="text-xs font-medium text-slate-500">
                    RAG: <span className="text-slate-800">{ass.rag?.ragMode || 'ADAPTIVE'}</span>
                  </span>
                  <Link
                    to={`/assessment/${ass.assessmentId || ass.id}`}
                    className="inline-flex items-center text-xs font-semibold text-blue-600 hover:text-blue-800 gap-1"
                  >
                    View Report
                    <ChevronRight className="w-4 h-4" />
                  </Link>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
