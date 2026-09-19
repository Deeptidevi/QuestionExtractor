from app.api.routes.auth import router as auth_router
from app.api.routes.documents import router as documents_router
from app.api.routes.questions import router as questions_router
from app.api.routes.answers import router as answers_router
from app.api.routes.review import router as review_router
from app.api.routes.relationships import router as relationships_router

__all__ = [
    "auth_router",
    "documents_router",
    "questions_router",
    "answers_router",
    "review_router",
    "relationships_router",
]
