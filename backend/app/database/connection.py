"""
Database Connection Manager
Following backend-architect.md specifications
"""
import sqlite3
from contextlib import contextmanager
from typing import Generator
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections with connection pooling"""

    def __init__(self, db_path: str = "data/linkedin_automation.db"):
        """Initialize database manager"""
        self.db_path = db_path
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self._connection = None

    def get_connection(self) -> sqlite3.Connection:
        """
        Get database connection
        Returns a single connection with row factory
        """
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign keys
        return conn

    @contextmanager
    def get_db(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database connections
        Automatically commits and closes

        Usage:
            with db_manager.get_db() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM posts")
        """
        conn = self.get_connection()
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database operation failed: {e}")
            raise
        finally:
            conn.close()

    def close(self):
        """Close database connection"""
        if self._connection:
            self._connection.close()
            self._connection = None


# Global database manager instance
_db_manager: DatabaseManager = None


def get_db_manager(db_path: str = "data/linkedin_automation.db") -> DatabaseManager:
    """Get or create database manager singleton"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager(db_path)
    return _db_manager


def get_db() -> Generator[sqlite3.Connection, None, None]:
    """
    Dependency injection function for FastAPI

    Usage in FastAPI:
        @app.get("/api/posts")
        def get_posts(db: Connection = Depends(get_db)):
            cursor = db.cursor()
            ...
    """
    db_manager = get_db_manager()
    with db_manager.get_db() as conn:
        yield conn
