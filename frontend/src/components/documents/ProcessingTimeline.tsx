import React from 'react';
import { DocumentStatus } from '../../types';
import {
  CheckCircle2,
  Loader2,
  FileSearch,
  Cpu,
  Layers,
  Sparkles,
  KeyRound,
  AlertTriangle,
} from 'lucide-react';

interface ProcessingTimelineProps {
  status: DocumentStatus;
  className?: string;
}

export const ProcessingTimeline: React.FC<ProcessingTimelineProps> = ({
  status,
  className = '',
}) => {
  const steps = [
    { id: 'uploaded', label: 'Uploaded & Verified', icon: FileSearch },
    { id: 'ocr', label: 'OCR & Normalization', icon: Cpu },
    { id: 'segmentation', label: 'Question Segmentation', icon: Layers },
    { id: 'answers', label: 'Answer Key Matching', icon: KeyRound },
    { id: 'completed', label: 'Confidence & Completed', icon: Sparkles },
  ];

  const getStepState = (stepIndex: number) => {
    if (status === 'COMPLETED' || status === 'NEEDS_REVIEW') {
      return 'completed';
    }
    if (status === 'PROCESSING') {
      if (stepIndex <= 2) return 'completed';
      if (stepIndex === 3) return 'active';
      return 'pending';
    }
    if (status === 'QUEUED') {
      if (stepIndex === 0) return 'completed';
      if (stepIndex === 1) return 'active';
      return 'pending';
    }
    if (status === 'FAILED') {
      if (stepIndex === 0) return 'completed';
      return 'failed';
    }
    return 'pending';
  };

  return (
    <div className={`card-panel p-6 bg-white ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h4 className="text-sm font-bold text-surface-900">Extraction Pipeline Stages</h4>
          <p className="text-xs text-surface-500 mt-0.5">
            Automated multi-stage OCR, layout parsing, and confidence scoring
          </p>
        </div>
        <div className="flex items-center gap-1.5 text-xs font-medium text-surface-500">
          <span
            className={`w-2 h-2 rounded-full ${
              status === 'COMPLETED'
                ? 'bg-emerald-500'
                : status === 'PROCESSING'
                ? 'bg-brand-500 animate-ping'
                : status === 'NEEDS_REVIEW'
                ? 'bg-amber-500'
                : 'bg-surface-400'
            }`}
          />
          <span>{status}</span>
        </div>
      </div>

      {/* Timeline Steps */}
      <div className="relative">
        {/* Horizontal Connector Line */}
        <div className="hidden sm:block absolute top-5 left-8 right-8 h-0.5 bg-surface-200 -z-0" />

        <div className="grid grid-cols-1 sm:grid-cols-5 gap-4 relative z-10">
          {steps.map((step, idx) => {
            const state = getStepState(idx);
            const Icon = step.icon;

            return (
              <div key={step.id} className="flex sm:flex-col items-center sm:text-center gap-3 sm:gap-2">
                {/* Step Circle */}
                <div
                  className={`w-10 h-10 rounded-xl flex items-center justify-center shrink-0 border transition-all ${
                    state === 'completed'
                      ? 'bg-emerald-50 text-emerald-600 border-emerald-300 shadow-2xs'
                      : state === 'active'
                      ? 'bg-brand-50 text-brand-600 border-brand-300 shadow-sm ring-4 ring-brand-50 animate-pulse-subtle'
                      : state === 'failed'
                      ? 'bg-rose-50 text-rose-600 border-rose-300'
                      : 'bg-surface-100 text-surface-400 border-surface-200'
                  }`}
                >
                  {state === 'completed' ? (
                    <CheckCircle2 className="w-5 h-5 text-emerald-600" />
                  ) : state === 'active' ? (
                    <Loader2 className="w-5 h-5 text-brand-600 animate-spin" />
                  ) : (
                    <Icon className="w-5 h-5" />
                  )}
                </div>

                {/* Step Label */}
                <div>
                  <p
                    className={`text-xs font-semibold ${
                      state === 'completed'
                        ? 'text-surface-900'
                        : state === 'active'
                        ? 'text-brand-700'
                        : 'text-surface-400'
                    }`}
                  >
                    {step.label}
                  </p>
                  <p className="text-[10px] text-surface-400 capitalize">
                    {state === 'completed' ? 'Done' : state === 'active' ? 'In Progress' : 'Queued'}
                  </p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};
