import { apiClient } from './client';
import {
  Document,
  DocumentPage,
  DocumentUploadResponse,
  PaginatedResponse,
} from '../types';

export interface GetDocumentsParams {
  page?: number;
  page_size?: number;
  status?: string;
  search?: string;
}

export interface UploadDocumentParams {
  file: File;
  title?: string;
  sync_process?: boolean;
}

export const documentsApi = {
  getDocuments: async (params?: GetDocumentsParams): Promise<PaginatedResponse<Document>> => {
    const response = await apiClient.get<PaginatedResponse<Document>>('/documents', {
      params,
    });
    return response.data;
  },

  getDocument: async (id: string): Promise<Document> => {
    const response = await apiClient.get<Document>(`/documents/${id}`);
    return response.data;
  },

  getDocumentStatus: async (id: string): Promise<{ document_id: string; status: string; total_pages: number; total_questions: number; updated_at: string }> => {
    const response = await apiClient.get(`/documents/${id}/status`);
    return response.data;
  },

  uploadDocument: async (params: UploadDocumentParams): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', params.file);
    if (params.title) {
      formData.append('title', params.title);
    }
    if (params.sync_process !== undefined) {
      formData.append('sync_process', String(params.sync_process));
    }

    const response = await apiClient.post<DocumentUploadResponse>('/documents', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  reprocessDocument: async (id: string, force_ocr = false): Promise<{ message: string; document_id: string }> => {
    const response = await apiClient.post(`/documents/${id}/reprocess`, null, {
      params: { force_ocr },
    });
    return response.data;
  },

  getDocumentPages: async (id: string): Promise<DocumentPage[]> => {
    const response = await apiClient.get<DocumentPage[]>(`/documents/${id}/pages`);
    return response.data;
  },
};
