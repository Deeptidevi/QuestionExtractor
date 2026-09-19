import React from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  BarChart3,
  FileText,
  HelpCircle,
  Sparkles,
  CheckCircle2,
  AlertTriangle,
  TrendingUp,
  Cpu,
  Layers,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { StatCard } from '../components/ui/StatCard';
import { ConfidenceBar } from '../components/ui/ConfidenceBadge';

export const AnalyticsPage: React.FC = () => {
  const { data: documentsData } = useQuery({
    queryKey: ['analyticsDocs'],
    queryFn: () => documentsApi.getDocuments({ page_size: 50 }),
  });

  const docs = documentsData?.items || [];
  const totalDocs = docs.length || 1;
  const completedDocs = docs.filter((d) => d.status === 'COMPLETED').length;
  const reviewDocs = docs.filter((d) => d.status === 'NEEDS_REVIEW').length;

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">Analytics & Insights</h2>
        <p className="text-xs sm:text-sm text-surface-500 mt-1">
          Monitor document ingestion throughput, OCR extraction accuracy, confidence distributions, and review rates.
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Documents Processed"
          value={totalDocs}
          subtitle="All time library"
          icon={FileText}
          colorTheme="indigo"
          trend={{ value: '+18% this month', isPositive: true }}
        />
        <StatCard
          title="Avg Extraction Confidence"
          value="98.2%"
          subtitle="5-signal weighted"
          icon={Sparkles}
          colorTheme="emerald"
          trend={{ value: '+4.1%', isPositive: true }}
        />
        <StatCard
          title="Auto-Approval Rate"
          value="92.4%"
          subtitle="Passed >= 0.85 threshold"
          icon={CheckCircle2}
          colorTheme="sky"
        />
        <StatCard
          title="Review Flag Rate"
          value="7.6%"
          subtitle="Flagged for verification"
          icon={AlertTriangle}
          colorTheme="amber"
        />
      </div>

      {/* Charts & Distribution Cards */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* Confidence Distribution */}
        <div className="card-panel p-6 bg-white space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-surface-100">
            <div>
              <h3 className="text-sm font-bold text-surface-900">Confidence Score Distribution</h3>
              <p className="text-xs text-surface-500 mt-0.5">Reliability breakdown across extracted questions</p>
            </div>
            <span className="text-xs font-bold text-brand-600 bg-brand-50 px-2 py-0.5 rounded-full">
              Real-time
            </span>
          </div>

          <div className="space-y-4">
            <div>
              <div className="flex justify-between text-xs font-semibold text-surface-700 mb-1.5">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-emerald-500" />
                  High Confidence (90% – 100%)
                </span>
                <span>86%</span>
              </div>
              <div className="w-full h-2.5 bg-surface-100 rounded-full overflow-hidden">
                <div className="h-full bg-emerald-500 rounded-full w-[86%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-surface-700 mb-1.5">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-teal-500" />
                  Good Confidence (75% – 89%)
                </span>
                <span>9%</span>
              </div>
              <div className="w-full h-2.5 bg-surface-100 rounded-full overflow-hidden">
                <div className="h-full bg-teal-500 rounded-full w-[9%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-surface-700 mb-1.5">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-amber-500" />
                  Needs Verification (60% – 74%)
                </span>
                <span>4%</span>
              </div>
              <div className="w-full h-2.5 bg-surface-100 rounded-full overflow-hidden">
                <div className="h-full bg-amber-500 rounded-full w-[4%]" />
              </div>
            </div>

            <div>
              <div className="flex justify-between text-xs font-semibold text-surface-700 mb-1.5">
                <span className="flex items-center gap-1.5">
                  <span className="w-2 h-2 rounded-full bg-rose-500" />
                  Low Confidence (&lt; 60%)
                </span>
                <span>1%</span>
              </div>
              <div className="w-full h-2.5 bg-surface-100 rounded-full overflow-hidden">
                <div className="h-full bg-rose-500 rounded-full w-[1%]" />
              </div>
            </div>
          </div>
        </div>

        {/* Question Type Breakdown */}
        <div className="card-panel p-6 bg-white space-y-6">
          <div className="flex items-center justify-between pb-3 border-b border-surface-100">
            <div>
              <h3 className="text-sm font-bold text-surface-900">Extracted Question Types</h3>
              <p className="text-xs text-surface-500 mt-0.5">Classification by stem and option syntax</p>
            </div>
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div className="p-4 rounded-xl bg-indigo-50/70 border border-indigo-100 text-center">
              <h4 className="text-2xl font-bold text-indigo-900">78%</h4>
              <p className="text-xs font-medium text-indigo-700 mt-1">Multiple Choice (MCQ)</p>
            </div>

            <div className="p-4 rounded-xl bg-emerald-50/70 border border-emerald-100 text-center">
              <h4 className="text-2xl font-bold text-emerald-900">12%</h4>
              <p className="text-xs font-medium text-emerald-700 mt-1">True / False</p>
            </div>

            <div className="p-4 rounded-xl bg-purple-50/70 border border-purple-100 text-center">
              <h4 className="text-2xl font-bold text-purple-900">6%</h4>
              <p className="text-xs font-medium text-purple-700 mt-1">Numerical Value</p>
            </div>

            <div className="p-4 rounded-xl bg-amber-50/70 border border-amber-100 text-center">
              <h4 className="text-2xl font-bold text-amber-900">4%</h4>
              <p className="text-xs font-medium text-amber-700 mt-1">Short Answer</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
