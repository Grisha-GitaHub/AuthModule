from fastapi import APIRouter

from .users.views import router as user_router
from api.auth.jwt_auth import router as auth_router

router = APIRouter()

router.include_router(router=user_router, prefix="/users")
router.include_router(router=auth_router, prefix="/auth")

