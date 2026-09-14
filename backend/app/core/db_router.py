from __future__ import annotations
import contextlib
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from typing import Any

_engines: dict[str, Any] = {}

class DatabaseRouter:
    @staticmethod
    def get_engine(uri: str):
        if uri not in _engines:
            _engines[uri] = create_engine(
                uri,
                pool_size=20,
                max_overflow=30,
                pool_pre_ping=True
            )
        return _engines[uri]

    @classmethod
    def get_session(cls, database_uri: str):
        engine = cls.get_engine(database_uri)
        return scoped_session(sessionmaker(bind=engine))

    @contextlib.contextmanager
    def session_scope(self, tenant_id: str, database_uri: str):
        session_factory = self.get_session(database_uri)
        session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
            session_factory.remove()

db_router = DatabaseRouter()
