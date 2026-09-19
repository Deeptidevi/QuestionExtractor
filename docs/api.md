# REST API Specification & Reference

Base URL: `/api/v1`

---

## 1. Authentication

### `POST /auth/register`
Register a new user account.

**Request Body:**
```json
{
  "email": "student@example.com",
  "password": "SecurePassword123!",
  "full_name": "Jane Doe"
}
```

**Response (201 Created):**
```json
{
  "id": "c98f9801-1e74-4b44-9dc5-d1420d20d75a",
  "email": "student@example.com",
  "full_name": "Jane Doe",
  "is_active": true,
  "is_superuser": false,
  "created_at": "2026-09-19T21:00:00Z"
}
```

### `POST /auth/login`
Authenticate and obtain a JWT Bearer Token.

**Request (Form URL-Encoded):**
- `username`: `student@example.com`
- `password`: `SecurePassword123!`

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

## 2. Documents

### `POST /documents`
Upload an examination paper or image.

**Headers:**
- `Authorization: Bearer <token>`
- `Content-Type: multipart/form-data`

**Form Data:**
- `file`: Binary file (`.pdf`, `.png`, `.jpg`, `.jpeg`)
- `title` *(optional)*: Custom document name
- `sync_process` *(optional)*: `true` for synchronous execution (e.g. testing)

**Response (202 Accepted):**
```json
{
  "document_id": "e89c6d3f-561b-4f91-888e-c98f9801b702",
  "title": "CS Midterm Exam",
  "original_filename": "exam.pdf",
  "status": "QUEUED",
  "message": "Document uploaded successfully and queued for asynchronous processing"
}
```

### `GET /documents/{document_id}/status`
Check processing status and job progress.

**Response (200 OK):**
```json
{
  "document_id": "e89c6d3f-561b-4f91-888e-c98f9801b702",
  "status": "COMPLETED",
  "total_pages": 2,
  "is_scanned": false,
  "overall_confidence": 0.94,
  "current_job_id": "14743903-68cd-4b15-a0e6-277c96d69623",
  "job_status": "SUCCESS",
  "current_stage": "COMPLETED",
  "progress_percent": 100,
  "error_summary": null,
  "review_required_count": 0,
  "total_questions": 4,
  "updated_at": "2026-09-19T21:00:05Z"
}
```

---

## 3. Extracted Questions

### `GET /documents/{document_id}/questions`
Retrieve paginated structured questions.

**Query Parameters:**
- `page`: Page index (default: `1`)
- `page_size`: Items per page (default: `50`)
- `question_type`: Optional filter (`MCQ`, `TRUE_FALSE`, `SHORT_ANSWER`, etc.)
- `review_required`: Optional boolean filter (`true`/`false`)

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "7b0a8814-1e74-4b44-9dc5-d1420d20d75a",
      "document_id": "e89c6d3f-561b-4f91-888e-c98f9801b702",
      "question_number": "1",
      "sequence_order": 1,
      "question_text": "What is the time complexity of binary search?",
      "question_type": "MCQ",
      "options_count": 4,
      "has_answer": true,
      "answer_value": "B",
      "source_pages": [1],
      "extraction_confidence": 0.97,
      "extraction_status": "SUCCESS",
      "review_required": false,
      "created_at": "2026-09-19T21:00:02Z"
    }
  ],
  "pagination": {
    "page": 1,
    "page_size": 50,
    "total_items": 4,
    "total_pages": 1,
    "has_next": false,
    "has_prev": false
  }
}
```

### `GET /questions/{question_id}`
Retrieve full details of an individual question.

**Response (200 OK):**
```json
{
  "id": "7b0a8814-1e74-4b44-9dc5-d1420d20d75a",
  "document_id": "e89c6d3f-561b-4f91-888e-c98f9801b702",
  "question_number": "1",
  "sequence_order": 1,
  "question_text": "What is the time complexity of binary search on a sorted array of N elements?",
  "raw_text": "1. What is the time complexity of binary search on a sorted array of N elements?\nA. O(1)\nB. O(log N)\nC. O(N)\nD. O(N^2)",
  "question_type": "MCQ",
  "options": [
    {"id": "opt-1", "label": "A", "option_text": "O(1)", "position": 1, "confidence": 1.0},
    {"id": "opt-2", "label": "B", "option_text": "O(log N)", "position": 2, "confidence": 1.0},
    {"id": "opt-3", "label": "C", "option_text": "O(N)", "position": 3, "confidence": 1.0},
    {"id": "opt-4", "label": "D", "option_text": "O(N^2)", "position": 4, "confidence": 1.0}
  ],
  "assets": [],
  "answer": {
    "id": "ans-1",
    "answer_value": "B",
    "raw_answer_text": "1 - B",
    "confidence": 0.95,
    "source_page": 2,
    "match_status": "EXACT_MATCH"
  },
  "source_pages": [1],
  "source_regions": [],
  "extraction_confidence": 0.97,
  "extraction_status": "SUCCESS",
  "review_required": false,
  "created_at": "2026-09-19T21:00:02Z",
  "updated_at": "2026-09-19T21:00:02Z"
}
```

---

## 4. Answers & Review

### `GET /documents/{document_id}/answers`
Retrieve detected answer keys and matching statuses.

### `GET /documents/{document_id}/review-items`
Retrieve warnings, ambiguous items, and review statistics.

### `POST /review-items/{review_item_id}/resolve`
Mark a warning item as resolved.

---

## 5. Document Relationships

### `POST /documents/{document_id}/relationships`
Associate related documents (e.g. Question Paper to separate Answer Key).

**Request Body:**
```json
{
  "target_document_id": "99cc00dd-11ee-22ff-33aa-44bb55cc66dd",
  "relationship_type": "ANSWER_KEY"
}
```

### `GET /documents/{document_id}/relationships`
List all relationships for a document.

### `DELETE /documents/{document_id}/relationships/{related_document_id}`
Unlink an associated document relationship.
