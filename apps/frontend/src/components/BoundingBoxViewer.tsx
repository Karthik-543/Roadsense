import React from 'react';
import { DetectionResult } from '../types';

interface BoundingBoxViewerProps {
  imageUrl: string;
  detections: DetectionResult[];
  width?: number;
  height?: number;
  imageWidth?: number;
  imageHeight?: number;
}

export const BoundingBoxViewer: React.FC<BoundingBoxViewerProps> = ({
  imageUrl,
  detections,
  width,
  height,
  imageWidth,
  imageHeight,
}) => {
  const effWidth = width || imageWidth || 640;
  const effHeight = height || imageHeight || 480;
  const BASE_URL = ((import.meta as any).env?.VITE_API_BASE_URL || 'https://roadsense-1-j77g.onrender.com').replace(/\/$/, '');
  
  const cleanPath = imageUrl.startsWith('/') ? imageUrl : `/${imageUrl}`;
  const fullImageUrl = imageUrl.startsWith('http')
    ? imageUrl
    : `${BASE_URL}${cleanPath}`;

  return (
    <div className="relative w-full min-h-[380px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl flex items-center justify-center">
      <img
        src={fullImageUrl}
        alt="Road Damage Detection"
        className="w-full h-auto min-h-[380px] max-h-[600px] object-contain block rounded-xl"
      />

      {detections.map((det, idx) => {
        if (!det.boundingBox || det.boundingBox.length < 4) return null;
        let [yMin, xMin, yMax, xMax] = det.boundingBox;

        let left = 0;
        let top = 0;
        let boxWidth = 0;
        let boxHeight = 0;

        if (xMax <= 1.0 && yMax <= 1.0 && xMin <= 1.0 && yMin <= 1.0) {
          left = xMin * 100;
          top = yMin * 100;
          boxWidth = (xMax - xMin) * 100;
          boxHeight = (yMax - yMin) * 100;
        } else {
          left = (xMin / effWidth) * 100;
          top = (yMin / effHeight) * 100;
          boxWidth = ((xMax - xMin) / effWidth) * 100;
          boxHeight = ((yMax - yMin) / effHeight) * 100;
        }

        const colors = [
          'border-rose-500 bg-rose-500/20 text-rose-300',
          'border-amber-500 bg-amber-500/20 text-amber-300',
          'border-cyan-500 bg-cyan-500/20 text-cyan-300',
          'border-emerald-500 bg-emerald-500/20 text-emerald-300',
        ];
        const colorClass = colors[idx % colors.length];

        return (
          <div
            key={idx}
            className={`absolute border-2 rounded ${colorClass} transition-all duration-300 hover:border-white hover:z-20`}
            style={{
              left: `${Math.max(0, Math.min(100, left))}%`,
              top: `${Math.max(0, Math.min(100, top))}%`,
              width: `${Math.max(1, Math.min(100, boxWidth))}%`,
              height: `${Math.max(1, Math.min(100, boxHeight))}%`,
            }}
          >
            <div className="absolute -top-7 left-0 bg-slate-900/95 text-white text-[11px] font-mono px-2 py-0.5 rounded border border-slate-700 shadow whitespace-nowrap flex items-center space-x-1.5 z-30">
              <span className="font-semibold text-blue-400">{det.damageType}</span>
              <span className="text-slate-300 font-bold">({(det.confidence * 100).toFixed(1)}%)</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
