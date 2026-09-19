import React from 'react';
import { LucideIcon, FileText } from 'lucide-react';

interface EmptyStateProps {
  icon?: LucideIcon;
  title: string;
  description: string;
  actionText?: string;
  onAction?: () => void;
  className?: string;
}

export const EmptyState: React.FC<EmptyStateProps> = ({
  icon: Icon = FileText,
  title,
  description,
  actionText,
  onAction,
  className = '',
}) => {
  return (
    <div
      className={`card-panel flex flex-col items-center justify-center text-center p-12 bg-white/50 border-dashed ${className}`}
    >
      <div className="w-14 h-14 rounded-2xl bg-surface-100 flex items-center justify-center text-surface-400 mb-4 ring-8 ring-surface-50">
        <Icon className="w-7 h-7" />
      </div>
      <h3 className="text-base font-semibold text-surface-900 mb-1">{title}</h3>
      <p className="text-sm text-surface-500 max-w-sm mb-6 leading-relaxed">{description}</p>
      {actionText && onAction && (
        <button onClick={onAction} className="btn-primary">
          {actionText}
        </button>
      )}
    </div>
  );
};
