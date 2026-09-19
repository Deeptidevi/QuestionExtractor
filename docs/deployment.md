# Production Deployment Guide

This document details the production deployment procedures for the **Document Processing & Question Extraction Service**.

---

## Architecture Overview

```
                          User / Browser
                               │
                               ▼
               ┌───────────────────────────────┐
               │     Vercel React Frontend     │
               │   (React 19 + TypeScript)     │
               └───────────────┬───────────────┘
                               │ HTTPS (REST API)
                               ▼
               ┌───────────────────────────────┐
               │    Render FastAPI Service     │
               │     (Port $PORT on 0.0.0.0)   │
               └───────┬───────────────┬───────┘
                       │               │
       Direct Database │               │ Async Task Queue
       Queries / ORM   │               │ (Redis)
                       ▼               ▼
        ┌──────────────────┐    ┌─────────────────────┐
        │ Render PostgreSQL│    │ Render Redis/KV     │
        └──────────────────┘    └──────────┬──────────┘
                                           │
                                           │ Worker Processing
                                           ▼
                                ┌─────────────────────┐
                                │Render Celery Worker │
                                │ (PyMuPDF, OCR,      │
                                │  Rule/AI Extraction)│
                                └─────────────────────┘
```

---

## Deployment Strategy Summary

- **Frontend**: Hosted on [Vercel](https://vercel.com) as a Single Page Application (Vite + React 19).
- **API Web Service**: Hosted on [Render](https://render.com) as a Python Web Service.
- **Background Worker**: Hosted on [Render](https://render.com) as a Background Worker running Celery.
- **Database**: Render Managed PostgreSQL.
- **Cache & Queue**: Render Key-Value (Redis-compatible).
- **Storage**: Local persistent storage (development) or S3-compatible cloud object storage (production AWS S3 / Cloudflare R2 / MinIO).

---

## Environment Variables Reference

### Backend Web Service & Celery Worker (Render)

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `APP_ENV` | Application environment | `production` |
| `APP_DEBUG` | Enable debug logs | `false` |
| `DATABASE_URL` | PostgreSQL Connection string | `postgresql://user:pass@host:5432/dbname` |
| `REDIS_URL` | Redis connection string | `rediss://default:pass@host:6379/0` |
| `SECRET_KEY` | JWT signing secret (min 32 chars) | Generated secure random string |
| `FRONTEND_URL` | Production frontend domain | `https://your-app.vercel.app` |
| `BACKEND_CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["https://your-app.vercel.app"]` |
| `STORAGE_BACKEND` | Storage driver (`local` or `s3`) | `local` (or `s3`) |
| `OCR_PROVIDER` | OCR engine (`tesseract` or `mock`) | `tesseract` |
| `EXTRACTION_ENGINE` | Extraction method (`rule_based` / `ai`) | `rule_based` |
| `S3_ENDPOINT` | Optional S3 endpoint URL | `https://s3.us-east-1.amazonaws.com` |
| `S3_BUCKET` | S3 bucket name | `doc-processing-storage` |
| `S3_ACCESS_KEY` | S3 Access Key ID | `AKIAIOSFODNN7EXAMPLE` |
| `S3_SECRET_KEY` | S3 Secret Access Key | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `S3_REGION` | S3 Region | `us-east-1` |

### Frontend (Vercel)

| Variable | Description | Example / Default |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | Production FastAPI base endpoint | `https://doc-extract-api.onrender.com/api/v1` |

---

## Step-by-Step Deployment Guide

### Phase 1: Push Code to GitHub

1. Initialize Git repository (if not already done) and stage files:
   ```bash
   git add .
   git commit -m "feat: complete production-ready document extraction platform"
   ```
2. Set remote and push to `main`:
   ```bash
   git branch -M main
   git remote add origin https://github.com/Deeptidevi/QuestionExtractor.git
   git push -u origin main
   ```

---

### Phase 2: Deploy Backend Infrastructure on Render

You can deploy using Render Blueprints (`render.yaml`) or manually create services in the Render Dashboard.

#### Option A: Using Render Blueprints (`render.yaml`)
1. Log in to [Render Dashboard](https://dashboard.render.com).
2. Click **New +** and select **Blueprint**.
3. Connect your repository `https://github.com/Deeptidevi/QuestionExtractor.git`.
4. Render will detect `render.yaml` and provision:
   - `doc-extract-db` (PostgreSQL)
   - `doc-extract-redis` (Key-Value Redis)
   - `doc-extract-api` (FastAPI Web Service)
   - `doc-extract-worker` (Celery Background Worker)
5. Click **Apply**.

#### Option B: Manual Setup on Render
1. **Create PostgreSQL**:
   - Name: `doc-extract-db`
   - Database: `doc_processing_db`
   - User: `doc_user`
   - Copy internal `DATABASE_URL`.
2. **Create Redis (Key-Value)**:
   - Name: `doc-extract-redis`
   - Copy internal `REDIS_URL`.
3. **Create FastAPI Web Service**:
   - Name: `doc-extract-api`
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - Health Check Path: `/health`
   - Add Environment Variables (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `APP_ENV=production`, `FRONTEND_URL=https://your-frontend.vercel.app`).
4. **Create Celery Background Worker**:
   - Name: `doc-extract-worker`
   - Runtime: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `celery -A app.workers.celery_app worker --loglevel=info`
   - Add Environment Variables (`DATABASE_URL`, `REDIS_URL`, `SECRET_KEY`, `APP_ENV=production`).

---

### Phase 3: Deploy Frontend on Vercel

1. Log in to [Vercel Dashboard](https://vercel.com).
2. Click **Add New...** > **Project**.
3. Import your GitHub repository: `https://github.com/Deeptidevi/QuestionExtractor.git`.
4. Configure Project Settings:
   - **Framework Preset**: Vite
   - **Root Directory**: `frontend`
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
5. Configure Environment Variables:
   - `VITE_API_BASE_URL`: `https://<your-render-backend-url>.onrender.com/api/v1`
6. Click **Deploy**.

---

### Phase 4: Connect & Verify CORS

1. Copy your Vercel deployment URL (e.g. `https://question-extractor.vercel.app`).
2. Update the backend environment variable in Render Dashboard for `doc-extract-api`:
   - `FRONTEND_URL`: `https://question-extractor.vercel.app`
3. Save changes; Render will redeploy the web service with updated CORS allowed origins.

---

## Database Migrations

Alembic migrations run automatically on Web Service startup via:
```bash
alembic upgrade head
```

To run migrations manually via Render Shell:
```bash
alembic upgrade head
```

---

## Production Verification Checklist

- [ ] `GET https://<render-backend>/health` returns `{"status": "HEALTHY"}`.
- [ ] Direct visit to `https://<vercel-frontend>` renders dashboard without console CORS errors.
- [ ] User registration and JWT login generate tokens and persist session in `localStorage`.
- [ ] Direct navigation to `/documents`, `/questions`, `/review`, `/analytics` works on page refresh (Vercel SPA rewrite verified).
- [ ] Uploading a PDF / JPG / PNG triggers background processing with Celery task receipt in worker logs.
- [ ] Extracted questions, answer keys, confidence scores, and review queue items are visible in the frontend.
