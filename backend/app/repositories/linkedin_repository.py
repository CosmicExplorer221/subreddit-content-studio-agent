"""Repository for LinkedIn posts"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime
from .base_repository import BaseRepository


class LinkedInPostRepository(BaseRepository):
    """Repository for managing LinkedIn posts in database"""

    def create(self, linkedin_data: Dict) -> int:
        """
        Create a new LinkedIn post

        Args:
            linkedin_data: Dictionary with LinkedIn post fields

        Returns:
            ID of created post
        """
        # Serialize JSON fields
        if 'hashtags' in linkedin_data:
            linkedin_data['hashtags'] = self._serialize_json_field(linkedin_data['hashtags'])

        # Add timestamps
        if 'generated_at' not in linkedin_data:
            linkedin_data['generated_at'] = datetime.utcnow().isoformat()
        if 'updated_at' not in linkedin_data:
            linkedin_data['updated_at'] = datetime.utcnow().isoformat()

        return self.insert('linkedin_posts', linkedin_data)

    def get_by_id(self, linkedin_post_id: int) -> Optional[Dict]:
        """Get LinkedIn post by ID"""
        post = self.fetchone(
            "SELECT * FROM linkedin_posts WHERE id = ?",
            (linkedin_post_id,)
        )
        if post:
            return self._deserialize_linkedin_post(post)
        return None

    def get_by_post_id(self, post_id: int) -> List[Dict]:
        """Get all LinkedIn variations for a Reddit post"""
        posts = self.fetchall(
            "SELECT * FROM linkedin_posts WHERE post_id = ? ORDER BY variation_number",
            (post_id,)
        )
        return [self._deserialize_linkedin_post(post) for post in posts]

    def list_posts(
        self,
        status: Optional[str] = None,
        template_id: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_quality_score: Optional[int] = None
    ) -> Dict:
        """
        List LinkedIn posts with filters

        Returns:
            Dict with 'posts' and 'total' keys
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        if status:
            where_clauses.append("status = ?")
            params.append(status)

        if template_id:
            where_clauses.append("template_id = ?")
            params.append(template_id)

        if min_quality_score is not None:
            where_clauses.append("quality_score >= ?")
            params.append(min_quality_score)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM linkedin_posts {where_sql}"
        count_result = self.fetchone(count_query, tuple(params))
        total = count_result['count'] if count_result else 0

        # Get posts with joined Reddit data
        query = f"""
            SELECT
                lp.*,
                p.reddit_post_id,
                p.title as reddit_title,
                p.subreddit,
                p.category,
                p.score as reddit_score,
                p.url as reddit_url
            FROM linkedin_posts lp
            LEFT JOIN posts p ON lp.post_id = p.id
            {where_sql}
            ORDER BY lp.generated_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        posts = self.fetchall(query, tuple(params))
        posts = [self._deserialize_linkedin_post(post) for post in posts]

        return {
            'posts': posts,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    def update_post(self, linkedin_post_id: int, updates: Dict) -> bool:
        """Update a LinkedIn post"""
        # Serialize JSON fields
        if 'hashtags' in updates:
            updates['hashtags'] = self._serialize_json_field(updates['hashtags'])

        # Update timestamp
        updates['updated_at'] = datetime.utcnow().isoformat()

        return self.update('linkedin_posts', linkedin_post_id, updates)

    def update_status(self, linkedin_post_id: int, new_status: str) -> bool:
        """Update post status"""
        return self.update_post(linkedin_post_id, {'status': new_status})

    def update_notion_sync(self, linkedin_post_id: int, notion_page_id: str) -> bool:
        """Update Notion sync information"""
        return self.update_post(linkedin_post_id, {
            'notion_page_id': notion_page_id,
            'notion_synced_at': datetime.utcnow().isoformat()
        })

    def delete_post(self, linkedin_post_id: int) -> bool:
        """Delete a LinkedIn post"""
        return self.delete('linkedin_posts', linkedin_post_id)

    def get_by_notion_page_id(self, notion_page_id: str) -> Optional[Dict]:
        """Get LinkedIn post by Notion page ID"""
        post = self.fetchone(
            "SELECT * FROM linkedin_posts WHERE notion_page_id = ?",
            (notion_page_id,)
        )
        if post:
            return self._deserialize_linkedin_post(post)
        return None

    def get_posts_by_status(self, status: str) -> List[Dict]:
        """Get all posts with specific status"""
        posts = self.fetchall(
            "SELECT * FROM linkedin_posts WHERE status = ? ORDER BY generated_at DESC",
            (status,)
        )
        return [self._deserialize_linkedin_post(post) for post in posts]

    def get_scheduled_posts(self, days_ahead: int = 7) -> List[Dict]:
        """Get posts scheduled for next N days"""
        future_date = (datetime.utcnow().timestamp() + (days_ahead * 86400))

        posts = self.fetchall(
            """
            SELECT * FROM linkedin_posts
            WHERE status = 'scheduled'
            AND scheduled_date IS NOT NULL
            AND scheduled_date <= ?
            ORDER BY scheduled_date ASC
            """,
            (future_date,)
        )
        return [self._deserialize_linkedin_post(post) for post in posts]

    def get_statistics(self) -> Dict:
        """Get LinkedIn post statistics"""
        stats = self.fetchone("""
            SELECT
                COUNT(*) as total_posts,
                AVG(quality_score) as avg_quality_score,
                COUNT(CASE WHEN status = 'draft' THEN 1 END) as draft_count,
                COUNT(CASE WHEN status = 'review' THEN 1 END) as review_count,
                COUNT(CASE WHEN status = 'approved' THEN 1 END) as approved_count,
                COUNT(CASE WHEN status = 'scheduled' THEN 1 END) as scheduled_count,
                COUNT(CASE WHEN status = 'published' THEN 1 END) as published_count,
                COUNT(CASE WHEN notion_page_id IS NOT NULL THEN 1 END) as synced_to_notion
            FROM linkedin_posts
        """)
        return dict(stats) if stats else {}

    def _deserialize_linkedin_post(self, post: Dict) -> Dict:
        """Deserialize JSON fields in a LinkedIn post"""
        if not post:
            return post

        post_dict = dict(post)
        if 'hashtags' in post_dict:
            post_dict['hashtags'] = self._deserialize_json_field(post_dict['hashtags'])

        return post_dict
