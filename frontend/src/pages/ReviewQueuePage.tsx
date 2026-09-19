import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  CheckSquare,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Edit3,
  Sparkles,
  ArrowRight,
  FileText,
  HelpCircle,
  X,
  Save,
} from 'lucide-react';
import { reviewApi } from '../api/review';
import { questionsApi } from '../api/questions';
import { documentsApi } from '../api/documents';
import { StatCard } from '../components/ui/StatCard';
import { ConfidenceBadge } from '../components/ui/ConfidenceBadge';
import { Modal } from '../components/ui/Modal';
import { DocumentPreview } from '../components/documents/DocumentPreview';
import { TableSkeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';
import { ReviewItem } from '../types';

export const ReviewQueuePage: React.FC = () => {
  const queryClient = useQueryClient();
  const navigate = useNavigate();
  const { success, error } = useToast();

  const [selectedReviewItem, setSelectedReviewItem] = useState<ReviewItem | null>(null);
  const [resolutionNotes, setResolutionNotes] = useState('');

  // 1. Fetch Review Queue
  const { data: queueData, isLoading, refetch } = useQuery({
    queryKey: ['reviewQueueList'],
    queryFn: () => reviewApi.getReviewQueue({ page_size: 50, status: 'PENDING' }),
  });

  // 2. Fetch Selected Question for modal
  const { data: activeQuestion } = useQuery({
    queryKey: ['activeReviewQuestion', selectedReviewItem?.question_id],
    queryFn: () => questionsApi.getQuestion(selectedReviewItem!.question_id!),
    enabled: !!selectedReviewItem?.question_id,
  });

  // 3. Fetch Parent Document for modal
  const { data: activeDocument } = useQuery({
    queryKey: ['activeReviewDocument', selectedReviewItem?.document_id],
    queryFn: () => documentsApi.getDocument(selectedReviewItem!.document_id),
    enabled: !!selectedReviewItem?.document_id,
  });

  // Resolve Mutation
  const resolveMutation = useMutation({
    mutationFn: ({ itemId, status, notes }: { itemId: string; status: 'ACCEPTED' | 'REJECTED' | 'EDITED'; notes?: string }) =>
      reviewApi.resolveReviewItem(itemId, { status, notes }),
    onSuccess: (_, vars) => {
      success('Review Item Resolved', `Question marked as ${vars.status}.`);
      setSelectedReviewItem(null);
      setResolutionNotes('');
      queryClient.invalidateQueries({ queryKey: ['reviewQueueList'] });
      queryClient.invalidateQueries({ queryKey: ['reviewQueueCount'] });
    },
    onError: () => {
      error('Resolution Failed', 'Could not submit review item resolution.');
    },
  });

  const items = queueData?.items || [];
  const totalPending = queueData?.meta?.total || items.length;

  const lowConfidenceCount = items.filter((i) => i.issue_type === 'LOW_OCR_CONFIDENCE').length;
  const unmatchedAnswerCount = items.filter((i) => i.issue_type === 'ANSWER_MATCH_UNCERTAIN').length;
  const optionsUncertainCount = items.filter((i) => i.issue_type === 'OPTIONS_UNCERTAIN').length;

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Header */}
      <div>
        <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">Review Queue</h2>
        <p className="text-xs sm:text-sm text-surface-500 mt-1">
          Questions requiring human verification due to low OCR density, ambiguous options, or unconfirmed answer key matches.
        </p>
      </div>

      {/* Review Metrics */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard
          title="Needs Review"
          value={totalPending}
          subtitle="Pending human check"
          icon={CheckSquare}
          colorTheme="amber"
        />
        <StatCard
          title="Low OCR Confidence"
          value={lowConfidenceCount}
          subtitle="Text noise / blur"
          icon={AlertTriangle}
          colorTheme="rose"
        />
        <StatCard
          title="Uncertain Answers"
          value={unmatchedAnswerCount}
          subtitle="Key pairing ambiguity"
          icon={HelpCircle}
          colorTheme="indigo"
        />
        <StatCard
          title="Option Anomalies"
          value={optionsUncertainCount}
          subtitle="Non-standard format"
          icon={Sparkles}
          colorTheme="sky"
        />
      </div>

      {/* Review Items Table */}
      <div className="card-panel overflow-hidden bg-white">
        <div className="p-5 border-b border-surface-100 flex items-center justify-between">
          <h3 className="text-base font-bold text-surface-900">Flagged Verification Items</h3>
          <span className="text-xs text-surface-500">{items.length} items in active queue</span>
        </div>

        {isLoading ? (
          <TableSkeleton rows={5} cols={5} />
        ) : items.length === 0 ? (
          <EmptyState
            title="All Clear! No Pending Reviews"
            description="All extracted questions met the high confidence threshold (>= 0.85) and have been auto-approved."
            icon={CheckCircle2}
            actionText="View Questions Explorer"
            onAction={() => navigate('/questions')}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-50 text-surface-500 font-semibold uppercase tracking-wider border-b border-surface-200">
                <tr>
                  <th className="py-3.5 px-4">Issue Type</th>
                  <th className="py-3.5 px-4">Severity</th>
                  <th className="py-3.5 px-4">Description</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100 text-surface-700">
                {items.map((item) => (
                  <tr key={item.id} className="hover:bg-surface-50 transition-colors">
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 text-amber-800 border border-amber-200 text-xs font-semibold">
                        <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
                        {item.issue_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4">
                      <span
                        className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                          item.severity === 'CRITICAL' || item.severity === 'HIGH'
                            ? 'bg-rose-100 text-rose-800'
                            : 'bg-amber-100 text-amber-800'
                        }`}
                      >
                        {item.severity}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 max-w-sm">
                      <p className="truncate text-surface-900 font-medium">{item.issue_description}</p>
                    </td>
                    <td className="py-3.5 px-4 text-surface-400">
                      {new Date(item.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => setSelectedReviewItem(item)}
                        className="btn-primary py-1.5 px-3 text-xs"
                      >
                        Review Question &rarr;
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Review Split-Screen Modal */}
      {selectedReviewItem && (
        <Modal
          isOpen={!!selectedReviewItem}
          onClose={() => setSelectedReviewItem(null)}
          title={`Review Verification Item: ${selectedReviewItem.issue_type}`}
          subtitle={selectedReviewItem.issue_description}
          maxWidth="4xl"
        >
          <div className="space-y-6">
            {/* Warning Banner */}
            <div className="p-3.5 rounded-xl bg-amber-50 border border-amber-200 text-xs text-amber-900 flex items-start gap-2.5">
              <AlertTriangle className="w-4 h-4 text-amber-600 shrink-0 mt-0.5" />
              <div>
                <span className="font-bold">Issue Detected: </span>
                {selectedReviewItem.issue_description}
              </div>
            </div>

            {/* Split Screen */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 items-start">
              {/* Left Side: Document Preview */}
              <div>
                <h4 className="text-xs font-bold text-surface-700 uppercase tracking-wider mb-2">
                  Original Source Document
                </h4>
                {activeDocument ? (
                  <DocumentPreview
                    document={activeDocument}
                    activePageNumber={activeQuestion?.source_pages?.[0] || 1}
                    highlightedQuestionText={activeQuestion?.question_text}
                  />
                ) : (
                  <div className="h-64 bg-surface-100 rounded-xl animate-pulse" />
                )}
              </div>

              {/* Right Side: Extracted Question & Resolution Form */}
              <div className="space-y-4">
                <h4 className="text-xs font-bold text-surface-700 uppercase tracking-wider mb-2">
                  Extracted Question Data
                </h4>

                <div className="p-4 rounded-xl bg-surface-50 border border-surface-200 space-y-3 text-xs">
                  <p className="font-bold text-surface-900 text-sm">
                    {activeQuestion?.question_text || 'Loading stem...'}
                  </p>

                  {activeQuestion?.options && (
                    <div className="space-y-1.5 pt-2 border-t border-surface-200">
                      {activeQuestion.options.map((o: any) => (
                        <div
                          key={o.label}
                          className="flex items-center gap-2 p-1.5 bg-white rounded border border-surface-200"
                        >
                          <span className="w-5 h-5 rounded bg-surface-200 text-surface-700 font-bold flex items-center justify-center text-[10px]">
                            {o.label}
                          </span>
                          <span>{o.option_text}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>

                {/* Resolution Notes Input */}
                <div>
                  <label className="block text-xs font-semibold text-surface-700 mb-1">
                    Reviewer Notes (Optional)
                  </label>
                  <textarea
                    rows={2}
                    value={resolutionNotes}
                    onChange={(e) => setResolutionNotes(e.target.value)}
                    placeholder="Add explanation for verification audit log..."
                    className="w-full p-2.5 text-xs bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500"
                  />
                </div>

                {/* Resolution Actions */}
                <div className="flex flex-wrap items-center justify-end gap-2.5 pt-3 border-t border-surface-100">
                  <button
                    onClick={() =>
                      resolveMutation.mutate({
                        itemId: selectedReviewItem.id,
                        status: 'REJECTED',
                        notes: resolutionNotes,
                      })
                    }
                    disabled={resolveMutation.isPending}
                    className="btn-secondary py-2 px-3 text-xs text-rose-600 hover:bg-rose-50 hover:border-rose-200"
                  >
                    <XCircle className="w-3.5 h-3.5" />
                    Reject Extraction
                  </button>

                  <button
                    onClick={() =>
                      resolveMutation.mutate({
                        itemId: selectedReviewItem.id,
                        status: 'ACCEPTED',
                        notes: resolutionNotes,
                      })
                    }
                    disabled={resolveMutation.isPending}
                    className="btn-primary py-2 px-4 text-xs bg-emerald-600 hover:bg-emerald-700 shadow-xs"
                  >
                    <CheckCircle2 className="w-3.5 h-3.5" />
                    Approve as Verified
                  </button>
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
};
