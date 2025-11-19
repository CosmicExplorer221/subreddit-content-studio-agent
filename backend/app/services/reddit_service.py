"""
Reddit Integration Service
Implements reddit-integration-expert agent for fetching posts from Reddit
"""
import praw
from praw.exceptions import PRAWException
from typing import List, Dict, Optional
import time
from datetime import datetime
import logging

from app.core.config import settings
from app.storage.json_storage import get_storage

logger = logging.getLogger(__name__)


class RedditService:
    """Reddit API integration service using PRAW"""

    def __init__(self):
        """Initialize Reddit client"""
        self.reddit = None
        self._initialize_client()

    def _initialize_client(self):
        """Initialize PRAW Reddit client with credentials"""
        try:
            if not all([
                settings.reddit_client_id,
                settings.reddit_client_secret,
                settings.reddit_username,
                settings.reddit_password
            ]):
                logger.warning("Reddit credentials not configured")
                return

            self.reddit = praw.Reddit(
                client_id=settings.reddit_client_id,
                client_secret=settings.reddit_client_secret,
                username=settings.reddit_username,
                password=settings.reddit_password,
                user_agent=f"LinkedInContentStudio/1.0 by {settings.reddit_username}"
            )

            # Test authentication
            self.reddit.user.me()
            logger.info(f"✓ Reddit API connected as u/{settings.reddit_username}")

        except Exception as e:
            logger.error(f"Failed to initialize Reddit client: {e}")
            self.reddit = None

    def is_configured(self) -> bool:
        """Check if Reddit API is configured"""
        return self.reddit is not None

    def should_include_post(
        self,
        post,
        min_score: int = 100,
        min_comments: int = 10,
        max_age_days: int = 7
    ) -> bool:
        """
        Filter posts based on quality thresholds
        """
        try:
            # Check if removed/deleted
            if post.removed_by_category or post.author == "[deleted]":
                return False

            # Check NSFW
            if post.over_18:
                return False

            # Check score
            if post.score < min_score:
                return False

            # Check comments
            if post.num_comments < min_comments:
                return False

            # Check age
            age_days = (time.time() - post.created_utc) / 86400
            if age_days > max_age_days:
                return False

            return True

        except Exception as e:
            logger.error(f"Error filtering post: {e}")
            return False

    def extract_post_data(self, post) -> Dict:
        """
        Extract post data into structured format
        """
        try:
            # Determine media type and URLs
            media_urls = []
            media_type = None

            # Check for images
            if hasattr(post, 'url') and post.url:
                if any(post.url.endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.gif']):
                    media_type = "image"
                    media_urls.append(post.url)

            # Check for Reddit video
            if hasattr(post, 'is_video') and post.is_video:
                media_type = "video"
                if hasattr(post, 'media') and post.media:
                    if 'reddit_video' in post.media:
                        video_url = post.media['reddit_video']['fallback_url']
                        media_urls.append(video_url)

            # Check for gallery
            if hasattr(post, 'is_gallery') and post.is_gallery:
                media_type = "gallery"
                if hasattr(post, 'media_metadata'):
                    for item_id, item_data in post.media_metadata.items():
                        if 's' in item_data and 'u' in item_data['s']:
                            media_urls.append(item_data['s']['u'].replace('&amp;', '&'))

            # Extract post data
            data = {
                "reddit_post_id": post.id,
                "subreddit": post.subreddit.display_name,
                "title": post.title,
                "content": post.selftext if hasattr(post, 'selftext') else None,
                "url": post.url,
                "author": str(post.author) if post.author else "[deleted]",
                "score": post.score,
                "num_comments": post.num_comments,
                "upvote_ratio": post.upvote_ratio,
                "created_utc": int(post.created_utc),
                "permalink": post.permalink,
                "flair": post.link_flair_text if hasattr(post, 'link_flair_text') else None,
                "media_type": media_type,
                "media_urls": media_urls
            }

            return data

        except Exception as e:
            logger.error(f"Error extracting post data: {e}")
            return None

    def extract_top_comments(self, post, limit: int = 5, min_score: int = 10) -> List[Dict]:
        """
        Extract top comments from post
        """
        try:
            # Expand comment forest
            post.comments.replace_more(limit=0)

            comments = []
            for comment in post.comments.list():
                if (hasattr(comment, 'score') and
                    comment.score >= min_score and
                    hasattr(comment, 'body') and
                    len(comment.body) > 50 and
                    str(comment.author) != "[deleted]"):

                    comments.append({
                        "author": str(comment.author),
                        "body": comment.body,
                        "score": comment.score,
                        "created_utc": int(comment.created_utc) if hasattr(comment, 'created_utc') else 0
                    })

            # Sort by score and return top N
            comments.sort(key=lambda x: x["score"], reverse=True)
            return comments[:limit]

        except Exception as e:
            logger.error(f"Error extracting comments: {e}")
            return []

    def fetch_posts(
        self,
        category: str,
        time_filter: str = "week",
        limit: int = 50,
        min_score: Optional[int] = None
    ) -> Dict:
        """
        Fetch posts from Reddit by category

        Args:
            category: Category ID to fetch posts from
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Maximum posts per subreddit
            min_score: Minimum score filter (overrides category default)

        Returns:
            Dictionary with fetched posts and metadata
        """
        if not self.is_configured():
            return {
                "status": "error",
                "error": "Reddit API not configured. Please set credentials in .env file.",
                "posts": []
            }

        try:
            # Get category configuration
            storage = get_storage()
            category_config = storage.get_category(category)

            if not category_config:
                return {
                    "status": "error",
                    "error": f"Category '{category}' not found",
                    "posts": []
                }

            # Get filters from category
            filters = category_config.get('filters', {})
            min_score = min_score or filters.get('min_score', 100)
            min_comments = filters.get('min_comments', 10)
            max_age_days = filters.get('max_age_days', 7)

            # Get subreddits
            subreddits = category_config.get('subreddits', [])

            if not subreddits:
                return {
                    "status": "error",
                    "error": f"No subreddits configured for category '{category}'",
                    "posts": []
                }

            logger.info(f"Fetching posts from {len(subreddits)} subreddits in category '{category}'")

            # Fetch posts from each subreddit
            all_posts = []
            errors = []

            for subreddit_name in subreddits:
                try:
                    logger.info(f"Fetching from r/{subreddit_name}...")

                    subreddit = self.reddit.subreddit(subreddit_name)

                    # Fetch posts based on time filter
                    posts = subreddit.top(time_filter=time_filter, limit=limit)

                    fetched_count = 0
                    for post in posts:
                        # Apply filters
                        if self.should_include_post(
                            post,
                            min_score=min_score,
                            min_comments=min_comments,
                            max_age_days=max_age_days
                        ):
                            # Extract post data
                            post_data = self.extract_post_data(post)

                            if post_data:
                                # Add category
                                post_data['category'] = category

                                # Extract comments
                                post_data['top_comments'] = self.extract_top_comments(post)

                                all_posts.append(post_data)
                                fetched_count += 1

                    logger.info(f"  ✓ r/{subreddit_name}: {fetched_count} posts")

                    # Rate limiting (60 requests/minute for Reddit API)
                    time.sleep(1)

                except PRAWException as e:
                    error_msg = f"r/{subreddit_name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"  ✗ {error_msg}")
                    continue

                except Exception as e:
                    error_msg = f"r/{subreddit_name}: {str(e)}"
                    errors.append(error_msg)
                    logger.error(f"  ✗ {error_msg}")
                    continue

            # Rank posts by score
            all_posts.sort(key=lambda x: x['score'], reverse=True)

            logger.info(f"✓ Fetched {len(all_posts)} total posts from category '{category}'")

            return {
                "status": "success",
                "category": category,
                "posts": all_posts,
                "total_posts": len(all_posts),
                "subreddits_fetched": len(subreddits),
                "errors": errors,
                "filters": {
                    "time_filter": time_filter,
                    "min_score": min_score,
                    "min_comments": min_comments,
                    "max_age_days": max_age_days
                },
                "fetched_at": datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching posts: {e}")
            return {
                "status": "error",
                "error": str(e),
                "posts": []
            }


# Singleton instance
_reddit_service = None


def get_reddit_service() -> RedditService:
    """Get Reddit service singleton"""
    global _reddit_service
    if _reddit_service is None:
        _reddit_service = RedditService()
    return _reddit_service
