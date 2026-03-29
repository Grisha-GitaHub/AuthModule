import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI

from api import router as api_router
from core.config import settings
from core.models import Base, db_helper
from core.models.seed import init_db

print(f"Текущая директория: {os.getcwd()}")
print(f"Файл .env существует: {os.path.exists('.env')}")


@asynccontextmanager
async def lifespan(main_app: FastAPI):
    async with db_helper.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Инициализация тестовых данных
    async with db_helper.session_factory() as session:
        await init_db(session)

    yield
    await db_helper.dispose()


main_app = FastAPI(lifespan=lifespan)

main_app.include_router(api_router, prefix=settings.api.prefix)

if __name__ == "__main__":
    uvicorn.run(
        "main:main_app",
        host=settings.run.host,
        port=settings.run.port,
        reload=True,
    )
