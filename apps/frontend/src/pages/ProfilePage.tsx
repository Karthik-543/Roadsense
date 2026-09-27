import React from 'react';
import { useAuth } from '../context/AuthContext';
import { 
  User as UserIcon, 
  Mail, 
  ShieldCheck, 
  Server, 
  Database, 
  Cpu, 
  Activity, 
  FileCheck2, 
  Layers, 
  ExternalLink 
} from 'lucide-react';

export const ProfilePage: React.FC = () => {
  const { user } = useAuth();

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
      {/* User Header */}
      <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm flex flex-col sm:flex-row items-center gap-6">
        <div className="w-20 h-20 rounded-full bg-gradient-to-br from-blue-600 to-indigo-700 text-white flex items-center justify-center text-3xl font-extrabold shadow-md">
          {user?.fullName ? user.fullName.charAt(0).toUpperCase() : 'U'}
        </div>
        <div className="space-y-1 text-center sm:text-left flex-1">
          <h1 className="text-2xl font-extrabold text-slate-900">{user?.fullName || 'RoadSense Engineer'}</h1>
          <div className="flex flex-wrap items-center justify-center sm:justify-start gap-4 text-sm text-slate-600">
            <span className="flex items-center gap-1.5">
              <Mail className="w-4 h-4 text-slate-400" />
              {user?.email}
            </span>
            <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-200">
              <ShieldCheck className="w-3.5 h-3.5" />
              {user?.role || 'ENGINEER'}
            </span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* System Microservices Status */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
            <Server className="w-5 h-5 text-blue-600" />
            Active Microservices & Pipeline Status
          </h3>

          <div className="space-y-3">
            <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <div>
                  <div className="text-sm font-semibold text-slate-900">Spring Boot 3 Backend Gateway</div>
                  <div className="text-xs text-slate-500 font-mono">Port 8080 • JWT Security & REST API</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">ONLINE</span>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <div>
                  <div className="text-sm font-semibold text-slate-900">RF-DETR Detection Microservice</div>
                  <div className="text-xs text-slate-500 font-mono">Port 8000 • PyTorch Medium Model</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">ONLINE</span>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <div>
                  <div className="text-sm font-semibold text-slate-900">Adaptive RAG Subsystem Engine</div>
                  <div className="text-xs text-slate-500 font-mono">Port 8001 • FAISS + SentenceTransformers</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">ONLINE</span>
            </div>

            <div className="p-3.5 bg-slate-50 rounded-lg border border-slate-200 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-emerald-500 animate-pulse"></div>
                <div>
                  <div className="text-sm font-semibold text-slate-900">MongoDB Atlas Cluster</div>
                  <div className="text-xs text-slate-500 font-mono">Database: RoadSense</div>
                </div>
              </div>
              <span className="text-xs font-bold text-emerald-700 bg-emerald-50 px-2 py-0.5 rounded">CONNECTED</span>
            </div>
          </div>
        </div>

        {/* Research System Specifications */}
        <div className="bg-white p-6 rounded-xl border border-slate-200 shadow-sm space-y-4">
          <h3 className="font-bold text-slate-900 text-base flex items-center gap-2">
            <Cpu className="w-5 h-5 text-indigo-600" />
            Research Architecture Specifications
          </h3>

          <div className="space-y-3 text-xs text-slate-700">
            <div className="p-3 bg-indigo-50/50 rounded-lg border border-indigo-100 space-y-1">
              <div className="font-semibold text-indigo-900 text-sm">RF-DETR Damage Detection Model</div>
              <p className="text-slate-600">
                Checkpoint: <code className="font-mono text-slate-900">models/checkpoint_best_total.pth</code>
              </p>
              <p className="text-slate-600">
                Classes: <span className="font-semibold">0: longitudinal_crack, 1: transverse_crack, 2: alligator_crack, 4: pothole</span>
              </p>
            </div>

            <div className="p-3 bg-purple-50/50 rounded-lg border border-purple-100 space-y-1">
              <div className="font-semibold text-purple-900 text-sm">Evidence-Aware Adaptive RAG Subsystem</div>
              <p className="text-slate-600">
                Official RAG Systems compared:
              </p>
              <ol className="list-decimal list-inside font-medium text-purple-800 space-y-0.5">
                <li>STANDARD_RAG</li>
                <li>EVIDENCE_AWARE_RAG</li>
                <li>EVIDENCE_AWARE_ADAPTIVE_RAG</li>
              </ol>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
