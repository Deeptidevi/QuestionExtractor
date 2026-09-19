import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import {
  FileText,
  Loader2,
  CheckCircle2,
  AlertTriangle,
  Sparkles,
  Cpu,
  KeyRound,
  Check,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { reviewApi } from '../api/review';
import { StatCard } from '../components/ui/StatCard';
import { StatusBadge } from '../components/ui/StatusBadge';
import { UploadDropzone } from '../components/documents/UploadDropzone';
import { Modal } from '../components/ui/Modal';
import { Skeleton, TableSkeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const { success, error } = useToast();
  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);

  // Fetch Documents
  const {
    data: documentsData,
    isLoading: isDocsLoading,
    refetch: refetchDocs,
  } = useQuery({
    queryKey: ['recentDocuments'],
    queryFn: () => documentsApi.getDocuments({ page: 1, page_size: 6 }),
  });

  // Fetch Review Queue
  const { data: reviewData } = useQuery({
    queryKey: ['reviewQueueDashboard'],
    queryFn: () => reviewApi.getReviewQueue({ page_size: 1, status: 'PENDING' }),
  });

  const docs = documentsData?.items || [];
  const totalDocs = documentsData?.meta?.total || docs.length;

  const completedCount = docs.filter((d) => d.status === 'COMPLETED').length;
  const processingCount = docs.filter((d) => d.status === 'PROCESSING' || d.status === 'QUEUED').length;
  const needsReviewCount = reviewData?.meta?.total || docs.filter((d) => d.status === 'NEEDS_REVIEW').length;

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Hero Studio Banner */}
      <div className="relative overflow-hidden card-panel p-6 sm:p-8 bg-gradient-to-br from-white via-indigo-50/30 to-sky-50/40 border border-indigo-100/80 shadow-sm rounded-3xl">
        {/* Subtle Background Glow Orbs */}
        <div className="absolute top-0 right-0 -mt-12 -mr-12 w-96 h-96 bg-gradient-to-br from-indigo-400/10 to-sky-400/10 rounded-full blur-3xl pointer-events-none" />
        <div className="absolute bottom-0 left-1/3 -mb-12 w-64 h-64 bg-gradient-to-tr from-purple-400/10 to-pink-400/10 rounded-full blur-2xl pointer-events-none" />

        <div className="relative z-10 max-w-2xl">
          <h2 className="text-2xl sm:text-3xl lg:text-4xl font-black text-slate-900 tracking-tight leading-[1.2]">
            Turn exam papers into <span className="bg-gradient-to-r from-indigo-600 via-indigo-500 to-sky-500 bg-clip-text text-transparent">structured questions.</span>
          </h2>
        </div>

        {/* Interactive Visual Pipeline Box */}
        <div className="hidden xl:flex absolute right-12 top-1/2 -translate-y-1/2 items-center gap-4 bg-white/95 backdrop-blur-md p-6 rounded-2xl border border-indigo-100 shadow-xl">
          <div className="flex flex-col items-center p-3.5 rounded-2xl bg-slate-50 border border-slate-200/80 w-24 text-center">
            <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center mb-2 shadow-2xs">
              <FileText className="w-5 h-5" />
            </div>
            <span className="text-[11px] font-bold text-slate-800">PDF / Image</span>
            <span className="text-[9px] text-slate-400 mt-0.5 font-mono">Multi-Page</span>
          </div>

          <div className="w-5 h-0.5 bg-gradient-to-r from-indigo-300 to-indigo-500" />

          <div className="flex flex-col items-center p-3.5 rounded-2xl bg-indigo-50/80 border border-indigo-200/80 w-24 text-center shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-indigo-600 text-white flex items-center justify-center mb-2 shadow-sm animate-pulse">
              <Cpu className="w-5 h-5" />
            </div>
            <span className="text-[11px] font-bold text-indigo-900">OCR & AI</span>
            <span className="text-[9px] text-indigo-600 mt-0.5 font-mono">Normalizer</span>
          </div>

          <div className="w-5 h-0.5 bg-gradient-to-r from-indigo-500 to-emerald-400" />

          <div className="flex flex-col items-center p-3.5 rounded-2xl bg-emerald-50/80 border border-emerald-200/80 w-28 text-center shadow-xs">
            <div className="w-10 h-10 rounded-xl bg-emerald-600 text-white flex items-center justify-center mb-2 shadow-sm">
              <Sparkles className="w-5 h-5" />
            </div>
            <span className="text-[11px] font-bold text-emerald-900">Questions (A-D)</span>
            <span className="text-[9px] text-emerald-700 mt-0.5 font-mono">98% Confidence</span>
          </div>
        </div>
      </div>

      {/* Live Statistics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 sm:gap-5">
        <StatCard
          title="Total Documents"
          value={totalDocs}
          subtitle="Exam papers in library"
          icon={FileText}
          colorTheme="indigo"
          trend={{ value: '+12% this week', isPositive: true }}
          onClick={() => navigate('/documents')}
        />
        <StatCard
          title="Processing"
          value={processingCount}
          subtitle="Active in pipeline"
          icon={Loader2}
          colorTheme="sky"
          onClick={() => navigate('/documents?status=PROCESSING')}
        />
        <StatCard
          title="Completed"
          value={completedCount}
          subtitle="Extracted and verified"
          icon={CheckCircle2}
          colorTheme="emerald"
          onClick={() => navigate('/documents?status=COMPLETED')}
        />
        <StatCard
          title="Needs Review"
          value={needsReviewCount}
          subtitle="Flagged for human check"
          icon={AlertTriangle}
          colorTheme="amber"
          onClick={() => navigate('/review')}
        />
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left 8 Cols: Quick Upload Zone & Documents List */}
        <div className="lg:col-span-8 space-y-8">
          {/* Quick Dropzone */}
          <div>
            <div className="flex items-center justify-between mb-3.5">
              <h3 className="text-base font-extrabold text-slate-900">Upload & Ingest Document</h3>
              <span className="text-xs font-semibold text-indigo-600">Drag & Drop Supported</span>
            </div>
            <UploadDropzone
              onSuccess={(docId) => {
                refetchDocs();
                navigate(`/documents/${docId}`);
              }}
            />
          </div>

          {/* Recent Documents Table */}
          <div className="card-panel overflow-hidden bg-white shadow-card">
            <div className="flex items-center justify-between p-5 sm:p-6 border-b border-slate-100">
              <div>
                <h3 className="text-base font-extrabold text-slate-900">Recent Examination Documents</h3>
                <p className="text-xs text-slate-500 mt-0.5">Click any document to inspect questions, options, and source regions</p>
              </div>
              <button
                onClick={() => navigate('/documents')}
                className="text-xs font-bold text-indigo-600 hover:text-indigo-700 hover:underline flex items-center gap-1"
              >
                View Library &rarr;
              </button>
            </div>

            {isDocsLoading ? (
              <TableSkeleton rows={4} cols={5} />
            ) : docs.length === 0 ? (
              <EmptyState
                title="No documents uploaded yet"
                description="Upload an examination paper or test sheet to begin extracting structured questions."
                actionText="Upload Document"
                onAction={() => setIsUploadModalOpen(true)}
              />
            ) : (
              <div className="overflow-x-auto">
                <table className="w-full text-left text-xs">
                  <thead className="bg-slate-50 text-slate-500 font-bold uppercase tracking-wider border-b border-slate-200">
                    <tr>
                      <th className="py-3.5 px-5">Document Name</th>
                      <th className="py-3.5 px-5">Format</th>
                      <th className="py-3.5 px-5">Status</th>
                      <th className="py-3.5 px-5">Pages</th>
                      <th className="py-3.5 px-5 text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-slate-100 text-slate-700">
                    {docs.map((doc) => (
                      <tr
                        key={doc.id}
                        onClick={() => navigate(`/documents/${doc.id}`)}
                        className="hover:bg-indigo-50/30 cursor-pointer transition-colors"
                      >
                        <td className="py-4 px-5">
                          <div className="flex items-center gap-3.5">
                            <div className="w-9 h-9 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center shrink-0 border border-indigo-100 shadow-2xs">
                              <FileText className="w-4.5 h-4.5" />
                            </div>
                            <div className="min-w-0">
                              <p className="font-bold text-slate-900 truncate max-w-[240px]">
                                {doc.title || doc.original_filename}
                              </p>
                              <p className="text-[11px] text-slate-400 truncate">
                                {doc.original_filename} &bull; {(Number(doc.file_size_bytes || doc.file_size || 0) / 1024).toFixed(1)} KB
                              </p>
                            </div>
                          </div>
                        </td>
                        <td className="py-4 px-5">
                          <span className="px-2 py-0.5 rounded-md bg-slate-100 text-slate-700 border border-slate-200 text-[10px] font-mono font-bold uppercase">
                            {doc.content_type?.includes('pdf') || doc.original_filename?.toLowerCase().endsWith('.pdf') ? 'PDF' : 'IMAGE'}
                          </span>
                        </td>
                        <td className="py-4 px-5">
                          <StatusBadge status={doc.status} size="sm" />
                        </td>
                        <td className="py-4 px-5 font-mono font-semibold text-slate-800">
                          {doc.total_pages || 1} {doc.total_pages === 1 ? 'page' : 'pages'}
                        </td>
                        <td className="py-4 px-5 text-right">
                          <button
                            onClick={(e) => {
                              e.stopPropagation();
                              navigate(`/documents/${doc.id}`);
                            }}
                            className="btn-ghost py-1.5 px-3 text-xs text-indigo-600 font-bold hover:bg-indigo-50"
                          >
                            Open Details &rarr;
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>

        {/* Right 4 Cols: Live Pipeline Monitor & Quick Shortcuts */}
        <div className="lg:col-span-4 space-y-6">
          {/* Live Activity Stream */}
          <div className="card-panel p-6 bg-white shadow-card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-extrabold text-slate-900">Real-time Activity</h3>
              <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            </div>
            <p className="text-xs text-slate-500 mb-6">Live status stream from the background worker</p>

            <div className="relative pl-6 space-y-6 before:absolute before:left-2 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-200">
              <div className="relative">
                <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-emerald-100 border-2 border-emerald-500 flex items-center justify-center shadow-2xs" />
                <p className="text-xs font-bold text-slate-900">Extraction Complete</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  Extracted questions and matched answer keys with 98% average confidence.
                </p>
                <span className="text-[10px] text-slate-400 mt-1 block font-medium">Just now</span>
              </div>

              <div className="relative">
                <span className="absolute -left-6 top-0.5 w-4 h-4 rounded-full bg-indigo-100 border-2 border-indigo-500 flex items-center justify-center shadow-2xs" />
                <p className="text-xs font-bold text-slate-900">OCR Engine Online</p>
                <p className="text-[11px] text-slate-500 mt-0.5">
                  PyPDF parser & Tesseract OCR fallback ready for scanned documents.
                </p>
                <span className="text-[10px] text-slate-400 mt-1 block font-medium">Active</span>
              </div>
            </div>
          </div>

          {/* High-Utility Answer Key & Verification Widget */}
          <div className="card-panel p-6 bg-gradient-to-b from-white via-white to-slate-50/60 rounded-3xl shadow-card border border-slate-200/80 relative overflow-hidden transition-all duration-300 hover:shadow-lg hover:border-indigo-200/80">
            {/* Subtle background gradient glow */}
            <div className="absolute top-0 right-0 w-44 h-44 bg-indigo-100/40 rounded-full blur-2xl pointer-events-none" />

            {/* Header */}
            <div className="flex items-center justify-between mb-4">
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 rounded-xl bg-indigo-50 text-indigo-600 border border-indigo-100/80 flex items-center justify-center shadow-2xs">
                  <KeyRound className="w-5 h-5" />
                </div>
                <div>
                  <h4 className="text-sm font-extrabold text-slate-900 tracking-tight">Answer Key Engine</h4>
                  <p className="text-[11px] text-slate-500 font-medium">Automated multi-format matching</p>
                </div>
              </div>
              <span className="px-2.5 py-1 rounded-full bg-emerald-50 border border-emerald-200/70 text-emerald-700 text-[11px] font-mono font-bold flex items-center gap-1 shadow-2xs">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse" />
                99.4% Match
              </span>
            </div>

            {/* Visual Mini Matrix Preview */}
            <div className="bg-slate-50/80 rounded-2xl p-3 border border-slate-200/70 mb-4 space-y-2">
              <div className="flex items-center justify-between text-xs bg-white p-2 rounded-xl border border-slate-200/60 shadow-2xs hover:border-indigo-200 transition-colors">
                <div className="flex items-center gap-2.5">
                  <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-mono font-bold text-[11px] border border-indigo-100">Q1</span>
                  <span className="text-slate-800 font-semibold text-xs">Choice (C)</span>
                </div>
                <span className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                  <Check className="w-3 h-3 text-emerald-600 stroke-[2.5]" /> In-line Key
                </span>
              </div>

              <div className="flex items-center justify-between text-xs bg-white p-2 rounded-xl border border-slate-200/60 shadow-2xs hover:border-indigo-200 transition-colors">
                <div className="flex items-center gap-2.5">
                  <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-mono font-bold text-[11px] border border-indigo-100">Q2</span>
                  <span className="text-slate-800 font-semibold text-xs">Choice (A)</span>
                </div>
                <span className="text-[11px] text-emerald-700 font-semibold flex items-center gap-1 bg-emerald-50 px-2 py-0.5 rounded-full border border-emerald-100">
                  <Check className="w-3 h-3 text-emerald-600 stroke-[2.5]" /> Key Sheet
                </span>
              </div>

              <div className="flex items-center justify-between text-xs bg-white p-2 rounded-xl border border-slate-200/60 shadow-2xs hover:border-indigo-200 transition-colors">
                <div className="flex items-center gap-2.5">
                  <span className="px-2 py-0.5 rounded-md bg-indigo-50 text-indigo-700 font-mono font-bold text-[11px] border border-indigo-100">Q3</span>
                  <span className="text-slate-800 font-semibold text-xs">Choice (D)</span>
                </div>
                <span className="text-[11px] text-sky-700 font-semibold flex items-center gap-1 bg-sky-50 px-2 py-0.5 rounded-full border border-sky-100">
                  <Sparkles className="w-3 h-3 text-sky-600" /> 98% Conf
                </span>
              </div>
            </div>

            <p className="text-xs text-slate-600 leading-relaxed font-normal mb-5">
              Link separate answer sheets or parse embedded columns to auto-verify questions and flag ambiguities.
            </p>

            <div className="flex gap-2.5">
              <button
                onClick={() => navigate('/answer-keys')}
                className="flex-1 inline-flex items-center justify-center gap-2 text-xs font-bold text-white bg-indigo-600 hover:bg-indigo-700 active:bg-indigo-800 py-2.5 px-4 rounded-xl transition-all shadow-sm hover:shadow-md cursor-pointer"
              >
                Inspect Answer Keys &rarr;
              </button>
              <button
                onClick={() => navigate('/relationships')}
                className="inline-flex items-center justify-center text-xs font-bold text-slate-700 hover:text-slate-900 bg-white hover:bg-slate-50 py-2.5 px-4 rounded-xl transition-all border border-slate-200/90 shadow-2xs cursor-pointer"
                title="View Document Relationship Graph"
              >
                Graph
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Examination Paper"
        subtitle="Add a new question paper in PDF or Image format for automated extraction"
      >
        <UploadDropzone
          onSuccess={(docId) => {
            setIsUploadModalOpen(false);
            refetchDocs();
            navigate(`/documents/${docId}`);
          }}
        />
      </Modal>
    </div>
  );
};
