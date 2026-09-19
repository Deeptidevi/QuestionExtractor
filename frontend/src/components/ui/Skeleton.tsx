import React from 'react';

export const Skeleton: React.FC<{ className?: string }> = ({ className = 'h-4 w-full' }) => {
  return <div className={`bg-surface-200/70 animate-pulse rounded-md ${className}`} />;
};

export const TableSkeleton: React.FC<{ rows?: number; cols?: number }> = ({
  rows = 5,
  cols = 6,
}) => {
  return (
    <div className="w-full space-y-3">
      <div className="flex gap-4 p-4 border-b border-surface-200 bg-surface-50/50 rounded-t-xl">
        {Array.from({ length: cols }).map((_, i) => (
          <Skeleton key={`head-${i}`} className={`h-4 ${i === 0 ? 'w-48' : 'w-24'}`} />
        ))}
      </div>
      <div className="divide-y divide-surface-100 p-2">
        {Array.from({ length: rows }).map((_, r) => (
          <div key={`row-${r}`} className="flex items-center gap-4 p-4">
            {Array.from({ length: cols }).map((_, c) => (
              <Skeleton
                key={`cell-${r}-${c}`}
                className={`h-4 ${c === 0 ? 'w-48' : 'w-24'}`}
              />
            ))}
          </div>
        ))}
      </div>
    </div>
  );
};

export const CardSkeleton: React.FC = () => {
  return (
    <div className="card-panel p-6 space-y-4">
      <div className="flex justify-between items-center">
        <Skeleton className="h-5 w-32" />
        <Skeleton className="h-8 w-8 rounded-full" />
      </div>
      <Skeleton className="h-8 w-20" />
      <Skeleton className="h-3 w-40" />
    </div>
  );
};
