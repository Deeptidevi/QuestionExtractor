import React from 'react';
import { DocumentStatus } from '../../types';
import { CheckCircle2, Clock, AlertTriangle, XCircle, Loader2, Sparkles } from 'lucide-react';

interface StatusBadgeProps {
  status: DocumentStatus | string;
  size?: 'sm' | 'md' | 'lg';
  showIcon?: boolean;
}

export const StatusBadge: React.FC<StatusBadgeProps> = ({
  status,
  size = 'md',
  showIcon = true,
}) => {
  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-medium',
    lg: 'px-3 py-1.5 text-sm font-semibold',
  };

  const statusConfig: Record<
    string,
    { label: string; bg: string; text: string; border: string; icon: React.ReactNode }
  > = {
    COMPLETED: {
      label: 'Completed',
      bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
      text: 'text-emerald-700',
      border: 'border-emerald-200',
      icon: <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />,
    },
    PROCESSING: {
      label: 'Processing',
      bg: 'bg-sky-50 text-sky-700 border-sky-200/80',
      text: 'text-sky-700',
      border: 'border-sky-200',
      icon: <Loader2 className="w-3.5 h-3.5 text-sky-600 animate-spin" />,
    },
    QUEUED: {
      label: 'Queued',
      bg: 'bg-indigo-50 text-indigo-700 border-indigo-200/80',
      text: 'text-indigo-700',
      border: 'border-indigo-200',
      icon: <Clock className="w-3.5 h-3.5 text-indigo-600" />,
    },
    NEEDS_REVIEW: {
      label: 'Needs Review',
      bg: 'bg-amber-50 text-amber-700 border-amber-200/80',
      text: 'text-amber-700',
      border: 'border-amber-200',
      icon: <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />,
    },
    PARTIAL: {
      label: 'Partial',
      bg: 'bg-orange-50 text-orange-700 border-orange-200/80',
      text: 'text-orange-700',
      border: 'border-orange-200',
      icon: <Sparkles className="w-3.5 h-3.5 text-orange-600" />,
    },
    FAILED: {
      label: 'Failed',
      bg: 'bg-rose-50 text-rose-700 border-rose-200/80',
      text: 'text-rose-700',
      border: 'border-rose-200',
      icon: <XCircle className="w-3.5 h-3.5 text-rose-600" />,
    },
  };

  const current = statusConfig[status] || {
    label: status,
    bg: 'bg-surface-100 text-surface-700 border-surface-200',
    text: 'text-surface-700',
    border: 'border-surface-200',
    icon: null,
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border shadow-2xs ${current.bg} ${sizeClasses[size]}`}
    >
      {showIcon && current.icon}
      <span>{current.label}</span>
    </span>
  );
};
