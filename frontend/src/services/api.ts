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
  HealthResponse,
  ConversationResponse,
  ConversationListResponse,
  ConversationDetailResponse,
  ConversationCreateRequest,
  ConversationUpdateRequest,
  ConversationQueryRequest,
  ConversationQueryResponse,
  MessageResponse
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

  // ============ 会话管理相关接口 ============

  /**
   * 创建新会话
   */
  createConversation: async (data: ConversationCreateRequest = {}): Promise<ConversationResponse> => {
    const response = await apiClient.post<ConversationResponse>('/api/conversations', data);
    return response.data;
  },

  /**
   * 获取会话列表
   */
  getConversations: async (skip: number = 0, limit: number = 100): Promise<ConversationListResponse> => {
    const response = await apiClient.get<ConversationListResponse>('/api/conversations', {
      params: { skip, limit }
    });
    return response.data;
  },

  /**
   * 获取会话详情（含消息）
   */
  getConversation: async (conversationId: string): Promise<ConversationDetailResponse> => {
    const response = await apiClient.get<ConversationDetailResponse>(`/api/conversations/${conversationId}`);
    return response.data;
  },

  /**
   * 更新会话标题
   */
  updateConversation: async (
    conversationId: string,
    data: ConversationUpdateRequest
  ): Promise<ConversationResponse> => {
    const response = await apiClient.put<ConversationResponse>(`/api/conversations/${conversationId}`, data);
    return response.data;
  },

  /**
   * 删除会话
   */
  deleteConversation: async (conversationId: string): Promise<DeleteResponse> => {
    const response = await apiClient.delete<DeleteResponse>(`/api/conversations/${conversationId}`);
    return response.data;
  },

  /**
   * 获取会话消息列表
   */
  getMessages: async (conversationId: string): Promise<MessageResponse[]> => {
    const response = await apiClient.get<MessageResponse[]>(`/api/conversations/${conversationId}/messages`);
    return response.data;
  },

  /**
   * 在会话中提问
   */
  queryInConversation: async (
    conversationId: string,
    request: ConversationQueryRequest
  ): Promise<ConversationQueryResponse> => {
    const response = await apiClient.post<ConversationQueryResponse>(
      `/api/conversations/${conversationId}/query`,
      request
    );
    return response.data;
  },
};
