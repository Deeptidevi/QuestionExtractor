import { apiClient } from './client';
import { PaginatedResponse, ReviewItem, ReviewStatus } from '../types';

export interface GetReviewQueueParams {
  page?: number;
  page_size?: number;
  document_id?: string;
  status?: ReviewStatus;
}

export interface ResolveReviewParams {
  status: 'ACCEPTED' | 'REJECTED' | 'EDITED';
  notes?: string;
}

export const reviewApi = {
  getReviewQueue: async (params?: GetReviewQueueParams): Promise<PaginatedResponse<ReviewItem>> => {
    const response = await apiClient.get<PaginatedResponse<ReviewItem>>('/review/queue', {
      params,
    });
    return response.data;
  },

  resolveReviewItem: async (
    itemId: string,
    params: ResolveReviewParams
  ): Promise<{ message: string; review_item_id: string; status: string }> => {
    const response = await apiClient.post(`/review/${itemId}/resolve`, params);
    return response.data;
  },
};
