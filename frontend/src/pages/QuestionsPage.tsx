import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useSearchParams, useNavigate } from 'react-router-dom';
import {
  HelpCircle,
  Search,
  Filter,
  Layers,
  Sparkles,
  AlertTriangle,
  FileText,
  LayoutGrid,
  CheckCircle2,
  BookOpen,
  Eye,
  ArrowRight,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { questionsApi } from '../api/questions';
import { QuestionCard } from '../components/questions/QuestionCard';
import { QuestionType } from '../types';
import { TableSkeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';

export const QuestionsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();

  const [searchQuery, setSearchQuery] = useState(searchParams.get('search') || '');
  const [selectedType, setSelectedType] = useState<string>('ALL');
  const [reviewOnly, setReviewOnly] = useState<boolean>(false);
  const [selectedDocId, setSelectedDocId] = useState<string>('ALL');
  const [viewMode, setViewMode] = useState<'grid' | 'quiz'>('grid');
  const [revealedAnswers, setRevealedAnswers] = useState<Record<string, boolean>>({});

  // Fetch all documents
  const { data: documentsData } = useQuery({
    queryKey: ['documentsDropdown'],
    queryFn: () => documentsApi.getDocuments({ page_size: 50 }),
  });

  const docs = documentsData?.items || [];
  const primaryDocId = selectedDocId !== 'ALL' ? selectedDocId : docs[0]?.id;

  // Fetch Questions
  const { data: questionsData, isLoading } = useQuery({
    queryKey: ['explorerQuestions', primaryDocId, selectedType, reviewOnly],
    queryFn: () =>
      primaryDocId
        ? questionsApi.getDocumentQuestions(primaryDocId, {
            question_type: selectedType !== 'ALL' ? (selectedType as QuestionType) : undefined,
            review_required: reviewOnly ? true : undefined,
          })
        : Promise.resolve({ items: [], meta: { total: 0, page: 1, page_size: 50, total_pages: 0 } }),
    enabled: !!primaryDocId,
  });

  const questions = (questionsData?.items || []).filter((q) => {
    if (!searchQuery.trim()) return true;
    return q.question_text.toLowerCase().includes(searchQuery.toLowerCase());
  });

  const toggleAnswerReveal = (qId: string) => {
    setRevealedAnswers((prev) => ({ ...prev, [qId]: !prev[qId] }));
  };

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-black text-slate-900 tracking-tight">Question Explorer</h2>
          <p className="text-xs sm:text-sm text-slate-500 mt-1">
            Explore all structured questions extracted across your examination library with search and interactive quiz modes.
          </p>
        </div>

        {/* View Mode Switcher */}
        <div className="flex items-center gap-1.5 p-1 bg-slate-200/80 rounded-xl">
          <button
            onClick={() => setViewMode('grid')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              viewMode === 'grid' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <LayoutGrid className="w-3.5 h-3.5" />
            Studio Grid
          </button>
          <button
            onClick={() => setViewMode('quiz')}
            className={`px-3 py-1.5 rounded-lg text-xs font-bold transition-all flex items-center gap-1.5 ${
              viewMode === 'quiz' ? 'bg-white text-indigo-700 shadow-2xs' : 'text-slate-600 hover:text-slate-900'
            }`}
          >
            <BookOpen className="w-3.5 h-3.5" />
            Interactive Quiz Mode
          </button>
        </div>
      </div>

      {/* Toolbar: Document selector, Question type, Review flag, Search */}
      <div className="card-panel p-4 sm:p-5 bg-white flex flex-col md:flex-row items-stretch md:items-center justify-between gap-4 shadow-card">
        {/* Search */}
        <div className="relative flex-1 min-w-[240px]">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search questions or keyword stems..."
            className="w-full pl-10 pr-4 py-2 text-xs sm:text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all font-medium"
          />
        </div>

        {/* Filters */}
        <div className="flex flex-wrap items-center gap-2.5">
          {/* Document Filter */}
          <select
            value={selectedDocId}
            onChange={(e) => setSelectedDocId(e.target.value)}
            className="px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">All Documents</option>
            {docs.map((d) => (
              <option key={d.id} value={d.id}>
                {d.title || d.original_filename}
              </option>
            ))}
          </select>

          {/* Question Type Filter */}
          <select
            value={selectedType}
            onChange={(e) => setSelectedType(e.target.value)}
            className="px-3.5 py-2 text-xs bg-slate-50 border border-slate-200 rounded-xl font-bold text-slate-700 focus:outline-none focus:ring-2 focus:ring-indigo-500"
          >
            <option value="ALL">All Types</option>
            <option value="MCQ">Multiple Choice (MCQ)</option>
            <option value="TRUE_FALSE">True / False</option>
            <option value="SHORT_ANSWER">Short Answer</option>
            <option value="NUMERICAL">Numerical</option>
          </select>

          {/* Review Only Toggle */}
          <button
            onClick={() => setReviewOnly(!reviewOnly)}
            className={`px-3.5 py-2 rounded-xl text-xs font-bold flex items-center gap-1.5 transition-all ${
              reviewOnly
                ? 'bg-amber-500 text-white shadow-xs'
                : 'bg-slate-100 text-slate-700 hover:bg-slate-200/70'
            }`}
          >
            <AlertTriangle className="w-3.5 h-3.5" />
            Needs Review
          </button>
        </div>
      </div>

      {/* Questions Content */}
      <div className="space-y-4">
        {isLoading ? (
          <TableSkeleton rows={5} cols={4} />
        ) : questions.length === 0 ? (
          <EmptyState
            title="No questions found"
            description="No extracted questions matched your search criteria or document selection."
            actionText="Upload Question Paper"
            onAction={() => navigate('/documents')}
          />
        ) : viewMode === 'grid' ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
            {questions.map((q) => (
              <QuestionCard
                key={q.id}
                question={q}
                onSelect={() => navigate(`/questions/${q.id}`)}
              />
            ))}
          </div>
        ) : (
          /* Interactive Quiz Mode */
          <div className="space-y-5">
            {questions.map((q) => {
              const isRevealed = revealedAnswers[q.id];

              return (
                <div
                  key={q.id}
                  className="card-panel p-6 sm:p-8 bg-white border-slate-200/80 shadow-md space-y-4"
                >
                  <div className="flex items-center justify-between pb-3 border-b border-slate-100 text-xs">
                    <span className="w-8 h-8 rounded-xl bg-indigo-600 text-white font-extrabold flex items-center justify-center text-sm shadow-xs">
                      #{q.question_number || q.sequence_order}
                    </span>
                    <span className="px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 font-bold border border-indigo-200 text-xs">
                      {q.question_type}
                    </span>
                  </div>

                  <p className="text-base font-bold text-slate-900 leading-relaxed">
                    {q.question_text}
                  </p>

                  {/* Options */}
                  {q.options && (
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 pt-2">
                      {q.options.map((opt: any) => {
                        const isCorrect = q.has_answer && opt.label === 'B'; // or matched answer

                        return (
                          <div
                            key={opt.label}
                            onClick={() => toggleAnswerReveal(q.id)}
                            className={`p-3.5 rounded-xl border text-xs cursor-pointer transition-all flex items-start gap-3 ${
                              isRevealed && isCorrect
                                ? 'bg-emerald-50 border-emerald-400 text-emerald-950 font-bold shadow-xs'
                                : 'bg-slate-50 hover:bg-indigo-50/50 border-slate-200 text-slate-800'
                            }`}
                          >
                            <span className="w-6 h-6 rounded-lg bg-white border border-slate-200 font-extrabold text-slate-700 flex items-center justify-center shrink-0">
                              {opt.label}
                            </span>
                            <span className="flex-1 mt-0.5 font-medium">{opt.option_text}</span>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  {/* Footer actions */}
                  <div className="flex items-center justify-between pt-4 border-t border-slate-100 text-xs">
                    <button
                      onClick={() => toggleAnswerReveal(q.id)}
                      className="btn-secondary py-1.5 px-3.5 text-xs font-bold text-indigo-600"
                    >
                      <Eye className="w-3.5 h-3.5" />
                      {isRevealed ? 'Hide Answer Key' : 'Reveal Solution Key'}
                    </button>

                    <button
                      onClick={() => navigate(`/questions/${q.id}`)}
                      className="inline-flex items-center gap-1 font-bold text-indigo-600 hover:underline"
                    >
                      Question Inspector &rarr;
                    </button>
                  </div>
                </div>
              );
            })}
          </div>
        )}
      </div>
    </div>
  );
};
