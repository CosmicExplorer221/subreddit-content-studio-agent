"""Repository for media files"""
import sqlite3
from typing import List, Dict, Optional
from .base_repository import BaseRepository


class MediaRepository(BaseRepository):
    """Repository for managing media files in database"""

    def create(self, media_data: Dict) -> int:
        """
        Create a new media file record

        Args:
            media_data: Dictionary with media file fields

        Returns:
            ID of created media record
        """
        return self.insert('media_files', media_data)

    def get_by_id(self, media_id: int) -> Optional[Dict]:
        """Get media file by ID"""
        return self.fetchone("SELECT * FROM media_files WHERE id = ?", (media_id,))

    def get_by_post_id(self, post_id: int) -> List[Dict]:
        """Get all media files for a post"""
        return self.fetchall(
            "SELECT * FROM media_files WHERE post_id = ? ORDER BY downloaded_at",
            (post_id,)
        )

    def update_media(self, media_id: int, updates: Dict) -> bool:
        """Update a media file record"""
        return self.update('media_files', media_id, updates)

    def update_status(self, media_id: int, new_status: str) -> bool:
        """Update media file status"""
        return self.update_media(media_id, {'status': new_status})

    def delete_media(self, media_id: int) -> bool:
        """Delete a media file record"""
        return self.delete('media_files', media_id)

    def get_by_file_path(self, file_path: str) -> Optional[Dict]:
        """Get media file by path"""
        return self.fetchone(
            "SELECT * FROM media_files WHERE file_path = ?",
            (file_path,)
        )

    def list_media(
        self,
        file_type: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> Dict:
        """
        List media files with filters

        Returns:
            Dict with 'media' and 'total' keys
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        if file_type:
            where_clauses.append("file_type = ?")
            params.append(file_type)

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM media_files {where_sql}"
        count_result = self.fetchone(count_query, tuple(params))
        total = count_result['count'] if count_result else 0

        # Get media files
        query = f"""
            SELECT * FROM media_files
            {where_sql}
            ORDER BY downloaded_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        media = self.fetchall(query, tuple(params))

        return {
            'media': media,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    def get_statistics(self) -> Dict:
        """Get media statistics"""
        stats = self.fetchone("""
            SELECT
                COUNT(*) as total_files,
                COUNT(CASE WHEN file_type = 'image' THEN 1 END) as image_count,
                COUNT(CASE WHEN file_type = 'video' THEN 1 END) as video_count,
                SUM(file_size) as total_size,
                AVG(file_size) as avg_file_size,
                COUNT(CASE WHEN status = 'downloaded' THEN 1 END) as downloaded_count,
                COUNT(CASE WHEN status = 'optimized' THEN 1 END) as optimized_count,
                COUNT(CASE WHEN status = 'failed' THEN 1 END) as failed_count
            FROM media_files
        """)
        return dict(stats) if stats else {}
