/**
 * API 服务类型定义
 */

export interface DocumentUploadResponse {
  document_id: string;
  filename: string;
  file_size: number;
  chunks_count: number;
  message: string;
}

export interface QueryRequest {
  question: string;
  top_k?: number;
}

export interface SourceDocument {
  content: string;
  filename: string;
  page: number | null;
  score: number;
}

export interface QueryResponse {
  answer: string;
  sources: SourceDocument[];
  question: string;
}

export interface DocumentInfo {
  document_id: string;
  filename: string;
  file_size: number;
  upload_time: string;
  chunks_count: number;
}

export interface DocumentListResponse {
  documents: DocumentInfo[];
  total: number;
}

export interface DeleteResponse {
  message: string;
  document_id: string;
}

export interface HealthResponse {
  status: string;
  version: string;
  vectordb_status: string;
  documents_count: number;
}
