from fastapi import APIRouter
from app.api.v1.projects import router as projects_router


router = APIRouter()
router.include_router(projects_router, prefix="/projects", tags=["projects"])