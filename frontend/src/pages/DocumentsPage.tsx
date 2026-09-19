import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate, useSearchParams } from 'react-router-dom';
import {
  FileText,
  UploadCloud,
  Search,
  Filter,
  RefreshCw,
  Trash2,
  Eye,
  MoreHorizontal,
  ChevronLeft,
  ChevronRight,
  Sparkles,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { StatusBadge } from '../components/ui/StatusBadge';
import { Modal } from '../components/ui/Modal';
import { UploadDropzone } from '../components/documents/UploadDropzone';
import { TableSkeleton } from '../components/ui/Skeleton';
import { EmptyState } from '../components/ui/EmptyState';
import { useToast } from '../context/ToastContext';

export const DocumentsPage: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams, setSearchParams] = useSearchParams();
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const [isUploadModalOpen, setIsUploadModalOpen] = useState(false);
  const [selectedStatus, setSelectedStatus] = useState<string>(searchParams.get('status') || 'ALL');
  const [searchQuery, setSearchQuery] = useState('');
  const [page, setPage] = useState(1);

  // Fetch Documents
  const { data, isLoading, refetch } = useQuery({
    queryKey: ['documentsList', selectedStatus, page, searchQuery],
    queryFn: () =>
      documentsApi.getDocuments({
        page,
        page_size: 10,
        status: selectedStatus === 'ALL' ? undefined : selectedStatus,
        search: searchQuery || undefined,
      }),
  });

  // Reprocess Mutation
  const reprocessMutation = useMutation({
    mutationFn: (id: string) => documentsApi.reprocessDocument(id, false),
    onSuccess: (_, id) => {
      success('Reprocessing Started', 'The extraction pipeline has been triggered again.');
      queryClient.invalidateQueries({ queryKey: ['documentsList'] });
    },
    onError: () => {
      error('Reprocess Failed', 'Could not trigger reprocessing.');
    },
  });

  const docs = data?.items || [];
  const meta = data?.meta || { total: docs.length, total_pages: 1, page: 1, page_size: 10 };

  const statuses = [
    { id: 'ALL', label: 'All Documents' },
    { id: 'PROCESSING', label: 'Processing' },
    { id: 'COMPLETED', label: 'Completed' },
    { id: 'NEEDS_REVIEW', label: 'Needs Review' },
    { id: 'FAILED', label: 'Failed' },
  ];

  const handleStatusChange = (statusId: string) => {
    setSelectedStatus(statusId);
    setPage(1);
    if (statusId === 'ALL') {
      searchParams.delete('status');
      setSearchParams(searchParams);
    } else {
      setSearchParams({ status: statusId });
    }
  };

  const formatDate = (isoDate: string) => {
    try {
      const d = new Date(isoDate);
      return d.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      });
    } catch {
      return isoDate;
    }
  };

  return (
    <div className="space-y-6 animate-fade-in pb-12">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">Documents</h2>
          <p className="text-xs sm:text-sm text-surface-500 mt-1">
            Manage uploaded examination papers, track OCR progress, and view extracted question sets.
          </p>
        </div>

        <button
          onClick={() => setIsUploadModalOpen(true)}
          className="btn-primary py-2 px-4 text-sm shrink-0"
        >
          <UploadCloud className="w-4 h-4" />
          + Upload Document
        </button>
      </div>

      {/* Filter Tabs & Search Toolbar */}
      <div className="card-panel p-4 bg-white flex flex-col sm:flex-row items-stretch sm:items-center justify-between gap-4">
        {/* Status Pills */}
        <div className="flex items-center gap-1.5 overflow-x-auto pb-2 sm:pb-0 scrollbar-none">
          {statuses.map((st) => (
            <button
              key={st.id}
              onClick={() => handleStatusChange(st.id)}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold whitespace-nowrap transition-all ${
                selectedStatus === st.id
                  ? 'bg-brand-600 text-white shadow-xs'
                  : 'bg-surface-100 text-surface-600 hover:bg-surface-200/80 hover:text-surface-900'
              }`}
            >
              {st.label}
            </button>
          ))}
        </div>

        {/* Search */}
        <div className="relative min-w-[240px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-surface-400" />
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Filter by title..."
            className="w-full pl-9 pr-4 py-1.5 text-xs bg-surface-50 border border-surface-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-brand-500 focus:bg-white transition-all"
          />
        </div>
      </div>

      {/* Document Table */}
      <div className="card-panel overflow-hidden bg-white">
        {isLoading ? (
          <TableSkeleton rows={6} cols={6} />
        ) : docs.length === 0 ? (
          <EmptyState
            title="No documents found"
            description={
              selectedStatus !== 'ALL'
                ? `There are currently no documents matching status "${selectedStatus}".`
                : 'Upload your first document to extract questions.'
            }
            actionText="Upload Document"
            onAction={() => setIsUploadModalOpen(true)}
          />
        ) : (
          <div>
            <div className="overflow-x-auto">
              <table className="w-full text-left text-xs">
                <thead className="bg-surface-50 text-surface-500 font-semibold uppercase tracking-wider border-b border-surface-200">
                  <tr>
                    <th className="py-3.5 px-4">Document</th>
                    <th className="py-3.5 px-4">Format</th>
                    <th className="py-3.5 px-4">Status</th>
                    <th className="py-3.5 px-4">Pages</th>
                    <th className="py-3.5 px-4">Uploaded Date</th>
                    <th className="py-3.5 px-4 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-surface-100 text-surface-700">
                  {docs.map((doc) => (
                    <tr
                      key={doc.id}
                      onClick={() => navigate(`/documents/${doc.id}`)}
                      className="hover:bg-surface-50/80 cursor-pointer transition-colors"
                    >
                      <td className="py-3.5 px-4">
                        <div className="flex items-center gap-3">
                          <div className="w-9 h-9 rounded-xl bg-brand-50 text-brand-600 flex items-center justify-center shrink-0 border border-brand-100">
                            <FileText className="w-4 h-4" />
                          </div>
                          <div className="min-w-0">
                            <p className="font-semibold text-surface-900 truncate max-w-[260px]">
                              {doc.title || doc.original_filename}
                            </p>
                              <p className="text-[11px] text-surface-400 truncate">
                                {doc.original_filename} &bull; {(Number(doc.file_size_bytes || doc.file_size || 0) / 1024).toFixed(1)} KB
                              </p>
                          </div>
                        </div>
                      </td>
                      <td className="py-3.5 px-4">
                        <span className="px-2 py-0.5 rounded bg-surface-100 text-surface-700 border border-surface-200 text-[10px] font-mono uppercase">
                          {doc.content_type?.includes('pdf') || doc.original_filename?.toLowerCase().endsWith('.pdf') ? 'PDF' : 'IMAGE'}
                        </span>
                      </td>
                      <td className="py-3.5 px-4">
                        <StatusBadge status={doc.status} size="sm" />
                      </td>
                      <td className="py-3.5 px-4 font-mono">
                        {doc.total_pages || 1} {doc.total_pages === 1 ? 'page' : 'pages'}
                      </td>
                      <td className="py-3.5 px-4 text-surface-500">
                        {formatDate(doc.created_at)}
                      </td>
                      <td className="py-3.5 px-4 text-right">
                        <div className="flex items-center justify-end gap-1.5" onClick={(e) => e.stopPropagation()}>
                          <button
                            onClick={() => reprocessMutation.mutate(doc.id)}
                            title="Reprocess Extraction"
                            className="p-1.5 rounded-lg text-surface-400 hover:text-brand-600 hover:bg-surface-100 transition-colors"
                          >
                            <RefreshCw className="w-4 h-4" />
                          </button>
                          <button
                            onClick={() => navigate(`/documents/${doc.id}`)}
                            className="btn-ghost py-1 px-2.5 text-xs text-brand-600 font-medium"
                          >
                            Open &rarr;
                          </button>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            {/* Pagination */}
            {meta.total_pages > 1 && (
              <div className="flex items-center justify-between p-4 border-t border-surface-100 bg-surface-50/50 text-xs">
                <span className="text-surface-500">
                  Showing Page {meta.page} of {meta.total_pages} ({meta.total} items)
                </span>
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => setPage(Math.max(1, page - 1))}
                    disabled={page <= 1}
                    className="btn-secondary py-1 px-2 text-xs"
                  >
                    <ChevronLeft className="w-3.5 h-3.5" />
                    Prev
                  </button>
                  <button
                    onClick={() => setPage(Math.min(meta.total_pages, page + 1))}
                    disabled={page >= meta.total_pages}
                    className="btn-secondary py-1 px-2 text-xs"
                  >
                    Next
                    <ChevronRight className="w-3.5 h-3.5" />
                  </button>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Upload Modal */}
      <Modal
        isOpen={isUploadModalOpen}
        onClose={() => setIsUploadModalOpen(false)}
        title="Upload Examination Document"
        subtitle="Add a new PDF or image paper to your library"
      >
        <UploadDropzone
          onSuccess={(docId) => {
            setIsUploadModalOpen(false);
            refetch();
            navigate(`/documents/${docId}`);
          }}
        />
      </Modal>
    </div>
  );
};
