from fastapi import APIRouter
from .auth import router as auth_router
from .metrics import router as metrics_router
from .definitions import router as definitions_router
from .smart import router as smart_router
from .persons import router as persons_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth", tags=["auth"])
api_router.include_router(persons_router, prefix="/persons", tags=["persons"])
api_router.include_router(definitions_router, prefix="/definitions", tags=["definitions"])
api_router.include_router(metrics_router, prefix="/metrics", tags=["metrics"])
api_router.include_router(smart_router, prefix="/smart", tags=["smart"])
