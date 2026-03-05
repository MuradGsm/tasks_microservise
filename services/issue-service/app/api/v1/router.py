from fastapi import APIRouter
from app.api.v1.issues import router as issues_router
from app.api.v1.comments import router as comments_router
from app.api.v1.transitions import router as transitions_router

router = APIRouter()
router.include_router(issues_router)
router.include_router(comments_router)
router.include_router(transitions_router)