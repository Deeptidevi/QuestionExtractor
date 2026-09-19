// Common API pagination & response types
export interface PaginationMeta {
  total?: number;
  total_items?: number;
  page: number;
  page_size: number;
  total_pages: number;
  has_next?: boolean;
  has_prev?: boolean;
}

export interface PaginatedResponse<T> {
  items: T[];
  pagination?: PaginationMeta;
  meta?: PaginationMeta;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface ApiResponse<T = any> {
  data?: T;
  error?: ApiError;
}

// User & Auth Types
export type UserRole = 'admin' | 'reviewer' | 'user';

export interface User {
  id: string;
  email: string;
  full_name: string;
  is_active: boolean;
  is_superuser?: boolean;
  created_at: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token?: string;
  token_type: string;
  expires_in?: number;
}

// Document Types
export type DocumentStatus =
  | 'UPLOADED'
  | 'QUEUED'
  | 'PROCESSING'
  | 'COMPLETED'
  | 'COMPLETED_WITH_WARNINGS'
  | 'FAILED'
  | 'NEEDS_REVIEW'
  | 'PARTIAL';

export interface Document {
  id: string;
  title: string;
  original_filename: string;
  mime_type?: string;
  content_type?: string;
  file_size?: number;
  file_size_bytes?: number;
  file_hash?: string;
  total_pages: number;
  is_scanned?: boolean;
  status: DocumentStatus;
  overall_confidence?: number | null;
  processing_error?: string;
  created_at: string;
  updated_at: string;
  total_questions?: number;
  pages?: DocumentPage[];
}

export interface DocumentUploadResponse {
  document_id: string;
  title: string;
  original_filename: string;
  status: DocumentStatus;
  message: string;
}

export interface DocumentPage {
  id: string;
  page_number: number;
  width?: number;
  height?: number;
  has_images: boolean;
  ocr_applied: boolean;
  text_length: number;
}

// Question & Option Types
export type QuestionType = 'MCQ' | 'TRUE_FALSE' | 'FILL_IN_BLANK' | 'SHORT_ANSWER' | 'NUMERICAL' | 'DESCRIPTIVE' | 'MATCHING';
export type ExtractionStatus = 'SUCCESS' | 'PARTIAL' | 'AMBIGUOUS' | 'FAILED';

export interface QuestionOption {
  id?: string;
  label: string;
  option_text: string;
  position: number;
  is_correct?: boolean;
  confidence: number;
}

export interface QuestionAsset {
  id?: string;
  asset_type: 'FIGURE' | 'DIAGRAM' | 'TABLE' | 'CHART' | 'EQUATION' | 'OTHER';
  storage_path: string;
  source_page: number;
  bbox?: number[];
  caption?: string;
  confidence: number;
}

export interface MatchedAnswerSummary {
  id?: string;
  answer_value?: string;
  raw_answer_text?: string;
  confidence: number;
  source_page?: number;
  match_status: 'EXACT_MATCH' | 'FUZZY_MATCH' | 'AMBIGUOUS' | 'UNMATCHED' | 'MANUAL_OVERRIDE';
}

export interface Question {
  id: string;
  document_id: string;
  question_number?: string;
  sequence_order: number;
  question_text: string;
  raw_text?: string;
  question_type: QuestionType;
  options: QuestionOption[];
  assets: QuestionAsset[];
  answer?: MatchedAnswerSummary;
  source_pages: number[];
  source_regions?: any[];
  extraction_confidence: number;
  extraction_status: ExtractionStatus;
  review_required: boolean;
  created_at: string;
  updated_at: string;
}

export interface QuestionListItem {
  id: string;
  document_id: string;
  question_number?: string;
  sequence_order: number;
  question_text: string;
  question_type: QuestionType;
  options_count: number;
  options?: QuestionOption[];
  has_answer: boolean;
  extraction_confidence: number;
  extraction_status: ExtractionStatus;
  review_required: boolean;
  source_pages: number[];
  created_at: string;
}

// Answer Types
export interface AnswerDetail {
  id: string;
  document_id: string;
  question_id?: string;
  question_number?: string;
  answer_value: string;
  raw_answer_text?: string;
  explanation?: string;
  confidence: number;
  source_page?: number;
  match_status: string;
  created_at: string;
}

export interface DocumentAnswersResponse {
  document_id: string;
  total_answers: number;
  matched_answers_count: number;
  unmatched_answers_count: number;
  answers: AnswerDetail[];
}

// Review Types
export type ReviewSeverity = 'INFO' | 'WARNING' | 'CRITICAL' | 'LOW' | 'MEDIUM' | 'HIGH';
export type ReviewStatus = 'PENDING' | 'ACCEPTED' | 'REJECTED' | 'EDITED' | 'RESOLVED' | 'UNRESOLVED';

export interface ReviewItem {
  id: string;
  document_id: string;
  question_id?: string | null;
  warning_type?: string;
  issue_type?: string;
  severity: ReviewSeverity;
  status?: ReviewStatus;
  is_resolved?: boolean;
  message?: string;
  issue_description?: string;
  source_page?: number | null;
  confidence?: number | null;
  details?: Record<string, any>;
  resolution_notes?: string;
  created_at: string;
  resolved_at?: string;
  question?: Question;
  document_title?: string;
}

export interface DocumentReviewSummaryResponse {
  document_id: string;
  total_review_items: number;
  unresolved_items: number;
  critical_count: number;
  warning_count: number;
  info_count: number;
  items: ReviewItem[];
}

// Relationship Types
export type RelationshipType = 'PARENT_CHILD' | 'ANSWER_KEY' | 'VERSION_OF' | 'REVISION';

export interface DocumentRelationship {
  id: string;
  source_document_id: string;
  target_document_id: string;
  relationship_type: RelationshipType;
  metadata?: Record<string, any>;
  created_at: string;
  target_document_title?: string;
  target_document_status?: DocumentStatus;
}
