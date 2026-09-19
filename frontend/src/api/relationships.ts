import { apiClient } from './client';
import { DocumentRelationship, RelationshipType } from '../types';

export interface CreateRelationshipParams {
  source_document_id: string;
  target_document_id: string;
  relationship_type: RelationshipType;
  metadata?: Record<string, any>;
}

export const relationshipsApi = {
  getDocumentRelationships: async (documentId: string): Promise<DocumentRelationship[]> => {
    const response = await apiClient.get<DocumentRelationship[]>(
      `/relationships/document/${documentId}`
    );
    return response.data;
  },

  createRelationship: async (params: CreateRelationshipParams): Promise<DocumentRelationship> => {
    const response = await apiClient.post<DocumentRelationship>('/relationships', params);
    return response.data;
  },

  deleteRelationship: async (relationshipId: string): Promise<{ success: boolean; message: string }> => {
    const response = await apiClient.delete(`/relationships/${relationshipId}`);
    return response.data;
  },
};
