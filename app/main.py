import time
from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.core.config import settings
from app.core.exceptions import AppException
from app.core.logging import logger
from app.api.routes import (
    auth_router,
    documents_router,
    questions_router,
    answers_router,
    review_router,
    relationships_router,
)

app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="""
## Production Document Processing & Question Extraction Service

Accepts **PDFs, JPGs, JPEGs, and PNGs** (examination papers, question banks, answer keys) and extracts structured, machine-readable questions, choices, answers, and confidence indicators.

### Key Capabilities:
- **Multi-layout & format resilience**: Robust across varied numbering styles (1., Q1, Question 1:, 1), 1:) and option formats.
- **Cross-page continuity**: Automatically aggregates multiline questions that span consecutive pages.
- **Answer key detection & matching**: Extracts inline, column, or standalone answer keys with ambiguity validation.
- **Multi-signal confidence scoring**: Weighted evaluation of numbering, options, text quality, boundary clarity, and continuity.
- **Actionable human review workflows**: Flags ambiguous, unnumbered, or low-confidence extractions with structured warnings.
- **Document relationship graph**: Link separate question papers and answer key documents.
    """,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc",
)

# Dynamic CORS Configuration
allowed_origins = list(settings.BACKEND_CORS_ORIGINS)
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request timing & Logging Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration_ms = round((time.time() - start_time) * 1000, 2)
    response.headers["X-Process-Time-Ms"] = str(duration_ms)
    return response


# Centralized Exception Handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(l) for l in err.get("loc", [])])
        errors.append({"field": loc, "message": err.get("msg"), "type": err.get("type")})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "Input validation failed. Please check your request parameters.",
                "details": {"validation_errors": errors},
            }
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled system exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred while processing your request.",
                "details": {},
            }
        },
    )


from fastapi.responses import HTMLResponse, RedirectResponse

# Landing Page & Health Check
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def root_dashboard():
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{settings.APP_NAME} - Dashboard</title>
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg: #0b0f19;
                --card-bg: rgba(22, 30, 49, 0.85);
                --card-border: rgba(255, 255, 255, 0.1);
                --primary: #6366f1;
                --primary-hover: #4f46e5;
                --accent: #10b981;
                --text-main: #f3f4f6;
                --text-muted: #9ca3af;
            }}
            * {{ box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }}
            body {{
                background: radial-gradient(circle at 50% 0%, #1e1b4b 0%, #0b0f19 75%);
                color: var(--text-main);
                min-height: 100vh;
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                padding: 24px;
            }}
            .container {{
                max-width: 860px;
                width: 100%;
                background: var(--card-bg);
                backdrop-filter: blur(16px);
                border: 1px solid var(--card-border);
                border-radius: 20px;
                padding: 40px;
                box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
            }}
            .badge {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                background: rgba(16, 185, 129, 0.15);
                color: #34d399;
                padding: 6px 14px;
                border-radius: 9999px;
                font-size: 13px;
                font-weight: 600;
                margin-bottom: 20px;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }}
            .badge-dot {{
                width: 8px;
                height: 8px;
                background: #10b981;
                border-radius: 50%;
                box-shadow: 0 0 10px #10b981;
            }}
            h1 {{ font-size: 32px; font-weight: 800; margin-bottom: 12px; letter-spacing: -0.5px; }}
            p.subtitle {{ color: var(--text-muted); font-size: 16px; line-height: 1.6; margin-bottom: 32px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 16px; margin-bottom: 32px; }}
            .card {{
                background: rgba(255, 255, 255, 0.03);
                border: 1px solid var(--card-border);
                border-radius: 12px;
                padding: 18px;
            }}
            .card h3 {{ font-size: 15px; font-weight: 600; color: var(--primary); margin-bottom: 6px; }}
            .card p {{ font-size: 13px; color: var(--text-muted); line-height: 1.4; }}
            .btn-group {{ display: flex; flex-wrap: wrap; gap: 14px; }}
            .btn {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                padding: 12px 24px;
                border-radius: 10px;
                font-weight: 600;
                font-size: 14px;
                text-decoration: none;
                transition: all 0.2s ease;
            }}
            .btn-primary {{
                background: var(--primary);
                color: #ffffff;
                box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
            }}
            .btn-primary:hover {{ background: var(--primary-hover); transform: translateY(-1px); }}
            .btn-secondary {{
                background: rgba(255, 255, 255, 0.07);
                color: var(--text-main);
                border: 1px solid var(--card-border);
            }}
            .btn-secondary:hover {{ background: rgba(255, 255, 255, 0.12); transform: translateY(-1px); }}
            footer {{ margin-top: 24px; font-size: 13px; color: var(--text-muted); text-align: center; }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="badge">
                <span class="badge-dot"></span>
                Backend Service Operational & Ready
            </div>
            <h1>{settings.APP_NAME}</h1>
            <p class="subtitle">
                Scalable, production-oriented document ingestion and structured question extraction engine with multi-format OCR fallback, layout continuity, 5-signal confidence scoring, and human review workflows.
            </p>
            
            <div class="grid">
                <div class="card">
                    <h3>Multi-Format Ingestion</h3>
                    <p>Handles PDF, JPG, JPEG, and PNG examination papers and answer keys with SHA-256 deduplication.</p>
                </div>
                <div class="card">
                    <h3>Extraction Pipeline</h3>
                    <p>Rule-based and AI segmenters parse stems, (A)-(D) options, tables, figures, and inline answer keys.</p>
                </div>
                <div class="card">
                    <h3>Confidence Engine</h3>
                    <p>5-signal weighted scoring (0.00-1.00) automatically routes high-confidence questions to production.</p>
                </div>
                <div class="card">
                    <h3>Review Queue</h3>
                    <p>Actionable review queues for human-in-the-loop validation, correction, and resolution.</p>
                </div>
            </div>

            <div class="btn-group">
                <a href="/docs" class="btn btn-primary">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253"></path></svg>
                    Interactive Swagger API Docs
                </a>
                <a href="/redoc" class="btn btn-secondary">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"></path></svg>
                    ReDoc Specification
                </a>
                <a href="/health" class="btn btn-secondary">
                    <svg width="18" height="18" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                    Health Status API
                </a>
            </div>
        </div>
        <footer>
            Environment: {settings.APP_ENV} &bull; API Prefix: {settings.API_V1_STR} &bull; FastAPI + PostgreSQL + Redis + Celery
        </footer>
    </body>
    </html>
    """

# Health Check
@app.get("/health", tags=["Health"])
@app.get(f"{settings.API_V1_STR}/health", tags=["Health"])
def health_check():
    return {
        "status": "HEALTHY",
        "app_name": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
    }


# Include Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(documents_router, prefix=settings.API_V1_STR)
app.include_router(questions_router, prefix=settings.API_V1_STR)
app.include_router(answers_router, prefix=settings.API_V1_STR)
app.include_router(review_router, prefix=settings.API_V1_STR)
app.include_router(relationships_router, prefix=settings.API_V1_STR)
