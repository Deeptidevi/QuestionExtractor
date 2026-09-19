import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  FileText,
  RefreshCw,
  Download,
  Trash2,
  Sparkles,
  HelpCircle,
  KeyRound,
  AlertTriangle,
  CheckCircle2,
  Layers,
  ChevronRight,
  Eye,
  SlidersHorizontal,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { questionsApi } from '../api/questions';
import { answersApi } from '../api/answers';
import { StatusBadge } from '../components/ui/StatusBadge';
import { ConfidenceBadge } from '../components/ui/ConfidenceBadge';
import { StatCard } from '../components/ui/StatCard';
import { ProcessingTimeline } from '../components/documents/ProcessingTimeline';
import { DocumentPreview } from '../components/documents/DocumentPreview';
import { QuestionCard } from '../components/questions/QuestionCard';
import { Skeleton, TableSkeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';

export const DocumentDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const [activeTab, setActiveTab] = useState<'questions' | 'answers' | 'pages'>('questions');
  const [selectedQuestion, setSelectedQuestion] = useState<any | null>(null);

  // 1. Fetch Document Info with polling
  const {
    data: document,
    isLoading: isDocLoading,
    refetch: refetchDoc,
  } = useQuery({
    queryKey: ['document', id],
    queryFn: () => documentsApi.getDocument(id!),
    enabled: !!id,
    refetchInterval: (query) => {
      const status = query.state.data?.status;
      return status === 'PROCESSING' || status === 'QUEUED' || status === 'UPLOADED' ? 2500 : false;
    },
  });

  // Automatically refresh questions, answers & pages when document status completes
  React.useEffect(() => {
    if (document?.status === 'COMPLETED' || document?.status === 'COMPLETED_WITH_WARNINGS' || document?.status === 'NEEDS_REVIEW') {
      queryClient.invalidateQueries({ queryKey: ['documentQuestions', id] });
      queryClient.invalidateQueries({ queryKey: ['documentAnswers', id] });
      queryClient.invalidateQueries({ queryKey: ['documentPages', id] });
    }
  }, [document?.status, id, queryClient]);

  // 2. Fetch Document Questions
  const { data: questionsData, isLoading: isQuestionsLoading } = useQuery({
    queryKey: ['documentQuestions', id],
    queryFn: () => questionsApi.getDocumentQuestions(id!),
    enabled: !!id,
  });

  // 3. Fetch Document Answers
  const { data: answersData } = useQuery({
    queryKey: ['documentAnswers', id],
    queryFn: () => answersApi.getDocumentAnswers(id!),
    enabled: !!id,
  });

  // 4. Fetch Document Pages
  const { data: pagesData } = useQuery({
    queryKey: ['documentPages', id],
    queryFn: () => documentsApi.getDocumentPages(id!),
    enabled: !!id,
  });

  // Reprocess Mutation
  const reprocessMutation = useMutation({
    mutationFn: (forceOcr: boolean) => documentsApi.reprocessDocument(id!, forceOcr),
    onSuccess: () => {
      success('Reprocessing Triggered', 'Document sent back to extraction pipeline.');
      queryClient.invalidateQueries({ queryKey: ['document', id] });
      queryClient.invalidateQueries({ queryKey: ['documentQuestions', id] });
    },
    onError: () => {
      error('Reprocess Error', 'Could not reprocess document.');
    },
  });

  const questions = questionsData?.items || [];
  const answers = answersData?.answers || [];
  const pages = pagesData || [];

  const totalQuestions = questions.length;
  const answeredCount = questions.filter((q) => q.has_answer).length;
  const reviewCount = questions.filter((q) => q.review_required).length;

  const avgConfidence =
    totalQuestions > 0
      ? Math.round(
          (questions.reduce((acc, q) => acc + (q.extraction_confidence || 0.95), 0) /
            totalQuestions) *
            100
        )
      : 100;

  if (isDocLoading) {
    return (
      <div className="space-y-6 animate-fade-in p-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-28 w-full" />
        <div className="grid grid-cols-4 gap-4">
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
          <Skeleton className="h-24 w-full" />
        </div>
      </div>
    );
  }

  if (!document) {
    return (
      <EmptyState
        title="Document Not Found"
        description="The requested document could not be located or has been deleted."
        actionText="Back to Documents"
        onAction={() => navigate('/documents')}
      />
    );
  }

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Top Header & Breadcrumb */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-200">
        <div>
          <button
            onClick={() => navigate('/documents')}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-surface-500 hover:text-surface-900 transition-colors mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back to Documents
          </button>

          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl sm:text-2xl font-extrabold text-surface-900 tracking-tight">
              {document.title || document.original_filename}
            </h2>
            <StatusBadge status={document.status} />
          </div>
          <p className="text-xs text-surface-400 mt-1">
            Filename: <span className="font-mono text-surface-600">{document.original_filename}</span> &bull;{' '}
            {(Number(document.file_size_bytes || document.file_size || 0) / 1024).toFixed(1)} KB &bull; {document.total_pages || 1} Pages
          </p>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5 shrink-0">
          <button
            onClick={() => reprocessMutation.mutate(false)}
            disabled={reprocessMutation.isPending || document.status === 'PROCESSING'}
            className="btn-secondary py-2 px-3 text-xs"
          >
            <RefreshCw
              className={`w-3.5 h-3.5 ${
                reprocessMutation.isPending || document.status === 'PROCESSING'
                  ? 'animate-spin'
                  : ''
              }`}
            />
            Reprocess
          </button>
          <button
            onClick={() => {
              // Copy JSON summary to clipboard
              navigator.clipboard.writeText(JSON.stringify({ document, questions, answers }, null, 2));
              success('Export Copied', 'Document and question JSON copied to clipboard.');
            }}
            className="btn-primary py-2 px-3 text-xs"
          >
            <Download className="w-3.5 h-3.5" />
            Export JSON
          </button>
        </div>
      </div>

      {/* Processing Pipeline Timeline */}
      <ProcessingTimeline status={document.status} />

      {/* Summary Stat Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Total Questions"
          value={totalQuestions}
          subtitle="Segmented stems"
          icon={HelpCircle}
          colorTheme="indigo"
        />
        <StatCard
          title="Answer Keys Matched"
          value={answeredCount}
          subtitle={`${answeredCount}/${totalQuestions} with solutions`}
          icon={KeyRound}
          colorTheme="emerald"
        />
        <StatCard
          title="Needs Review"
          value={reviewCount}
          subtitle="Flagged for verification"
          icon={AlertTriangle}
          colorTheme="amber"
          onClick={() => navigate('/review')}
        />
        <StatCard
          title="Average Confidence"
          value={`${avgConfidence}%`}
          subtitle="Weighted 5-signal score"
          icon={Sparkles}
          colorTheme="sky"
        />
      </div>

      {/* Main Content Area: Split View */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side (5 Cols on LG): Document Viewer & Source Regions */}
        <div className="lg:col-span-5 sticky top-20 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-surface-900">Source Document Preview</h3>
            <span className="text-[11px] text-surface-500 font-mono">
              Click any question to highlight region
            </span>
          </div>

          <DocumentPreview
            document={document}
            pages={pages}
            activePageNumber={
              selectedQuestion?.source_pages?.[0] || selectedQuestion?.page_start || 1
            }
            highlightedQuestionText={
              selectedQuestion
                ? `${selectedQuestion.question_number ? `Q${selectedQuestion.question_number}. ` : ''}${selectedQuestion.question_text}`
                : undefined
            }
          />
        </div>

        {/* Right Side (7 Cols on LG): Extracted Content & Tabs */}
        <div className="lg:col-span-7 space-y-6">
          {/* Navigation Tabs */}
          <div className="flex items-center gap-2 border-b border-surface-200 pb-2">
            <button
              onClick={() => setActiveTab('questions')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'questions'
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'text-surface-600 hover:text-surface-900 hover:bg-surface-100'
              }`}
            >
              Extracted Questions ({totalQuestions})
            </button>
            <button
              onClick={() => setActiveTab('answers')}
              className={`px-4 py-2 rounded-xl text-xs font-bold transition-all ${
                activeTab === 'answers'
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'text-surface-600 hover:text-surface-900 hover:bg-surface-100'
              }`}
            >
              Answer Keys ({answers.length})
            </button>
          </div>

          {/* Tab 1: Questions List */}
          {activeTab === 'questions' && (
            <div className="space-y-4">
              {isQuestionsLoading ? (
                <TableSkeleton rows={4} cols={4} />
              ) : questions.length === 0 ? (
                <EmptyState
                  title="No questions extracted yet"
                  description={
                    document.status === 'PROCESSING'
                      ? 'The extraction pipeline is currently parsing this document. Please wait...'
                      : 'No questions were identified in this document.'
                  }
                />
              ) : (
                questions.map((q) => (
                  <QuestionCard
                    key={q.id}
                    question={q}
                    isSelected={selectedQuestion?.id === q.id}
                    onSelect={() => setSelectedQuestion(q)}
                  />
                ))
              )}
            </div>
          )}

          {/* Tab 2: Answer Keys */}
          {activeTab === 'answers' && (
            <div className="card-panel p-6 bg-white space-y-4">
              <div className="flex items-center justify-between pb-3 border-b border-surface-100">
                <h4 className="text-sm font-bold text-surface-900">Extracted Answer Keys</h4>
                <span className="text-xs text-surface-500">
                  Matched: {answersData?.matched_answers_count || 0} &bull; Unmatched:{' '}
                  {answersData?.unmatched_answers_count || 0}
                </span>
              </div>

              {answers.length === 0 ? (
                <EmptyState
                  title="No answer keys detected"
                  description="No standalone or inline answer key section was found in this document."
                />
              ) : (
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {answers.map((ans) => (
                    <div
                      key={ans.id}
                      className="p-3.5 rounded-xl bg-surface-50 border border-surface-200/80 flex items-start justify-between gap-3 text-xs"
                    >
                      <div>
                        <div className="flex items-center gap-2">
                          <span className="w-5 h-5 rounded bg-brand-600 text-white font-bold text-[10px] flex items-center justify-center">
                            #{ans.question_number || '?'}
                          </span>
                          <span className="font-bold text-surface-900">
                            Correct: [{ans.answer_value}]
                          </span>
                        </div>
                        {ans.raw_answer_text && (
                          <p className="text-[11px] text-surface-500 mt-1 truncate max-w-[180px]">
                            Raw: {ans.raw_answer_text}
                          </p>
                        )}
                      </div>

                      <div className="text-right">
                        <span
                          className={`inline-block px-2 py-0.5 rounded text-[10px] font-semibold ${
                            ans.match_status === 'EXACT_MATCH'
                              ? 'bg-emerald-100 text-emerald-800'
                              : 'bg-amber-100 text-amber-800'
                          }`}
                        >
                          {ans.match_status}
                        </span>
                        <p className="text-[10px] text-surface-400 mt-1">
                          {Math.round(ans.confidence * 100)}% conf
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
