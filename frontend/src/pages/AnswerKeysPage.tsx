import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import {
  KeyRound,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Layers,
  ArrowRight,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { answersApi } from '../api/answers';
import { StatCard } from '../components/ui/StatCard';
import { EmptyState } from '../components/ui/EmptyState';
import { TableSkeleton } from '../components/ui/Skeleton';
import { useNavigate } from 'react-router-dom';

export const AnswerKeysPage: React.FC = () => {
  const navigate = useNavigate();

  // 1. Fetch documents
  const { data: documentsData, isLoading: isDocsLoading } = useQuery({
    queryKey: ['answerKeyDocuments'],
    queryFn: () => documentsApi.getDocuments({ page_size: 50 }),
  });

  const docs = documentsData?.items || [];
  const [selectedDocId, setSelectedDocId] = useState<string>(docs[0]?.id || '');

  const activeDocId = selectedDocId || docs[0]?.id;

  // 2. Fetch answers for selected document
  const { data: answersData, isLoading: isAnswersLoading } = useQuery({
    queryKey: ['docAnswersKeyPage', activeDocId],
    queryFn: () => (activeDocId ? answersApi.getDocumentAnswers(activeDocId) : Promise.resolve(null)),
    enabled: !!activeDocId,
  });

  const answers = answersData?.answers || [];
  const matchedCount = answersData?.matched_answers_count || 0;
  const unmatchedCount = answersData?.unmatched_answers_count || 0;
  const matchPercentage =
    answers.length > 0 ? Math.round((matchedCount / answers.length) * 100) : 100;

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">Answer Keys & Matching</h2>
        <p className="text-xs sm:text-sm text-surface-500 mt-1">
          Inspect extracted answer keys, automatic question stem pairings, and ambiguity flags.
        </p>
      </div>

      {/* Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Answer Keys"
          value={answers.length}
          subtitle="Detected in document"
          icon={KeyRound}
          colorTheme="indigo"
        />
        <StatCard
          title="Exact Matched"
          value={matchedCount}
          subtitle="Paired with stem"
          icon={CheckCircle2}
          colorTheme="emerald"
        />
        <StatCard
          title="Unmatched / Uncertain"
          value={unmatchedCount}
          subtitle="Requires attention"
          icon={AlertTriangle}
          colorTheme="amber"
        />
        <StatCard
          title="Match Rate"
          value={`${matchPercentage}%`}
          subtitle="Auto-pairing success"
          icon={Sparkles}
          colorTheme="sky"
        />
      </div>

      {/* Document Selector Toolbar */}
      <div className="card-panel p-4 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-brand-600 shrink-0" />
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-surface-400">
              Select Question Paper
            </label>
            <select
              value={activeDocId}
              onChange={(e) => setSelectedDocId(e.target.value)}
              className="text-sm font-semibold text-surface-900 bg-transparent focus:outline-none cursor-pointer"
            >
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title || d.original_filename} ({d.total_pages || 1} pages)
                </option>
              ))}
            </select>
          </div>
        </div>

        {activeDocId && (
          <button
            onClick={() => navigate(`/documents/${activeDocId}`)}
            className="btn-secondary py-1.5 px-3 text-xs"
          >
            Open Document Details &rarr;
          </button>
        )}
      </div>

      {/* Answer Keys Grid */}
      <div className="card-panel p-6 bg-white space-y-4">
        <div className="flex items-center justify-between pb-3 border-b border-surface-100">
          <h3 className="text-base font-bold text-surface-900">Extracted Answer Values & Keys</h3>
          <span className="text-xs text-surface-500 font-mono">
            {answers.length} answers extracted
          </span>
        </div>

        {isAnswersLoading ? (
          <TableSkeleton rows={4} cols={4} />
        ) : answers.length === 0 ? (
          <EmptyState
            title="No Answer Keys Extracted"
            description="No answer key table or section was detected in this document. Upload a document with an answer section or link a separate answer sheet."
          />
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
            {answers.map((ans) => (
              <div
                key={ans.id}
                className="p-4 rounded-xl bg-surface-50 border border-surface-200/90 space-y-2 text-xs transition-all hover:border-brand-300 hover:shadow-xs"
              >
                <div className="flex items-center justify-between">
                  <span className="w-7 h-7 rounded-lg bg-brand-600 text-white font-bold flex items-center justify-center text-xs">
                    #{ans.question_number || '?'}
                  </span>
                  <span
                    className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      ans.match_status === 'EXACT_MATCH'
                        ? 'bg-emerald-100 text-emerald-800'
                        : 'bg-amber-100 text-amber-800'
                    }`}
                  >
                    {ans.match_status}
                  </span>
                </div>

                <div className="pt-1">
                  <p className="font-extrabold text-surface-900 text-sm">
                    Correct Option: [{ans.answer_value}]
                  </p>
                  {ans.raw_answer_text && (
                    <p className="text-[11px] text-surface-500 truncate mt-0.5">
                      Source text: "{ans.raw_answer_text}"
                    </p>
                  )}
                </div>

                <div className="flex items-center justify-between pt-2 border-t border-surface-200/60 text-[11px] text-surface-400">
                  <span>Confidence: {Math.round(ans.confidence * 100)}%</span>
                  {ans.source_page && <span>Page {ans.source_page}</span>}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
