# Document Processing & Question Extraction Service

A production-oriented, scalable backend service built with **FastAPI**, **PostgreSQL**, **Redis**, and **Celery** for ingesting exam papers, quizzes, question banks, and answer keys in PDF and image formats, performing OCR/layout parsing, extracting questions, options, assets, and answer keys, computing multi-signal confidence scores, and enabling human review workflows.

---

## Features

- **Document Ingestion & Management**
  - Multi-page PDF, JPG, JPEG, and PNG processing.
  - File validation (magic bytes: `%PDF`, `\x89PNG`, `\xFF\xD8\xFF`, max 50MB limit).
  - Cryptographic deduplication (SHA-256) per user.
  - S3-compatible / Local storage abstraction with path traversal security.
- **Robust Processing Pipeline**
  - Multi-stage asynchronous pipeline orchestrated via Celery & Redis.
  - Multi-page extraction via `pypdf` with fallback to pluggable OCR (Tesseract / Mock).
  - EXIF orientation auto-correction and layout normalization (hyphenated word repair, whitespace cleanup, OCR character artifact correction).
  - Pluggable question segmenters: High-accuracy regex Rule-Based Extractor and LLM/AI Extractor.
  - Robust option parsing: Single-line, multi-line, parenthesized `(A)`, inline horizontal `(A) ... (B) ... (C) ... (D)`.
  - Embedded asset & diagram detection (`[Figure 1]`, `[Table 1]`, bounding boxes).
  - Separate & in-document answer key detection and automated ambiguity-aware question-answer matching.
- **Confidence Engine & Human Review**
  - Configurable 5-signal weighted confidence engine ($w_1..w_5$):
    - OCR quality / text density ($0.25$)
    - Question boundary clarity ($0.25$)
    - Option completeness ($0.20$)
    - Answer key match certainty ($0.15$)
    - Layout consistency ($0.15$)
  - Configurable threshold routing (`> 0.85` Auto-approved, `0.60 - 0.85` Needs review, `< 0.60` Low confidence).
  - Review item generation with granular issue codes (`LOW_OCR_CONFIDENCE`, `OPTIONS_UNCERTAIN`, `ANSWER_MATCH_UNCERTAIN`, `MISSING_QUESTION_NUMBER`, etc.).
  - Human review workflow: Accept, Reject, Edit, and Resolution audit tracking.
- **Document Relationships & Versioning**
  - Link question papers with independent answer keys (`PARENT_CHILD`, `ANSWER_KEY`, `VERSION_OF`, `REVISION`).
- **Security & Observability**
  - JWT Bearer Authentication (Access + Refresh tokens).
  - Role-Based Access Control (`admin`, `reviewer`, `user`) & document ownership enforcement.
  - Structured JSON logging with automated credential redaction.
  - Production-ready Alembic migrations and Docker Compose orchestration.

---

## System Architecture

```
                                      +-------------------------+
                                      |   FastAPI REST API      |
                                      | (Auth, Docs, Questions, |
                                      |  Answers, Reviews, Ops) |
                                      +------------+------------+
                                                   |
                        +--------------------------+--------------------------+
                        |                                                     |
             +----------v----------+                               +----------v----------+
             |   PostgreSQL 16     |                               |      Redis 7        |
             | (Documents, Pages,  |                               | (Broker, Result     |
             |  Questions, Reviews)|                               |  Backend, Cache)    |
             +---------------------+                               +----------+----------+
                                                                              |
                                                                   +----------v----------+
                                                                   |    Celery Worker    |
                                                                   | (Multi-stage async  |
                                                                   |  Document Pipeline) |
                                                                   +----------+----------+
                                                                              |
                                                      +-----------------------+-----------------------+
                                                      |                       |                       |
                                             +--------v-------+      +--------v-------+      +--------v-------+
                                             | PyPDF / OCR    |      | Rule/AI        |      | Confidence     |
                                             | Layout Engine  |      | Segmentation   |      | & Review Gen   |
                                             +----------------+      +----------------+      +----------------+
```

---

## Directory Structure

```
.
├── alembic/                      # Database migrations
│   ├── env.py
│   └── versions/                 # Revision scripts
├── app/
│   ├── api/                      # REST API routes and dependencies
│   │   ├── dependencies.py
│   │   └── routes/               # Auth, Docs, Questions, Answers, Reviews, Relationships
│   ├── core/                     # Configuration, Security, Logging, Exceptions
│   ├── db/                       # SQLAlchemy models, session, base repositories
│   ├── processing/               # Extraction & Processing pipeline
│   │   ├── extractors/           # Rule-based & AI question extractors
│   │   ├── ocr/                  # Tesseract & Mock OCR providers
│   │   ├── answer_key_detector.py
│   │   ├── answer_matcher.py
│   │   ├── asset_extractor.py
│   │   ├── confidence_engine.py
│   │   ├── normalizer.py
│   │   ├── option_extractor.py
│   │   ├── page_extractor.py
│   │   ├── pipeline.py
│   │   └── review_generator.py
│   ├── schemas/                  # Pydantic v2 schemas
│   ├── services/                 # Business logic services & Storage service
│   └── workers/                  # Celery application & asynchronous tasks
├── docs/                         # Detailed system documentation
│   ├── architecture.md
│   ├── api.md
│   ├── processing.md
│   └── decisions.md
├── postman/                      # Postman v2.1 API Collection
├── samples/
│   ├── documents/                # Generated realistic sample PDFs and images
│   └── outputs/                  # Sample extracted JSON response
├── tests/                        # 41 Unit & Integration tests
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── README.md
```

---

## Quickstart & Local Setup

### Prerequisites
- Python 3.11+ (or Python 3.12/3.14)
- PostgreSQL 15+ (optional for local SQLite testing)
- Redis 7+ (optional; Celery can run eagerly for tests)
- Tesseract OCR (optional; system falls back gracefully to Mock OCR)

### 1. Clone & Environment Setup

```bash
git clone <repository_url>
cd DocumentService

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Configuration

Create a `.env` file in the root directory:

```env
PROJECT_NAME="Document Processing Service"
ENVIRONMENT=development
DEBUG=true
API_V1_STR=/api/v1
SECRET_KEY=dev-secret-key-at-least-32-chars-long-123456
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database (PostgreSQL in Docker, SQLite fallback for unit tests)
DATABASE_URL=postgresql+psycopg2://postgres:postgres@localhost:5432/doc_processing_db

# Redis & Celery
REDIS_URL=redis://localhost:6379/0
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0

# Storage
STORAGE_BACKEND=local
LOCAL_STORAGE_PATH=./data/storage

# Confidence Thresholds
CONFIDENCE_THRESHOLD_AUTO_APPROVE=0.85
CONFIDENCE_THRESHOLD_REVIEW_REQUIRED=0.60
```

### 3. Run Database Migrations

```bash
alembic upgrade head
```

### 4. Start the Application

Start the FastAPI server:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start the Celery worker (in a separate terminal):
```bash
celery -A app.workers.celery_app.celery_app worker --loglevel=info -P solo
```

Open Interactive Swagger API Docs at: `http://localhost:8000/docs`

---

## Running with Docker Compose

To spin up the complete environment (PostgreSQL, Redis, FastAPI backend, Celery Worker, and Flower monitor):

```bash
# Build and start all services
docker-compose up -d --build

# Inspect logs
docker-compose logs -f backend celery_worker

# Run migrations inside container
docker-compose exec backend alembic upgrade head
```

- API & Swagger Docs: `http://localhost:8000/docs`
- Flower Celery Monitor: `http://localhost:5555`

---

## Running the Test Suite

The test suite contains **41 automated tests** covering security, token revocation, magic byte validation, normalizers, regex segmentation, option formatting, answer matching, confidence formulas, API routes, and end-to-end processing pipeline runs.

```bash
pytest -v
```

To run with coverage:
```bash
pytest --cov=app --cov-report=term-missing
```

---

## Sample Documents & Testing

The repository includes pre-generated realistic sample documents in `samples/documents/`:
1. `computer_science_midterm_exam.pdf`: Multi-page exam with various option formats, inline diagrams, and mixed types.
2. `advanced_algorithms_spanning_question.pdf`: Single-question paper with multi-line options and table layout.
3. `computer_science_answer_key.pdf`: Separate answer key document for testing document relationship matching.
4. `scanned_chemistry_question.png`: Scanned image document for OCR pipeline testing.
5. `low_confidence_sample.pdf`: Degraded document with ambiguous boundaries for review queue testing.

A sample extraction output is available at `samples/outputs/extracted_sample_output.json`.

---

## Postman Collection

Import `postman/Document_Processing_Service.postman_collection.json` into Postman. It includes pre-configured environment variables and requests for:
- User Registration & Authentication (Login, Refresh, Me)
- Document Ingestion (File upload with auto-extracted `document_id`)
- Processing Job Polling & Rerun triggers
- Question Retrieval & Filtering (by confidence, review status, type)
- Answer Key Attachment & Auto-matching
- Human Review Queue & Resolutions (Accept, Reject, Edit)
- Document Relationship Linking (Parent-Child, Answer Key)
- System Health & Monitoring

---

## License

MIT License.
#   Q u e s t i o n E x t r a c t o r  
 