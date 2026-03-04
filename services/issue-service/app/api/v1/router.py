from fastapi import APIRouter
from app.api.v1.issues import router as issues_router

router = APIRouter()
router.include_router(issues_router)