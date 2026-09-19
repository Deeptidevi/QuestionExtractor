import { apiClient } from './client';
import { DocumentAnswersResponse } from '../types';

export const answersApi = {
  getDocumentAnswers: async (documentId: string): Promise<DocumentAnswersResponse> => {
    const response = await apiClient.get<DocumentAnswersResponse>(
      `/documents/${documentId}/answers`
    );
    return response.data;
  },
};
