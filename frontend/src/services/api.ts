/**
 * API 服务
 */
import axios from 'axios';
import type {
  DocumentUploadResponse,
  QueryRequest,
  QueryResponse,
  DocumentListResponse,
  DeleteResponse,
  HealthResponse
} from '../types/api';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  timeout: 60000,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const api = {
  /**
   * 上传文档
   */
  uploadDocument: async (file: File): Promise<DocumentUploadResponse> => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await apiClient.post<DocumentUploadResponse>(
      '/api/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * 问答查询
   */
  query: async (request: QueryRequest): Promise<QueryResponse> => {
    const response = await apiClient.post<QueryResponse>('/api/query', request);
    return response.data;
  },

  /**
   * 获取文档列表
   */
  getDocuments: async (): Promise<DocumentListResponse> => {
    const response = await apiClient.get<DocumentListResponse>('/api/documents');
    return response.data;
  },

  /**
   * 删除文档
   */
  deleteDocument: async (documentId: string): Promise<DeleteResponse> => {
    const response = await apiClient.delete<DeleteResponse>(`/api/documents/${documentId}`);
    return response.data;
  },

  /**
   * 健康检查
   */
  health: async (): Promise<HealthResponse> => {
    const response = await apiClient.get<HealthResponse>('/api/health');
    return response.data;
  },
};
