import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  GitFork,
  FileText,
  Plus,
  Trash2,
  KeyRound,
  ArrowRight,
  Layers,
  Sparkles,
} from 'lucide-react';
import { documentsApi } from '../api/documents';
import { relationshipsApi } from '../api/relationships';
import { Modal } from '../components/ui/Modal';
import { EmptyState } from '../components/ui/EmptyState';
import { TableSkeleton } from '../components/ui/Skeleton';
import { useToast } from '../context/ToastContext';
import { RelationshipType } from '../types';

export const RelationshipsPage: React.FC = () => {
  const queryClient = useQueryClient();
  const { success, error } = useToast();

  const [isLinkModalOpen, setIsLinkModalOpen] = useState(false);
  const [sourceDocId, setSourceDocId] = useState('');
  const [targetDocId, setTargetDocId] = useState('');
  const [relType, setRelType] = useState<RelationshipType>('ANSWER_KEY');

  // Fetch all documents
  const { data: documentsData } = useQuery({
    queryKey: ['relDocuments'],
    queryFn: () => documentsApi.getDocuments({ page_size: 50 }),
  });

  const docs = documentsData?.items || [];
  const primaryDocId = sourceDocId || docs[0]?.id;

  // Fetch relationships for active doc
  const { data: relationships, isLoading } = useQuery({
    queryKey: ['relationships', primaryDocId],
    queryFn: () => (primaryDocId ? relationshipsApi.getDocumentRelationships(primaryDocId) : Promise.resolve([])),
    enabled: !!primaryDocId,
  });

  // Create Relationship Mutation
  const createRelMutation = useMutation({
    mutationFn: () =>
      relationshipsApi.createRelationship({
        source_document_id: primaryDocId,
        target_document_id: targetDocId,
        relationship_type: relType,
      }),
    onSuccess: () => {
      success('Relationship Created', 'Documents have been linked successfully.');
      setIsLinkModalOpen(false);
      setTargetDocId('');
      queryClient.invalidateQueries({ queryKey: ['relationships'] });
    },
    onError: () => {
      error('Linking Failed', 'Could not link documents.');
    },
  });

  // Delete Relationship Mutation
  const deleteRelMutation = useMutation({
    mutationFn: (relId: string) => relationshipsApi.deleteRelationship(relId),
    onSuccess: () => {
      success('Unlinked', 'Document relationship removed.');
      queryClient.invalidateQueries({ queryKey: ['relationships'] });
    },
    onError: () => {
      error('Unlink Failed', 'Could not remove relationship.');
    },
  });

  const relList = relationships || [];

  return (
    <div className="space-y-8 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h2 className="text-xl sm:text-2xl font-bold text-surface-900 tracking-tight">
            Document Relationships
          </h2>
          <p className="text-xs sm:text-sm text-surface-500 mt-1">
            Link independent question papers with external answer keys, parent-child sections, or revisions.
          </p>
        </div>

        <button
          onClick={() => setIsLinkModalOpen(true)}
          disabled={docs.length < 2}
          className="btn-primary py-2 px-4 text-xs sm:text-sm"
        >
          <Plus className="w-4 h-4" />
          + Link Documents
        </button>
      </div>

      {/* Select Source Document Toolbar */}
      <div className="card-panel p-4 bg-white flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <FileText className="w-5 h-5 text-brand-600 shrink-0" />
          <div>
            <label className="block text-[11px] font-bold uppercase tracking-wider text-surface-400">
              Select Primary Document
            </label>
            <select
              value={primaryDocId}
              onChange={(e) => setSourceDocId(e.target.value)}
              className="text-sm font-semibold text-surface-900 bg-transparent focus:outline-none cursor-pointer"
            >
              {docs.map((d) => (
                <option key={d.id} value={d.id}>
                  {d.title || d.original_filename}
                </option>
              ))}
            </select>
          </div>
        </div>
      </div>

      {/* Relationships Table / List */}
      <div className="card-panel overflow-hidden bg-white">
        <div className="p-5 border-b border-surface-100 flex items-center justify-between">
          <h3 className="text-base font-bold text-surface-900">Linked Documents</h3>
          <span className="text-xs text-surface-500">{relList.length} active relationships</span>
        </div>

        {isLoading ? (
          <TableSkeleton rows={3} cols={4} />
        ) : relList.length === 0 ? (
          <EmptyState
            title="No Linked Documents"
            description="This document is not currently linked to any answer keys or related revisions."
            actionText="Link a Related Document"
            onAction={() => setIsLinkModalOpen(true)}
          />
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead className="bg-surface-50 text-surface-500 font-semibold uppercase tracking-wider border-b border-surface-200">
                <tr>
                  <th className="py-3.5 px-4">Relationship</th>
                  <th className="py-3.5 px-4">Target Document</th>
                  <th className="py-3.5 px-4">Created Date</th>
                  <th className="py-3.5 px-4 text-right">Actions</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-surface-100 text-surface-700">
                {relList.map((rel) => (
                  <tr key={rel.id} className="hover:bg-surface-50">
                    <td className="py-3.5 px-4">
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full bg-brand-50 text-brand-700 border border-brand-200 text-xs font-semibold">
                        <GitFork className="w-3.5 h-3.5" />
                        {rel.relationship_type}
                      </span>
                    </td>
                    <td className="py-3.5 px-4 font-semibold text-surface-900">
                      {rel.target_document_title || rel.target_document_id}
                    </td>
                    <td className="py-3.5 px-4 text-surface-400">
                      {new Date(rel.created_at).toLocaleDateString()}
                    </td>
                    <td className="py-3.5 px-4 text-right">
                      <button
                        onClick={() => deleteRelMutation.mutate(rel.id)}
                        className="p-1.5 rounded-lg text-surface-400 hover:text-rose-600 hover:bg-rose-50"
                        title="Unlink"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Link Modal */}
      <Modal
        isOpen={isLinkModalOpen}
        onClose={() => setIsLinkModalOpen(false)}
        title="Link Related Documents"
        subtitle="Associate an external answer key or parent paper"
      >
        <div className="space-y-4 text-xs">
          <div>
            <label className="block font-semibold text-surface-700 mb-1">Target Document</label>
            <select
              value={targetDocId}
              onChange={(e) => setTargetDocId(e.target.value)}
              className="w-full p-2.5 bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500"
            >
              <option value="">Select target document...</option>
              {docs
                .filter((d) => d.id !== primaryDocId)
                .map((d) => (
                  <option key={d.id} value={d.id}>
                    {d.title || d.original_filename}
                  </option>
                ))}
            </select>
          </div>

          <div>
            <label className="block font-semibold text-surface-700 mb-1">Relationship Type</label>
            <select
              value={relType}
              onChange={(e) => setRelType(e.target.value as RelationshipType)}
              className="w-full p-2.5 bg-surface-50 border border-surface-200 rounded-xl focus:ring-2 focus:ring-brand-500"
            >
              <option value="ANSWER_KEY">Answer Key (Solution document)</option>
              <option value="PARENT_CHILD">Parent-Child (Section or Part)</option>
              <option value="VERSION_OF">Version Of (Alternative version)</option>
              <option value="REVISION">Revision (Updated edition)</option>
            </select>
          </div>

          <div className="flex justify-end gap-2.5 pt-4 border-t border-surface-100">
            <button onClick={() => setIsLinkModalOpen(false)} className="btn-secondary py-2 px-3 text-xs">
              Cancel
            </button>
            <button
              onClick={() => createRelMutation.mutate()}
              disabled={!targetDocId || createRelMutation.isPending}
              className="btn-primary py-2 px-4 text-xs"
            >
              Confirm & Link
            </button>
          </div>
        </div>
      </Modal>
    </div>
  );
};
