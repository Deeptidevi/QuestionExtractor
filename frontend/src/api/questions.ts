import { apiClient } from './client';
import {
  PaginatedResponse,
  Question,
  QuestionListItem,
  QuestionType,
} from '../types';

export interface GetQuestionsParams {
  page?: number;
  page_size?: number;
  question_type?: QuestionType;
  review_required?: boolean;
}

export interface UpdateQuestionParams {
  question_text?: string;
  question_number?: string;
  question_type?: QuestionType;
  review_required?: boolean;
}

export const questionsApi = {
  getDocumentQuestions: async (
    documentId: string,
    params?: GetQuestionsParams
  ): Promise<PaginatedResponse<QuestionListItem>> => {
    const response = await apiClient.get<PaginatedResponse<QuestionListItem>>(
      `/documents/${documentId}/questions`,
      { params }
    );
    return response.data;
  },

  getQuestion: async (id: string): Promise<Question> => {
    const response = await apiClient.get<Question>(`/questions/${id}`);
    return response.data;
  },

  updateQuestion: async (id: string, params: UpdateQuestionParams): Promise<Question> => {
    const response = await apiClient.patch<Question>(`/questions/${id}`, params);
    return response.data;
  },
};
