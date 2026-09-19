import React from 'react';
import { Question, QuestionListItem, QuestionType } from '../../types';
import { ConfidenceBadge } from '../ui/ConfidenceBadge';
import {
  HelpCircle,
  FileText,
  CheckCircle2,
  AlertTriangle,
  Layers,
  Sparkles,
  ArrowRight,
  Table as TableIcon,
  Image as ImageIcon,
} from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface QuestionCardProps {
  question: Question | QuestionListItem | any;
  onSelect?: () => void;
  isSelected?: boolean;
  compact?: boolean;
}

export const QuestionCard: React.FC<QuestionCardProps> = ({
  question,
  onSelect,
  isSelected = false,
  compact = false,
}) => {
  const navigate = useNavigate();

  const typeLabels: Record<string, { label: string; color: string }> = {
    MCQ: { label: 'Multiple Choice', color: 'bg-indigo-50 text-indigo-700 border-indigo-200' },
    TRUE_FALSE: { label: 'True / False', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
    FILL_IN_BLANK: { label: 'Fill in Blank', color: 'bg-amber-50 text-amber-700 border-amber-200' },
    SHORT_ANSWER: { label: 'Short Answer', color: 'bg-sky-50 text-sky-700 border-sky-200' },
    NUMERICAL: { label: 'Numerical', color: 'bg-purple-50 text-purple-700 border-purple-200' },
    DESCRIPTIVE: { label: 'Descriptive', color: 'bg-slate-100 text-slate-700 border-slate-200' },
    MATCHING: { label: 'Matching', color: 'bg-teal-50 text-teal-700 border-teal-200' },
  };

  const typeConfig = typeLabels[question.question_type] || {
    label: question.question_type || 'Question',
    color: 'bg-slate-100 text-slate-700 border-slate-200',
  };

  const pages = question.source_pages || [question.page_start || 1];
  const pageText = pages.length > 1 ? `Pages ${pages[0]}–${pages[pages.length - 1]}` : `Page ${pages[0] || 1}`;

  return (
    <div
      onClick={onSelect}
      className={`card-panel-hover p-6 transition-all duration-300 relative ${
        isSelected
          ? 'border-indigo-500 ring-2 ring-indigo-200 bg-indigo-50/20 shadow-md'
          : 'hover:border-indigo-200'
      } ${onSelect ? 'cursor-pointer' : ''}`}
    >
      {/* Top Meta Header */}
      <div className="flex flex-wrap items-center justify-between gap-2 pb-3.5 mb-3.5 border-b border-slate-100 text-xs">
        <div className="flex items-center gap-2">
          <span className="w-7 h-7 rounded-xl bg-slate-900 text-white font-extrabold text-xs flex items-center justify-center shadow-2xs">
            {question.question_number || question.sequence_order || '#'}
          </span>
          <span className={`px-2.5 py-1 rounded-lg border text-[11px] font-bold ${typeConfig.color}`}>
            {typeConfig.label}
          </span>
          <span className="px-2.5 py-1 rounded-lg bg-slate-100 text-slate-700 border border-slate-200 text-[11px] font-semibold">
            {pageText}
          </span>
        </div>

        <div className="flex items-center gap-2">
          {question.review_required && (
            <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-amber-50 border border-amber-200 text-amber-800 text-[11px] font-bold">
              <AlertTriangle className="w-3.5 h-3.5 text-amber-600" />
              Review Flagged
            </span>
          )}
          <ConfidenceBadge score={question.extraction_confidence || 0.95} size="sm" />
        </div>
      </div>

      {/* Stem Content */}
      <p className="text-sm font-semibold text-slate-900 leading-relaxed line-clamp-3 mb-4">
        {question.question_text}
      </p>

      {/* Options preview */}
      {question.options && question.options.length > 0 && !compact && (
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2.5 mt-4 pt-3.5 border-t border-slate-100">
          {question.options.map((opt: any) => {
            const isAnswer =
              question.answer?.answer_value === opt.label ||
              opt.is_correct === true;

            return (
              <div
                key={opt.id || opt.label}
                className={`flex items-start gap-2.5 p-2.5 rounded-xl text-xs transition-all border ${
                  isAnswer
                    ? 'bg-emerald-50/90 border-emerald-300 text-emerald-950 font-semibold shadow-2xs'
                    : 'bg-slate-50/80 border-slate-200 text-slate-700'
                }`}
              >
                <span
                  className={`w-5.5 h-5.5 rounded-lg flex items-center justify-center font-bold text-[11px] shrink-0 ${
                    isAnswer ? 'bg-emerald-600 text-white shadow-2xs' : 'bg-slate-200 text-slate-700'
                  }`}
                >
                  {opt.label}
                </span>
                <span className="truncate flex-1 mt-0.5">{opt.option_text}</span>
              </div>
            );
          })}
        </div>
      )}

      {/* Assets & Footer */}
      <div className="flex items-center justify-between mt-4 pt-3 border-t border-slate-100 text-xs text-slate-400">
        <div className="flex items-center gap-2">
          {question.assets && question.assets.length > 0 && (
            <span className="inline-flex items-center gap-1 text-[11px] font-bold text-slate-700 bg-slate-100 px-2.5 py-1 rounded-lg">
              <ImageIcon className="w-3.5 h-3.5 text-indigo-600" />
              {question.assets.length} Asset{question.assets.length > 1 ? 's' : ''}
            </span>
          )}
          {question.answer?.answer_value && (
            <span className="inline-flex items-center gap-1.5 text-[11px] font-bold text-emerald-800 bg-emerald-50 px-2.5 py-1 rounded-lg border border-emerald-200">
              <CheckCircle2 className="w-3.5 h-3.5 text-emerald-600" />
              Key: [{question.answer.answer_value}]
            </span>
          )}
        </div>

        <button
          onClick={(e) => {
            e.stopPropagation();
            navigate(`/questions/${question.id}`);
          }}
          className="inline-flex items-center gap-1 text-indigo-600 hover:text-indigo-700 font-bold hover:underline text-xs"
        >
          View Full Details
          <ArrowRight className="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  );
};
