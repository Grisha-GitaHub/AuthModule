
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, async_sessionmaker, AsyncSession, AsyncGenerator
from core.config import Settings

class DatabaseHelper:
    def __init__(
        self,
        url: str,
        echo: bool,
        echo_pool: bool,
        pool_size: int,
        max_overflow: int, 
    ) -> None:
        self.engine: AsyncEngine = create_async_engine(
            url=url,
            echo=echo,
            echo_pool=echo_pool,
            pool_size=pool_size,
            max_overflow=max_overflow,
        )
        
        self.session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
            bind=self.engine,
            autoflush=False,
            autocommit=False,
            expire_on_commit=False,
        )
    async def dispose(self) -> None:
        await self.engine.dispose()
        
    async def session_getter(self) -> AsyncGenerator[AsyncSession, None]:
        async with self.session_factory() as session:
            yield session

db_helper = DatabaseHelper(
    url=str(Settings.db.url),
    echo=Settings.db.echo,
    echo_pool=Settings.db.echo_pool,
    pool_size=Settings.db.pool_size,
    max_overflow=Settings.db.max_overflow,
    
)