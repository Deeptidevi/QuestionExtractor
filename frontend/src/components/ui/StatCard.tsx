import React from 'react';
import { LucideIcon } from 'lucide-react';

interface StatCardProps {
  title: string;
  value: string | number;
  subtitle?: string;
  icon: LucideIcon;
  trend?: {
    value: string;
    isPositive?: boolean;
  };
  colorTheme?: 'indigo' | 'emerald' | 'amber' | 'rose' | 'sky';
  onClick?: () => void;
}

export const StatCard: React.FC<StatCardProps> = ({
  title,
  value,
  subtitle,
  icon: Icon,
  trend,
  colorTheme = 'indigo',
  onClick,
}) => {
  const themeStyles = {
    indigo: {
      bg: 'bg-gradient-to-tr from-indigo-600 to-indigo-500 text-white',
      border: 'hover:border-indigo-300',
      ring: 'group-hover:ring-indigo-100',
      glow: 'group-hover:shadow-indigo-500/20',
    },
    emerald: {
      bg: 'bg-gradient-to-tr from-emerald-600 to-teal-500 text-white',
      border: 'hover:border-emerald-300',
      ring: 'group-hover:ring-emerald-100',
      glow: 'group-hover:shadow-emerald-500/20',
    },
    amber: {
      bg: 'bg-gradient-to-tr from-amber-500 to-orange-500 text-white',
      border: 'hover:border-amber-300',
      ring: 'group-hover:ring-amber-100',
      glow: 'group-hover:shadow-amber-500/20',
    },
    rose: {
      bg: 'bg-gradient-to-tr from-rose-600 to-pink-500 text-white',
      border: 'hover:border-rose-300',
      ring: 'group-hover:ring-rose-100',
      glow: 'group-hover:shadow-rose-500/20',
    },
    sky: {
      bg: 'bg-gradient-to-tr from-sky-500 to-cyan-500 text-white',
      border: 'hover:border-sky-300',
      ring: 'group-hover:ring-sky-100',
      glow: 'group-hover:shadow-sky-500/20',
    },
  };

  const style = themeStyles[colorTheme];

  return (
    <div
      onClick={onClick}
      className={`group card-panel-hover p-6 relative overflow-hidden transition-all duration-300 ${
        onClick ? 'cursor-pointer hover:scale-[1.015]' : ''
      } ${style.border}`}
    >
      <div className="flex items-start justify-between">
        <div>
          <p className="text-[11px] font-bold uppercase tracking-wider text-slate-400">{title}</p>
          <div className="flex items-baseline gap-2.5 mt-2.5">
            <h3 className="text-3xl font-extrabold tracking-tight text-slate-900">{value}</h3>
            {trend && (
              <span
                className={`text-[11px] font-bold inline-flex items-center px-2 py-0.5 rounded-full ${
                  trend.isPositive ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' : 'bg-slate-100 text-slate-600'
                }`}
              >
                {trend.value}
              </span>
            )}
          </div>
          {subtitle && <p className="text-xs text-slate-500 mt-1.5 font-medium">{subtitle}</p>}
        </div>

        <div className={`p-3 rounded-2xl shadow-md transition-all duration-300 ${style.bg} ${style.glow} group-hover:scale-110 group-hover:rotate-3`}>
          <Icon className="w-5 h-5" />
        </div>
      </div>
    </div>
  );
};
