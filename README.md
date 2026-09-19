# QuestionExtractor — Document Processing & Question Extraction Service

A full-stack, production-grade cloud platform for automated examination paper ingestion, OCR layout parsing, structured question extraction, options and figure parsing, answer key matching, 5-signal confidence scoring, and human review workflows.

---

## Live Deployment URLs

| Service | Target Platform | URL |
| :--- | :--- | :--- |
| **Frontend Dashboard** | Vercel | `https://questionextractor.vercel.app` (Placeholder) |
| **FastAPI REST API** | Render Web Service | `https://questionextractor-api.onrender.com` (Placeholder) |
| **Interactive Swagger Docs** | Render Web Service | `https://questionextractor-api.onrender.com/docs` (Placeholder) |
| **System Health Status** | Render Web Service | `https://questionextractor-api.onrender.com/health` (Placeholder) |

---

## System Architecture

```
User / Web Browser
       │
       ▼
┌─────────────────────────────────────────────────────────────┐
│                 Vercel React Frontend                       │
│    (React 19, TypeScript, Tailwind CSS, TanStack Query)     │
└──────────────────────────────┬──────────────────────────────┘
                               │ HTTPS REST API requests
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 Render FastAPI Web Service                  │
│       (Port $PORT on 0.0.0.0, JWT Auth, Ingestion API)      │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
Direct DB ORM  │                               │ Async Job Queue
Queries        │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌─────────────────────────────┐
│      Render PostgreSQL       │ │   Render Key-Value Redis    │
│ (Documents, Pages, Questions,│ │(Broker, Results, Task Queue)│
│  Reviews, Answer Keys, Users)│ └─────────────┬───────────────┘
└──────────────────────────────┘               │
                                               │ Background processing
                                               ▼
                                 ┌─────────────────────────────┐
                                 │Render Celery Worker Process │
                                 │ (PyMuPDF, Tesseract OCR,    │
                                 │  Rule & AI Question Parser, │
                                 │  5-Signal Confidence Engine)│
                                 └─────────────────────────────┘
```

---

## Tech Stack

### Frontend
- **Framework**: React 19 + TypeScript + Vite
- **Styling**: Tailwind CSS v4 + Lucide Icons
- **State & Data Fetching**: TanStack Query (React Query v5) + Axios
- **Routing**: React Router v7 (with SPA rewrites for Vercel)
- **Deployment**: Vercel

### Backend
- **Framework**: FastAPI (Python 3.11 / 3.12)
- **Database & ORM**: PostgreSQL + SQLAlchemy 2.0 + Alembic migrations
- **Task Queue & Cache**: Celery 5 + Redis (Render Key-Value)
- **Document & OCR Engine**: PyMuPDF (`fitz`), Pillow, PyTesseract
- **Storage**: Storage abstraction supporting Local Disk & S3-compatible cloud object storage (AWS S3, Cloudflare R2, MinIO)
- **Authentication**: JWT Bearer Tokens with bcrypt password hashing
- **Deployment**: Render Web Service + Render Background Worker

---

## Local Development

### 1. Prerequisites
- Python 3.11+
- Node.js 18+ and npm
- PostgreSQL 15+ and Redis 7+ (or Docker)

### 2. Backend Setup

```bash
# 1. Clone repository
git clone https://github.com/Deeptidevi/QuestionExtractor.git
cd QuestionExtractor

# 2. Setup Python environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env

# 4. Run database migrations
alembic upgrade head

# 5. Start FastAPI development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# 6. Start Celery worker (in a separate terminal)
celery -A app.workers.celery_app worker --loglevel=info -P solo
```

The backend is now accessible at `http://localhost:8000` (Swagger docs: `http://localhost:8000/docs`).

### 3. Frontend Setup

```bash
cd frontend

# 1. Install dependencies
npm install

# 2. Configure environment
cp .env.example .env.local
# VITE_API_BASE_URL=http://localhost:8000/api/v1

# 3. Start Vite dev server
npm run dev
```

The frontend dashboard will be available at `http://localhost:5173`.

### 4. Running with Docker Compose

```bash
docker-compose up -d --build
```
- Frontend: `http://localhost:5173`
- Backend Swagger: `http://localhost:8000/docs`
- Flower Celery Monitor: `http://localhost:5555`

---

## Production Deployment Guide

### Phase 1: Push Repository to GitHub

```bash
git add .
git commit -m "feat: production deployment configuration for Render and Vercel"
git branch -M main
git remote add origin https://github.com/Deeptidevi/QuestionExtractor.git
git push -u origin main
```

---

### Phase 2: Deploy Backend Infrastructure on Render

#### Option A: One-Click Render Blueprint (`render.yaml`)
1. Go to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** > **Blueprint**.
3. Connect repository `https://github.com/Deeptidevi/QuestionExtractor.git`.
4. Render provisions:
   - `doc-extract-db` (PostgreSQL)
   - `doc-extract-redis` (Key-Value Redis)
   - `doc-extract-api` (FastAPI Web Service)
   - `doc-extract-worker` (Celery Background Worker)
5. Click **Apply**.

#### Option B: Manual Service Creation
1. **PostgreSQL**: Create a Render PostgreSQL database (`doc-extract-db`).
2. **Redis**: Create a Render Redis / Key-Value instance (`doc-extract-redis`).
3. **Web Service**:
   - **Name**: `doc-extract-api`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Health Check Path**: `/health`
   - **Environment Variables**:
     - `DATABASE_URL`: *(from Render PostgreSQL)*
     - `REDIS_URL`: *(from Render Redis)*
     - `SECRET_KEY`: *(Generate random 32-character string)*
     - `APP_ENV`: `production`
     - `APP_DEBUG`: `false`
     - `FRONTEND_URL`: `https://your-frontend.vercel.app`
4. **Background Worker**:
   - **Name**: `doc-extract-worker`
   - **Runtime**: `Python`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `celery -A app.workers.celery_app worker --loglevel=info`
   - **Environment Variables**: Same `DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `APP_ENV=production`.

---

### Phase 3: Deploy Frontend on Vercel

1. Log in to [Vercel](https://vercel.com).
2. Click **Add New...** > **Project** and import `Deeptidevi/QuestionExtractor`.
3. Configure Build Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
4. Add Environment Variable:
   - `VITE_API_BASE_URL`: `https://<your-render-backend-url>.onrender.com/api/v1`
5. Click **Deploy**.

---

### Phase 4: Configure CORS

1. Copy your assigned Vercel URL (e.g. `https://questionextractor.vercel.app`).
2. Open Render Dashboard -> `doc-extract-api` -> **Environment**.
3. Set `FRONTEND_URL` to `https://questionextractor.vercel.app`.
4. Click **Save Changes** to redeploy the API with active CORS authorization.

---

## Automated Verification & Testing

Run the 41-test automated suite:
```bash
pytest -v
```

Build the production frontend bundle:
```bash
cd frontend && npm run build
```

---

## License

MIT License.