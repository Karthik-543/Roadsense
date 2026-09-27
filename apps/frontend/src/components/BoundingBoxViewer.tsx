import React from 'react';
import { DetectionResult } from '../types';

interface BoundingBoxViewerProps {
  imageUrl: string;
  detections: DetectionResult[];
  width: number;
  height: number;
}

export const BoundingBoxViewer: React.FC<BoundingBoxViewerProps> = ({
  imageUrl,
  detections,
  width,
  height,
}) => {
  return (
    <div className="relative inline-block w-full overflow-hidden rounded-xl border border-slate-800 bg-slate-950 shadow-2xl">
      <img
        src={imageUrl}
        alt="Road Damage Detection"
        className="w-full h-auto object-contain block max-h-[500px]"
      />

      {detections.map((det, idx) => {
        if (!det.boundingBox || det.boundingBox.length < 4) return null;
        const [xMin, yMin, xMax, yMax] = det.boundingBox;

        // Calculate relative percentages
        const left = (xMin / (width || 640)) * 100;
        const top = (yMin / (height || 480)) * 100;
        const boxWidth = ((xMax - xMin) / (width || 640)) * 100;
        const boxHeight = ((yMax - yMin) / (height || 480)) * 100;

        const colors = [
          'border-rose-500 bg-rose-500/10 text-rose-300',
          'border-amber-500 bg-amber-500/10 text-amber-300',
          'border-cyan-500 bg-cyan-500/10 text-cyan-300',
          'border-emerald-500 bg-emerald-500/10 text-emerald-300',
        ];
        const colorClass = colors[idx % colors.length];

        return (
          <div
            key={idx}
            className={`absolute border-2 rounded ${colorClass} transition-all duration-300 hover:border-white hover:z-20`}
            style={{
              left: `${left}%`,
              top: `${top}%`,
              width: `${boxWidth}%`,
              height: `${boxHeight}%`,
            }}
          >
            <div className="absolute -top-6 left-0 bg-slate-900/90 text-white text-[11px] font-mono px-2 py-0.5 rounded border border-slate-700 shadow whitespace-nowrap flex items-center space-x-1">
              <span className="font-semibold text-blue-400">{det.damageType}</span>
              <span className="text-slate-400">({(det.confidence * 100).toFixed(1)}%)</span>
            </div>
          </div>
        );
      })}
    </div>
  );
};
