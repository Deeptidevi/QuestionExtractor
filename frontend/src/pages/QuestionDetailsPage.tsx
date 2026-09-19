import React, { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  ArrowLeft,
  HelpCircle,
  CheckCircle2,
  AlertTriangle,
  FileText,
  KeyRound,
  Sparkles,
  Edit3,
  Save,
  X,
  Layers,
  Table as TableIcon,
  Image as ImageIcon,
} from 'lucide-react';
import { questionsApi } from '../api/questions';
import { documentsApi } from '../api/documents';
import { ConfidenceBadge } from '../components/ui/ConfidenceBadge';
import { DocumentPreview } from '../components/documents/DocumentPreview';
import { Skeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';

export const QuestionDetailsPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const [isEditing, setIsEditing] = useState(false);
  const [editedText, setEditedText] = useState('');
  const [editedNumber, setEditedNumber] = useState('');

  // 1. Fetch Question Detail
  const {
    data: question,
    isLoading: isQuestionLoading,
    refetch,
  } = useQuery({
    queryKey: ['questionDetail', id],
    queryFn: () => questionsApi.getQuestion(id!),
    enabled: !!id,
  });

  // 2. Fetch Parent Document for Left Preview
  const { data: document } = useQuery({
    queryKey: ['parentDocument', question?.document_id],
    queryFn: () => documentsApi.getDocument(question!.document_id),
    enabled: !!question?.document_id,
  });

  // Update Mutation
  const updateMutation = useMutation({
    mutationFn: (params: any) => questionsApi.updateQuestion(id!, params),
    onSuccess: () => {
      success('Question Updated', 'Your edits have been saved to the database.');
      setIsEditing(false);
      queryClient.invalidateQueries({ queryKey: ['questionDetail', id] });
    },
    onError: () => {
      error('Update Failed', 'Could not update question.');
    },
  });

  const handleStartEdit = () => {
    if (question) {
      setEditedText(question.question_text);
      setEditedNumber(question.question_number || '');
      setIsEditing(true);
    }
  };

  const handleSaveEdit = () => {
    updateMutation.mutate({
      question_text: editedText,
      question_number: editedNumber || undefined,
    });
  };

  if (isQuestionLoading) {
    return (
      <div className="space-y-6 animate-fade-in p-6">
        <Skeleton className="h-8 w-64" />
        <div className="grid grid-cols-2 gap-6">
          <Skeleton className="h-96 w-full" />
          <Skeleton className="h-96 w-full" />
        </div>
      </div>
    );
  }

  if (!question) {
    return (
      <EmptyState
        title="Question Not Found"
        description="The requested question could not be found."
        actionText="Back to Questions"
        onAction={() => navigate('/questions')}
      />
    );
  }

  return (
    <div className="space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 pb-4 border-b border-surface-200">
        <div>
          <button
            onClick={() => navigate(-1)}
            className="inline-flex items-center gap-1.5 text-xs font-semibold text-surface-500 hover:text-surface-900 transition-colors mb-2"
          >
            <ArrowLeft className="w-4 h-4" />
            Back
          </button>

          <div className="flex flex-wrap items-center gap-3">
            <h2 className="text-xl sm:text-2xl font-extrabold text-surface-900 tracking-tight">
              Question #{question.question_number || question.sequence_order}
            </h2>
            <ConfidenceBadge score={question.extraction_confidence || 0.95} />
            <span className="px-2.5 py-1 rounded-full bg-brand-50 text-brand-700 border border-brand-200 text-xs font-semibold">
              {question.question_type}
            </span>
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex items-center gap-2.5">
          {!isEditing ? (
            <button onClick={handleStartEdit} className="btn-secondary py-2 px-3 text-xs">
              <Edit3 className="w-3.5 h-3.5" />
              Edit Question
            </button>
          ) : (
            <>
              <button
                onClick={() => setIsEditing(false)}
                className="btn-secondary py-2 px-3 text-xs"
              >
                <X className="w-3.5 h-3.5" />
                Cancel
              </button>
              <button
                onClick={handleSaveEdit}
                disabled={updateMutation.isPending}
                className="btn-primary py-2 px-3 text-xs"
              >
                <Save className="w-3.5 h-3.5" />
                Save Changes
              </button>
            </>
          )}
        </div>
      </div>

      {/* Warnings Banner if review required */}
      {question.review_required && (
        <div className="p-4 rounded-xl bg-amber-50 border border-amber-200/80 flex items-start gap-3">
          <AlertTriangle className="w-5 h-5 text-amber-600 shrink-0 mt-0.5" />
          <div className="text-xs text-amber-900">
            <h4 className="font-bold">Human Review Recommended</h4>
            <p className="mt-0.5 opacity-90">
              This question was flagged due to low OCR density or uncertain answer key pairing. Please verify the stem and option correctness against the original document.
            </p>
          </div>
        </div>
      )}

      {/* Main Split Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side: Document Page Viewer */}
        <div className="lg:col-span-6 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-sm font-bold text-surface-900">Source Document Region</h3>
            <span className="text-xs text-surface-500">
              Page {question.source_pages?.[0] || 1}
            </span>
          </div>

          {document ? (
            <DocumentPreview
              document={document}
              activePageNumber={question.source_pages?.[0] || 1}
              highlightedQuestionText={`${question.question_number ? `Q${question.question_number}. ` : ''}${question.question_text}`}
            />
          ) : (
            <Skeleton className="h-96 w-full" />
          )}
        </div>

        {/* Right Side: Question Data, Options & Matched Solution */}
        <div className="lg:col-span-6 space-y-6">
          {/* Question Stem Card */}
          <div className="card-panel p-6 bg-white space-y-4">
            <h3 className="text-xs font-bold uppercase tracking-wider text-surface-400">
              Question Content
            </h3>

            {isEditing ? (
              <div className="space-y-3">
                <div>
                  <label className="block text-xs font-semibold text-surface-700 mb-1">
                    Question Number
                  </label>
                  <input
                    type="text"
                    value={editedNumber}
                    onChange={(e) => setEditedNumber(e.target.value)}
                    className="w-28 px-3 py-1.5 text-xs bg-surface-50 border border-surface-200 rounded-lg focus:ring-2 focus:ring-brand-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-surface-700 mb-1">
                    Question Stem
                  </label>
                  <textarea
                    rows={4}
                    value={editedText}
                    onChange={(e) => setEditedText(e.target.value)}
                    className="w-full p-3 text-sm bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500"
                  />
                </div>
              </div>
            ) : (
              <p className="text-base font-semibold text-surface-900 leading-relaxed">
                {question.question_text}
              </p>
            )}

            {/* Options List */}
            {question.options && question.options.length > 0 && (
              <div className="pt-3 border-t border-surface-100 space-y-2.5">
                <h4 className="text-xs font-bold uppercase tracking-wider text-surface-400">
                  Multiple Choice Options
                </h4>
                <div className="space-y-2">
                  {question.options.map((opt) => {
                    const isCorrect =
                      question.answer?.answer_value === opt.label ||
                      opt.is_correct === true;

                    return (
                      <div
                        key={opt.id || opt.label}
                        className={`flex items-start gap-3 p-3 rounded-xl border text-xs transition-all ${
                          isCorrect
                            ? 'bg-emerald-50 border-emerald-300 text-emerald-950 font-medium shadow-2xs'
                            : 'bg-surface-50 border-surface-200/80 text-surface-800'
                        }`}
                      >
                        <span
                          className={`w-6 h-6 rounded-lg flex items-center justify-center font-bold text-xs shrink-0 ${
                            isCorrect
                              ? 'bg-emerald-600 text-white'
                              : 'bg-surface-200 text-surface-700'
                          }`}
                        >
                          {opt.label}
                        </span>
                        <div className="flex-1 min-w-0">
                          <p>{opt.option_text}</p>
                        </div>
                        {isCorrect && (
                          <span className="text-[11px] font-bold text-emerald-700 uppercase tracking-wide">
                            Correct Answer
                          </span>
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}

            {/* Matched Answer Card */}
            {question.answer && (
              <div className="pt-3 border-t border-surface-100">
                <div className="p-4 rounded-xl bg-gradient-to-r from-emerald-50 to-teal-50 border border-emerald-200 flex items-start justify-between gap-3 text-xs">
                  <div>
                    <div className="flex items-center gap-1.5 text-emerald-800 font-bold">
                      <CheckCircle2 className="w-4 h-4 text-emerald-600" />
                      Matched Answer Key
                    </div>
                    <p className="text-sm font-extrabold text-emerald-950 mt-1">
                      Option [{question.answer.answer_value}]
                    </p>
                    {question.answer.raw_answer_text && (
                      <p className="text-[11px] text-emerald-700 mt-0.5">
                        Raw Source: "{question.answer.raw_answer_text}"
                      </p>
                    )}
                  </div>
                  <span className="px-2 py-0.5 rounded bg-emerald-100 text-emerald-800 font-semibold text-[10px]">
                    {question.answer.match_status}
                  </span>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
