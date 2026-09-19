import React from 'react';

interface ConfidenceBadgeProps {
  score: number; // 0.0 to 1.0 or 0 to 100
  size?: 'sm' | 'md' | 'lg';
  showLabel?: boolean;
}

export const ConfidenceBadge: React.FC<ConfidenceBadgeProps> = ({
  score,
  size = 'md',
  showLabel = true,
}) => {
  // Normalize score to percentage 0-100
  const normalized = score <= 1.0 ? Math.round(score * 100) : Math.round(score);

  const getTier = (val: number) => {
    if (val >= 85) {
      return {
        label: 'High Confidence',
        bg: 'bg-emerald-50 text-emerald-700 border-emerald-200/80',
        dot: 'bg-emerald-500',
      };
    }
    if (val >= 60) {
      return {
        label: 'Medium Confidence',
        bg: 'bg-amber-50 text-amber-700 border-amber-200/80',
        dot: 'bg-amber-500',
      };
    }
    return {
      label: 'Needs Review',
      bg: 'bg-rose-50 text-rose-700 border-rose-200/80',
      dot: 'bg-rose-500',
    };
  };

  const tier = getTier(normalized);

  const sizeClasses = {
    sm: 'px-2 py-0.5 text-xs',
    md: 'px-2.5 py-1 text-xs font-medium',
    lg: 'px-3 py-1.5 text-sm font-semibold',
  };

  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full border ${tier.bg} ${sizeClasses[size]}`}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${tier.dot}`} />
      <span className="font-semibold">{normalized}%</span>
      {showLabel && <span className="opacity-80">({tier.label})</span>}
    </span>
  );
};

interface ConfidenceBarProps {
  score: number;
  height?: string;
  showText?: boolean;
}

export const ConfidenceBar: React.FC<ConfidenceBarProps> = ({
  score,
  height = 'h-1.5',
  showText = false,
}) => {
  const normalized = Math.min(100, Math.max(0, score <= 1.0 ? Math.round(score * 100) : Math.round(score)));

  const getColor = (val: number) => {
    if (val >= 85) return 'bg-emerald-500';
    if (val >= 60) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  return (
    <div className="w-full">
      {showText && (
        <div className="flex justify-between items-center text-xs text-surface-500 mb-1">
          <span>Confidence</span>
          <span className="font-semibold text-surface-700">{normalized}%</span>
        </div>
      )}
      <div className={`w-full bg-surface-100 rounded-full overflow-hidden ${height}`}>
        <div
          className={`${getColor(normalized)} ${height} rounded-full transition-all duration-500 ease-out`}
          style={{ width: `${normalized}%` }}
        />
      </div>
    </div>
  );
};
