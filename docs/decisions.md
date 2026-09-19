# Architectural & Technical Decision Records (ADR)

## 1. OCR Engine Choice: Tesseract + PyTesseract with Mock Fallback
- **Selected**: Tesseract OCR via `pytesseract` with `BaseOCRProvider` abstraction.
- **Alternatives Considered**: EasyOCR, AWS Textract, Google Cloud Vision.
- **Rationale**: Tesseract provides an open-source, offline, and containerizable OCR engine that runs locally inside Docker without recurring API costs or cloud vendor lock-in. The `BaseOCRProvider` interface allows external vision APIs to be plugged in effortlessly.
- **Trade-offs**: Tesseract can struggle with low-contrast, heavily degraded scans, which is why our confidence engine computes OCR word confidence and flags `LOW_OCR_CONFIDENCE` for human review.

---

## 2. PDF Parsing Choice: PyPDF / Native Text Stream Extraction
- **Selected**: `pypdf` for native page extraction and text density analysis.
- **Alternatives Considered**: `pdfplumber`, `PyMuPDF (fitz)`.
- **Rationale**: `pypdf` is pure Python, cross-platform, robust, and has zero native compiler dependencies on Windows / Linux / macOS.
- **Trade-offs**: Does not extract vector layout paths directly, but combined with our OCR engine and geometry analyzer, it provides high reliability across environments.

---

## 3. Question Extraction Architecture: Multi-Pattern Regex & State Machine with AI Fallback
- **Selected**: Hybrid architecture with `RuleBasedExtractor` primary and pluggable `AIQuestionExtractor` with strict Pydantic structured output validation.
- **Alternatives Considered**: Pure End-to-End LLM, Single Fixed Regex.
- **Rationale**: Pure LLM extraction incurs latency, cost, and token limits on 50-page exam papers. A rule-based parser handles standard examinations in milliseconds with deterministic results, while the AI extractor handles complex unformatted documents.
- **Trade-offs**: Rule-based parsers require comprehensive regex coverage, which is why our implementation handles 10+ numbering and option formats.

---

## 4. Asynchronous Processing: Celery + Redis
- **Selected**: `Celery` task queue with `Redis` message broker and result backend.
- **Alternatives Considered**: `RQ`, `FastAPI BackgroundTasks`.
- **Rationale**: `FastAPI BackgroundTasks` runs in the same web process and can block the event loop with heavy CPU OCR tasks. Celery provides horizontal scaling, separate worker pools, retries, and task state tracking.

---

## 5. Storage Layer: Pluggable `BaseStorageService` with `LocalStorageService`
- **Selected**: Filesystem abstraction with SHA-256 integrity hashing and UUID namespace isolation.
- **Alternatives Considered**: Direct BLOB storage in PostgreSQL.
- **Rationale**: Large binary PDFs and images cause database bloat and slow backups. The abstraction allows local development without external dependencies, while remaining 100% compatible with S3/GCS in cloud production.
