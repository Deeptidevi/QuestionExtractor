import { apiClient } from './client';
import { DocumentRelationship, RelationshipType } from '../types';

export interface CreateRelationshipParams {
  source_document_id: string;
  target_document_id: string;
  relationship_type?: RelationshipType;
}

export const relationshipsApi = {
  getDocumentRelationships: async (documentId: string): Promise<DocumentRelationship[]> => {
    try {
      const response = await apiClient.get<{ document_id: string; relationships: DocumentRelationship[] }>(
        `/documents/${documentId}/relationships`
      );
      return response.data?.relationships || [];
    } catch {
      return [];
    }
  },

  createRelationship: async (params: CreateRelationshipParams): Promise<DocumentRelationship> => {
    const response = await apiClient.post<DocumentRelationship>(
      `/documents/${params.source_document_id}/relationships`,
      {
        target_document_id: params.target_document_id,
        relationship_type: params.relationship_type || 'ANSWER_KEY',
      }
    );
    return response.data;
  },

  deleteRelationship: async (
    sourceDocOrRelId: string,
    relatedDocumentId?: string
  ): Promise<{ success: boolean; message: string }> => {
    if (relatedDocumentId) {
      const response = await apiClient.delete(
        `/documents/${sourceDocOrRelId}/relationships/${relatedDocumentId}`
      );
      return response.data;
    }
    const response = await apiClient.delete(`/relationships/${sourceDocOrRelId}`);
    return response.data;
  },
};
