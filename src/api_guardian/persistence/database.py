"""Database engine and session management with RLS support."""
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import Session, sessionmaker

from api_guardian.domain import TenantContext


class DatabaseManager:
    """Manages database connections and RLS tenant context."""
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url, pool_pre_ping=True)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Enforce RLS context clearing when connections return to pool
        @event.listens_for(self.engine, "checkin")
        def reset_tenant_context(dbapi_connection: Any, connection_record: Any) -> None:
            cursor = dbapi_connection.cursor()
            try:
                cursor.execute("RESET app.current_tenant_id")
            finally:
                cursor.close()

    @contextmanager
    def get_tenant_session(self, ctx: TenantContext) -> Generator[Session, None, None]:
        """Provides a database session with RLS context applied."""
        session = self.SessionLocal()
        try:
            # Set the tenant context for this transaction
            session.execute(
                text("SET LOCAL app.current_tenant_id = :tenant_id"),
                {"tenant_id": str(ctx.tenant_id)}
            )
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
