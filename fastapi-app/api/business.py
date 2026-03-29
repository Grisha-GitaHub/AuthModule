from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from api.dependencies import get_current_user_with_permissions
from core.models.db_helper import db_helper

router = APIRouter(tags=["Бизнес-объекты"])


# Mock данные
MOCK_PROJECTS = [
    {"id": 1, "name": "Проект Альфа", "description": "Разработка новой системы", "access_level": "private"},
    {"id": 2, "name": "Проект Бета", "description": "Модернизация существующей системы", "access_level": "internal"},
    {"id": 3, "name": "Проект Гамма", "description": "Исследовательский проект", "access_level": "public"},
]

MOCK_DOCUMENTS = [
    {"id": 1, "title": "Техническое задание", "project_id": 1, "access_level": "private"},
    {"id": 2, "title": "Архитектура системы", "project_id": 1, "access_level": "internal"},
    {"id": 3, "title": "Руководство пользователя", "project_id": 2, "access_level": "public"},
]

MOCK_REPORTS = [
    {"id": 1, "title": "Ежемесячный отчёт", "month": "Январь", "access_level": "internal"},
    {"id": 2, "title": "Квартальный отчёт", "quarter": "Q1", "access_level": "private"},
]


def check_access(user_permissions: list[str], access_level: str) -> bool:
    """Проверка доступа к объекту по уровню доступа"""
    if access_level == "public":
        return True
    if access_level == "internal" and "read" in user_permissions:
        return True
    if access_level == "private" and "read" in user_permissions:
        return True
    return False


# === Проекты ===

@router.get("/projects")
async def get_projects(
    current_user: dict = Depends(get_current_user_with_permissions),
    session: AsyncSession = Depends(db_helper.get_scoped_session)
):
    """Получить список проектов (с учётом прав доступа)"""
    permissions = current_user.get("permissions", [])
    
    if "read" not in permissions and "admin" not in current_user.get("roles", []):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра проектов"
        )
    
    # Возвращаем только проекты, доступные пользователю
    accessible_projects = [
        p for p in MOCK_PROJECTS
        if check_access(permissions, p["access_level"])
    ]
    
    return accessible_projects


@router.get("/projects/{project_id}")
async def get_project(
    project_id: int,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """Получить проект по ID"""
    permissions = current_user.get("permissions", [])
    
    project = next((p for p in MOCK_PROJECTS if p["id"] == project_id), None)
    if not project:
        raise HTTPException(status_code=404, detail="Проект не найден")
    
    if not check_access(permissions, project["access_level"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому проекту"
        )
    
    return project


@router.post("/projects")
async def create_project(
    name: str,
    description: str,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """Создать проект (требует права create)"""
    permissions = current_user.get("permissions", [])
    
    if "create" not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для создания проектов"
        )
    
    new_id = max(p["id"] for p in MOCK_PROJECTS) + 1 if MOCK_PROJECTS else 1
    new_project = {
        "id": new_id,
        "name": name,
        "description": description,
        "access_level": "private"
    }
    
    return new_project


# === Документы ===

@router.get("/documents")
async def get_documents(
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """Получить список документов"""
    permissions = current_user.get("permissions", [])
    
    if "read" not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра документов"
        )
    
    accessible_docs = [
        d for d in MOCK_DOCUMENTS
        if check_access(permissions, d["access_level"])
    ]
    
    return accessible_docs


@router.get("/documents/{document_id}")
async def get_document(
    document_id: int,
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """Получить документ по ID"""
    permissions = current_user.get("permissions", [])
    
    doc = next((d for d in MOCK_DOCUMENTS if d["id"] == document_id), None)
    if not doc:
        raise HTTPException(status_code=404, detail="Документ не найден")
    
    if not check_access(permissions, doc["access_level"]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к этому документу"
        )
    
    return doc


# === Отчёты ===

@router.get("/reports")
async def get_reports(
    current_user: dict = Depends(get_current_user_with_permissions)
):
    """Получить список отчётов"""
    permissions = current_user.get("permissions", [])
    
    if "read" not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для просмотра отчётов"
        )
    
    accessible_reports = [
        r for r in MOCK_REPORTS
        if check_access(permissions, r["access_level"])
    ]
    
    return accessible_reports


# === Демонстрация ошибок ===

@router.get("/forbidden-demo")
async def forbidden_demo():
    """Эндпоинт для демонстрации 403 ошибки (всегда возвращает Forbidden)"""
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Доступ запрещён. У вас нет прав для доступа к этому ресурсу."
    )


@router.get("/unauthorized-demo")
async def unauthorized_demo():
    """Эндпоинт для демонстрации 401 ошибки (требует авторизации)"""
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Требуется авторизация. Пожалуйста, войдите в систему."
    )
