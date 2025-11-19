"""Repository for Reddit posts"""
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from .base_repository import BaseRepository


class PostRepository(BaseRepository):
    """Repository for managing Reddit posts in database"""

    def create(self, post_data: Dict) -> int:
        """
        Create a new Reddit post

        Args:
            post_data: Dictionary with post fields

        Returns:
            ID of created post
        """
        # Serialize JSON fields
        if 'media_urls' in post_data:
            post_data['media_urls'] = self._serialize_json_field(post_data['media_urls'])
        if 'top_comments' in post_data:
            post_data['top_comments'] = self._serialize_json_field(post_data['top_comments'])

        return self.insert('posts', post_data)

    def get_by_id(self, post_id: int) -> Optional[Dict]:
        """Get post by ID"""
        post = self.fetchone("SELECT * FROM posts WHERE id = ?", (post_id,))
        if post:
            return self._deserialize_post(post)
        return None

    def get_by_reddit_id(self, reddit_post_id: str) -> Optional[Dict]:
        """Get post by Reddit post ID"""
        post = self.fetchone(
            "SELECT * FROM posts WHERE reddit_post_id = ?",
            (reddit_post_id,)
        )
        if post:
            return self._deserialize_post(post)
        return None

    def list_posts(
        self,
        category: Optional[str] = None,
        subreddit: Optional[str] = None,
        limit: int = 50,
        offset: int = 0,
        min_score: Optional[int] = None,
        order_by: str = 'fetched_at DESC'
    ) -> Dict:
        """
        List posts with filters

        Returns:
            Dict with 'posts' and 'total' keys
        """
        # Build WHERE clause
        where_clauses = []
        params = []

        if category:
            where_clauses.append("category = ?")
            params.append(category)

        if subreddit:
            where_clauses.append("subreddit = ?")
            params.append(subreddit)

        if min_score is not None:
            where_clauses.append("score >= ?")
            params.append(min_score)

        where_sql = f"WHERE {' AND '.join(where_clauses)}" if where_clauses else ""

        # Get total count
        count_query = f"SELECT COUNT(*) as count FROM posts {where_sql}"
        count_result = self.fetchone(count_query, tuple(params))
        total = count_result['count'] if count_result else 0

        # Get posts
        query = f"""
            SELECT * FROM posts
            {where_sql}
            ORDER BY {order_by}
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])

        posts = self.fetchall(query, tuple(params))
        posts = [self._deserialize_post(post) for post in posts]

        return {
            'posts': posts,
            'total': total,
            'limit': limit,
            'offset': offset
        }

    def get_posts_by_category(self, category: str) -> List[Dict]:
        """Get all posts for a category"""
        posts = self.fetchall(
            "SELECT * FROM posts WHERE category = ? ORDER BY score DESC",
            (category,)
        )
        return [self._deserialize_post(post) for post in posts]

    def get_recent_posts(self, days: int = 7) -> List[Dict]:
        """Get posts from last N days"""
        cutoff_timestamp = int((datetime.utcnow() - timedelta(days=days)).timestamp())

        posts = self.fetchall(
            """
            SELECT * FROM posts
            WHERE created_utc >= ?
            ORDER BY created_utc DESC
            """,
            (cutoff_timestamp,)
        )
        return [self._deserialize_post(post) for post in posts]

    def update_post(self, post_id: int, updates: Dict) -> bool:
        """Update a post"""
        # Serialize JSON fields
        if 'media_urls' in updates:
            updates['media_urls'] = self._serialize_json_field(updates['media_urls'])
        if 'top_comments' in updates:
            updates['top_comments'] = self._serialize_json_field(updates['top_comments'])

        return self.update('posts', post_id, updates)

    def delete_post(self, post_id: int) -> bool:
        """Delete a post"""
        return self.delete('posts', post_id)

    def post_exists(self, reddit_post_id: str) -> bool:
        """Check if post exists by Reddit ID"""
        result = self.fetchone(
            "SELECT COUNT(*) as count FROM posts WHERE reddit_post_id = ?",
            (reddit_post_id,)
        )
        return result and result['count'] > 0

    def bulk_create(self, posts: List[Dict]) -> List[int]:
        """
        Bulk create posts

        Returns:
            List of created post IDs
        """
        post_ids = []
        for post_data in posts:
            # Skip if already exists
            if not self.post_exists(post_data.get('reddit_post_id')):
                post_id = self.create(post_data)
                post_ids.append(post_id)
        return post_ids

    def get_statistics(self) -> Dict:
        """Get post statistics"""
        stats = self.fetchone("""
            SELECT
                COUNT(*) as total_posts,
                COUNT(DISTINCT category) as total_categories,
                COUNT(DISTINCT subreddit) as total_subreddits,
                AVG(score) as avg_score,
                MAX(score) as max_score,
                SUM(CASE WHEN media_type IS NOT NULL THEN 1 ELSE 0 END) as posts_with_media
            FROM posts
        """)
        return dict(stats) if stats else {}

    def _deserialize_post(self, post: Dict) -> Dict:
        """Deserialize JSON fields in a post"""
        if not post:
            return post

        post_dict = dict(post)
        if 'media_urls' in post_dict:
            post_dict['media_urls'] = self._deserialize_json_field(post_dict['media_urls'])
        if 'top_comments' in post_dict:
            post_dict['top_comments'] = self._deserialize_json_field(post_dict['top_comments'])

        return post_dict
