# System Architecture & Technical Design

## 1. High-Level Architecture Overview

The **Document Processing & Question Extraction Service** is a modular, event-driven backend service designed to ingest examination papers, question banks, and answer keys in PDF or image format, convert them into structured questions, and deliver normalized JSON representations to downstream assessment platforms.

```
+-------------------------------------------------------------------------+
|                              CLIENT LAYER                               |
|        (Web App / Exam Platform / Postman / Automated Ingestion)        |
+-------------------------------------------------------------------------+
                                    |
                                    | REST API (JWT Bearer, Versioned /v1)
                                    v
+-------------------------------------------------------------------------+
|                              FASTAPI APP                                |
|  - Request Validation (Pydantic v2)                                     |
|  - File Security & Signature Check (FileValidator)                      |
|  - Authentication & RBAC (Jose JWT, Bcrypt)                             |
|  - Storage Abstraction (LocalStorageService / S3)                       |
+-------------------------------------------------------------------------+
           |                                             |
           | Sync Storage / DB Writes                    | Dispatches Async Task
           v                                             v
+-----------------------+                    +-----------------------+
|      POSTGRESQL       |                    |     REDIS BROKER      |
| - Users               |                    | - Task Queue          |
| - Documents & Pages   |                    | - Rate Limiter State  |
| - Questions & Options |                    +-----------------------+
| - Answers & Assets    |                                |
| - Review Items        |                                v
| - Relationships       |                    +-----------------------+
+-----------------------+                    |  CELERY ASYNC WORKER  |
           ^                                 | (Multi-worker pool)   |
           |                                 +-----------------------+
           |                                             |
           +---------------- Pipeline DB Commits --------+
                                                         |
                                                         v
                                  +---------------------------------------+
                                  |      DOCUMENT PROCESSING PIPELINE     |
                                  | 1. Page Extraction (PyPDF/PyMuPDF)    |
                                  | 2. OCR & Normalization (Tesseract)    |
                                  | 3. Question Segmentation              |
                                  | 4. Option Extraction                  |
                                  | 5. Asset & Table Association          |
                                  | 6. Answer Key Detection & Matching    |
                                  | 7. Multi-Signal Confidence Scoring    |
                                  | 8. Review Warning Generation          |
                                  | 9. Transactional DB Persistence       |
                                  +---------------------------------------+
```

---

## 2. Component Breakdown

### A. API Layer (FastAPI)
- **Asynchronous Execution**: Uploads return immediately (`202 Accepted`) with a tracking `document_id`. Heavy OCR and parsing runs non-blocking in Celery background workers.
- **Dependency Injection**: Database sessions, current authenticated user, and repositories are injected via `Depends(get_db)` and `Depends(get_current_user)`.
- **Centralized Exception Handling**: Structured error responses with unique error codes (`RESOURCE_NOT_FOUND`, `INVALID_FILE`, `AUTHENTICATION_FAILED`, `UNSUPPORTED_FILE_TYPE`).

### B. Persistent Database (PostgreSQL)
- Schema managed with **Alembic** migrations.
- UUID primary keys across all tables for secure identifier distribution.
- Normalized models with cascading foreign key deletions (`ON DELETE CASCADE`) to prevent orphaned artifacts upon document removal.
- Indexed columns on `user_id`, `status`, `question_number`, `document_id` for efficient pagination and filtering.

### C. Asynchronous Worker Architecture (Celery + Redis)
- **Decoupled Processing**: Ingestion throughput is never throttled by expensive CPU OCR tasks.
- **Idempotency**: Processing tasks clear previously extracted artifacts before writing new ones, ensuring safe retries without creating duplicated questions.
- **Granular Progress**: Jobs update progress percentage (10% to 100%) and current stage names in real time.

### D. File Storage Abstraction
- Defined by `BaseStorageService` with a production-ready `LocalStorageService`.
- **Path Traversal Protection**: Rejects `../` relative exploits.
- **File Hashing**: Computes SHA-256 hashes during chunked stream writes for deduplication and integrity auditing.
- Easily swappable for Amazon S3 / Google Cloud Storage without altering business logic.

---

## 3. The Extraction Pipeline Stages

1. **File Validation**: Validates MIME type, binary magic signature (`%PDF`, `\x89PNG`, `\xFF\xD8\xFF`), and size constraints (up to 50MB).
2. **Page Extraction**: Extracts digital native text and geometry (width, height, rotation) per page.
3. **Normalization**:
   - Transposes EXIF rotation for scanned/camera images.
   - Collapses excessive whitespace and joins hyphenated line breaks.
   - Cleans common OCR mistranscriptions (`l.` -> `1.`, `(0)` -> `(D)`).
4. **OCR Fallback**: Automatically evaluates digital text density. If density is low or the file is an image, runs Tesseract OCR and extracts word-level confidence.
5. **Question Segmentation**: Evaluates multi-style numbering patterns (`1.`, `Q1.`, `Question 1:`, `1)`, `1:`, unnumbered questions) across multi-page boundaries.
6. **Option Extraction**: Identifies and separates choices (`A.`, `(a)`, `1.`, inline formats) from question stems.
7. **Asset Association**: Isolates figure and table references and links them to preceding questions.
8. **Answer Key Detection & Matching**: Parses answer sections/grids, correlates detected answers against extracted questions, and validates option bounds.
9. **Confidence Engine**: Calculates a 5-signal weighted score (Numbering, Options, Text Quality, Boundaries, Continuity).
10. **Review Generation**: Generates typed warnings (`LOW_OCR_CONFIDENCE`, `QUESTION_CONTINUES_NEXT_PAGE`, `OPTIONS_UNCERTAIN`, `ANSWER_MATCH_UNCERTAIN`, `PARTIAL_EXTRACTION`).
11. **Persistence**: Saves entities in a single atomic database transaction.
