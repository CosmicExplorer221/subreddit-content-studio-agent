"""Base repository with common operations"""
import sqlite3
from typing import List, Dict, Optional, Any
import json
import logging

logger = logging.getLogger(__name__)


class BaseRepository:
    """Base repository class with common database operations"""

    def __init__(self, conn: sqlite3.Connection):
        """Initialize with database connection"""
        self.conn = conn
        self.cursor = conn.cursor()

    def _row_to_dict(self, row: sqlite3.Row) -> Dict:
        """Convert SQLite Row to dictionary"""
        if row is None:
            return None
        return dict(row)

    def _rows_to_list(self, rows: List[sqlite3.Row]) -> List[Dict]:
        """Convert list of SQLite Rows to list of dictionaries"""
        return [self._row_to_dict(row) for row in rows]

    def _serialize_json_field(self, value: Any) -> str:
        """Serialize Python object to JSON string for storage"""
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)

    def _deserialize_json_field(self, value: str) -> Any:
        """Deserialize JSON string to Python object"""
        if value is None:
            return None
        if isinstance(value, (list, dict)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value

    def execute(self, query: str, params: tuple = ()) -> sqlite3.Cursor:
        """Execute a query with parameters"""
        try:
            return self.cursor.execute(query, params)
        except sqlite3.Error as e:
            logger.error(f"Query execution failed: {query}\nParams: {params}\nError: {e}")
            raise

    def fetchone(self, query: str, params: tuple = ()) -> Optional[Dict]:
        """Execute query and fetch one result"""
        self.execute(query, params)
        row = self.cursor.fetchone()
        return self._row_to_dict(row)

    def fetchall(self, query: str, params: tuple = ()) -> List[Dict]:
        """Execute query and fetch all results"""
        self.execute(query, params)
        rows = self.cursor.fetchall()
        return self._rows_to_list(rows)

    def insert(self, table: str, data: Dict) -> int:
        """
        Insert a record and return the ID

        Args:
            table: Table name
            data: Dictionary of column: value

        Returns:
            ID of inserted record
        """
        columns = ', '.join(data.keys())
        placeholders = ', '.join(['?' for _ in data])
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"

        self.execute(query, tuple(data.values()))
        return self.cursor.lastrowid

    def update(self, table: str, record_id: int, data: Dict, id_column: str = 'id') -> bool:
        """
        Update a record

        Args:
            table: Table name
            record_id: ID of record to update
            data: Dictionary of column: value
            id_column: Name of ID column

        Returns:
            True if update was successful
        """
        set_clause = ', '.join([f"{k} = ?" for k in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {id_column} = ?"

        self.execute(query, tuple(data.values()) + (record_id,))
        return self.cursor.rowcount > 0

    def delete(self, table: str, record_id: int, id_column: str = 'id') -> bool:
        """
        Delete a record

        Args:
            table: Table name
            record_id: ID of record to delete
            id_column: Name of ID column

        Returns:
            True if deletion was successful
        """
        query = f"DELETE FROM {table} WHERE {id_column} = ?"
        self.execute(query, (record_id,))
        return self.cursor.rowcount > 0
