from pydantic import BaseModel, AnyUrl, TypeAdapter
from pydantic_settings import BaseSettings
from pydantic.networks import UrlConstraints
from typing import Annotated

SqliteUrl = Annotated[
    AnyUrl,
    UrlConstraints(allowed_schemas=["sqlite", "sqlite+aiosqlite"])
]


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000

class ApiPrefix(BaseModel):
    prefix: str = "/api"
 
class DatabaseConfig(BaseModel):
    url: SqliteUrl
class Settings(BaseSettings):
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig

settings = Settings()