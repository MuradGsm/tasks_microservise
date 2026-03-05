from fastapi import APIRouter
from app.api.v1.issues import router as issues_router
from app.api.v1.comments import router as comments_router

router = APIRouter()
router.include_router(issues_router)
router.include_router(comments_router)