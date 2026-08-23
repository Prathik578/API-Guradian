"""Database engine and session management with RLS support."""

from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session, sessionmaker

from api_guardian.domain import TenantContext


class DatabaseManager:
    """Manages database connections and RLS tenant context."""

    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)



    @contextmanager
    def get_tenant_session(self, ctx: TenantContext) -> Generator[Session, None, None]:
        """Provides a database session scoped to the tenant using PostgreSQL RLS."""
        session = self.SessionLocal()
        try:
            if self.engine.dialect.name == "postgresql":
                session.execute(
                    text("SET LOCAL app.current_tenant_id = :tenant_id"),
                    {"tenant_id": str(ctx.tenant_id)},
                )
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


import os

# Global singleton for use in FastAPI and Celery workers
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///:memory:")
db_manager = DatabaseManager(DATABASE_URL)
