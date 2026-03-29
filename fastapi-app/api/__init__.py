from fastapi import APIRouter

from .users.views import router as user_router
from .auth.jwt_auth import router as auth_router
from .auth.tokens import router as token_router
from .admin import router as admin_router
from .business import router as business_router

router = APIRouter()

router.include_router(router=user_router, prefix="/users")
router.include_router(router=auth_router, prefix="/auth")
router.include_router(router=token_router, prefix="/tokens")
router.include_router(router=admin_router, prefix="/admin")
router.include_router(router=business_router, prefix="/business")

 
