from pathlib import Path

from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict


class RunConfig(BaseModel):
    host: str = "0.0.0.0"
    port: int = 8000


class ApiPrefix(BaseModel):
    prefix: str = "/api"


class DatabaseConfig(BaseModel):
    url: str
    echo: bool = False
    echo_pool: bool = False
    pool_size: int = 5
    max_overflow: int = 10


class AuthJWT(BaseModel):
    private_key_path: Path = Path("certs/private.pem")
    public_key_path: Path = Path("certs/public.pem")
    algorithm: str = "RS256"
    TOKEN_TYPE: str = "Bearer"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 5


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=("env.template", ".env"),
        case_sensitive=False,
        env_nested_delimiter="__",
        env_prefix="APP_CONFIG__"
    )
    run: RunConfig = RunConfig()
    api: ApiPrefix = ApiPrefix()
    db: DatabaseConfig
    auth_JWT: AuthJWT = AuthJWT()


settings = Settings()  
