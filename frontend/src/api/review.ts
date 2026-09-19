import { apiClient } from './client';
import { Document, DocumentReviewSummaryResponse, PaginatedResponse, ReviewItem } from '../types';

export interface GetReviewQueueParams {
  page?: number;
  page_size?: number;
  document_id?: string;
  status?: string;
}

export interface ResolveReviewParams {
  status?: 'ACCEPTED' | 'REJECTED' | 'EDITED';
  is_resolved?: boolean;
  notes?: string;
  resolution_note?: string;
}

export const reviewApi = {
  getDocumentReviewItems: async (
    documentId: string,
    params?: { unresolved_only?: boolean; severity?: string }
  ): Promise<DocumentReviewSummaryResponse> => {
    const response = await apiClient.get<DocumentReviewSummaryResponse>(
      `/documents/${documentId}/review-items`,
      { params }
    );
    return response.data;
  },

  getReviewQueue: async (
    params?: GetReviewQueueParams
  ): Promise<{ items: ReviewItem[]; meta: { total: number } }> => {
    if (params?.document_id) {
      try {
        const summary = await reviewApi.getDocumentReviewItems(params.document_id, {
          unresolved_only: true,
        });
        return { items: summary.items || [], meta: { total: summary.unresolved_items || 0 } };
      } catch {
        return { items: [], meta: { total: 0 } };
      }
    }

    try {
      const docsRes = await apiClient.get<PaginatedResponse<Document>>('/documents', {
        params: { page: 1, page_size: 20 },
      });
      const docs = docsRes.data?.items || [];
      const summaries = await Promise.all(
        docs.map((doc) =>
          reviewApi
            .getDocumentReviewItems(doc.id, { unresolved_only: true })
            .catch(() => ({ items: [], unresolved_items: 0 }))
        )
      );
      const allItems = summaries.flatMap((s) => s.items || []);
      return { items: allItems, meta: { total: allItems.length } };
    } catch {
      return { items: [], meta: { total: 0 } };
    }
  },

  resolveReviewItem: async (
    itemId: string,
    params: ResolveReviewParams
  ): Promise<ReviewItem> => {
    const response = await apiClient.post<ReviewItem>(`/review-items/${itemId}/resolve`, {
      is_resolved: params.is_resolved !== undefined ? params.is_resolved : true,
      resolution_note: params.resolution_note || params.notes || 'Resolved via review queue',
    });
    return response.data;
  },
};
