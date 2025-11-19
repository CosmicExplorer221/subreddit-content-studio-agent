"""
Reddit RSS Service - No API Key Required
Fetches posts from Reddit using public RSS feeds
"""
import aiohttp
import feedparser
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging
from pathlib import Path

from app.storage.json_storage import get_storage

logger = logging.getLogger(__name__)


class RedditRSSService:
    """Service for fetching Reddit posts via RSS (no API key needed)"""

    def __init__(self):
        """Initialize RSS service"""
        self.storage = get_storage()
        self.rate_limit_rpm = 30  # Conservative rate limiting

    async def fetch_posts(
        self,
        category: str,
        time_filter: str = "week",
        limit: int = 50,
        min_score: Optional[int] = None
    ) -> Dict:
        """
        Fetch posts from Reddit using RSS feeds (no API key required)

        Args:
            category: Category ID to fetch posts for
            time_filter: Time filter (not used in RSS, but kept for compatibility)
            limit: Maximum posts to fetch per subreddit
            min_score: Minimum score filter

        Returns:
            Dictionary with fetched posts and metadata
        """
        # Get category configuration
        try:
            category_config = self.storage.storage.read("categories", category)
        except Exception as e:
            raise ValueError(f"Category {category} not found: {e}")

        subreddits = category_config.get('subreddits', [])
        if not subreddits:
            raise ValueError(f"No subreddits configured for category {category}")

        filters = category_config.get('filters', {})
        min_score = min_score or filters.get('min_score', 100)
        min_comments = filters.get('min_comments', 10)
        max_age_days = filters.get('max_age_days', 7)

        all_posts = []
        errors = []

        # Fetch from each subreddit
        for subreddit_name in subreddits:
            try:
                posts = await self._fetch_subreddit_rss(
                    subreddit_name,
                    limit=limit,
                    min_score=min_score,
                    min_comments=min_comments,
                    max_age_days=max_age_days
                )
                all_posts.extend(posts)
                logger.info(f"Fetched {len(posts)} posts from r/{subreddit_name}")
            except Exception as e:
                error_msg = f"Error fetching r/{subreddit_name}: {e}"
                logger.error(error_msg)
                errors.append(error_msg)

        # Sort by score
        all_posts.sort(key=lambda x: x['score'], reverse=True)

        return {
            'category': category,
            'total_fetched': len(all_posts),
            'subreddits': subreddits,
            'posts': all_posts[:limit],
            'errors': errors
        }

    async def _fetch_subreddit_rss(
        self,
        subreddit: str,
        limit: int = 50,
        min_score: int = 100,
        min_comments: int = 10,
        max_age_days: int = 7
    ) -> List[Dict]:
        """
        Fetch posts from a subreddit using RSS

        RSS endpoints:
        - /r/{subreddit}/.rss - New posts
        - /r/{subreddit}/top/.rss?t=week - Top posts (week/month/year/all)
        - /r/{subreddit}/hot/.rss - Hot posts
        """
        # Use top posts RSS feed
        rss_url = f"https://www.reddit.com/r/{subreddit}/top/.rss?limit={limit}"

        async with aiohttp.ClientSession() as session:
            async with session.get(
                rss_url,
                headers={'User-Agent': 'LinkedInAutomation/1.0'}
            ) as response:
                if response.status != 200:
                    raise Exception(f"RSS fetch failed: HTTP {response.status}")

                content = await response.text()

        # Parse RSS feed
        feed = feedparser.parse(content)
        posts = []

        cutoff_date = datetime.utcnow() - timedelta(days=max_age_days)

        for entry in feed.entries:
            try:
                # Extract post data from RSS
                post_data = self._parse_rss_entry(entry, subreddit)

                # Apply filters
                post_date = datetime.fromtimestamp(post_data['created_utc'])
                if post_date < cutoff_date:
                    continue

                if post_data['score'] < min_score:
                    continue

                if post_data['num_comments'] < min_comments:
                    continue

                posts.append(post_data)

            except Exception as e:
                logger.warning(f"Error parsing RSS entry: {e}")
                continue

        return posts

    def _parse_rss_entry(self, entry, subreddit: str) -> Dict:
        """
        Parse RSS entry into post data

        RSS entries have:
        - title
        - link (permalink)
        - author
        - published (date)
        - summary (content/description)
        - category (flair)
        """
        # Extract Reddit post ID from link
        # Link format: https://www.reddit.com/r/subreddit/comments/POST_ID/title/
        link = entry.get('link', '')
        post_id = self._extract_post_id(link)

        # Parse published date
        published = entry.get('published_parsed')
        created_utc = int(datetime(*published[:6]).timestamp()) if published else 0

        # Extract score and comments from summary
        # RSS summary often contains "[score] points and [comments] comments"
        summary = entry.get('summary', '')
        score, num_comments = self._extract_metrics_from_summary(summary)

        # Clean content (remove HTML)
        content = self._clean_html(summary)

        # Detect media URLs
        media_urls = self._extract_media_urls(entry)
        media_type = 'image' if media_urls and any(
            url.endswith(('.jpg', '.png', '.gif')) for url in media_urls
        ) else 'video' if media_urls else None

        return {
            'reddit_post_id': post_id,
            'subreddit': subreddit,
            'title': entry.get('title', ''),
            'content': content[:500] if content else None,  # Truncate
            'url': link,
            'author': entry.get('author', 'unknown'),
            'score': score,
            'num_comments': num_comments,
            'upvote_ratio': 0.9,  # RSS doesn't provide this, estimate
            'created_utc': created_utc,
            'permalink': link.replace('https://www.reddit.com', ''),
            'flair': entry.get('category', None),
            'media_type': media_type,
            'media_urls': media_urls,
            'top_comments': []  # RSS doesn't include comments
        }

    def _extract_post_id(self, link: str) -> str:
        """Extract post ID from Reddit URL"""
        parts = link.split('/')
        try:
            comments_idx = parts.index('comments')
            return parts[comments_idx + 1]
        except (ValueError, IndexError):
            # Fallback: use last part of URL
            return link.split('/')[-2] if link.endswith('/') else link.split('/')[-1]

    def _extract_metrics_from_summary(self, summary: str) -> tuple:
        """
        Extract score and comment count from RSS summary

        RSS summaries often contain text like:
        "submitted by user to r/subreddit [link] [comments]"
        "123 points (95% upvoted) by user"
        """
        import re

        score = 0
        num_comments = 0

        # Try to find score
        score_match = re.search(r'(\d+)\s*points?', summary)
        if score_match:
            score = int(score_match.group(1))

        # Try to find comment count
        comment_match = re.search(r'(\d+)\s*comments?', summary)
        if comment_match:
            num_comments = int(comment_match.group(1))

        return score, num_comments

    def _clean_html(self, html: str) -> str:
        """Remove HTML tags from text"""
        import re
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', html)
        # Decode HTML entities
        text = text.replace('&lt;', '<').replace('&gt;', '>').replace('&amp;', '&')
        text = text.replace('&quot;', '"').replace('&#39;', "'")
        return text.strip()

    def _extract_media_urls(self, entry) -> List[str]:
        """Extract media URLs from RSS entry"""
        urls = []

        # Check for media content in entry
        if hasattr(entry, 'media_content'):
            for media in entry.media_content:
                if 'url' in media:
                    urls.append(media['url'])

        # Check for thumbnails
        if hasattr(entry, 'media_thumbnail'):
            for thumb in entry.media_thumbnail:
                if 'url' in thumb:
                    urls.append(thumb['url'])

        # Extract from links
        if hasattr(entry, 'links'):
            for link in entry.links:
                if link.get('type', '').startswith('image/'):
                    urls.append(link['href'])

        return urls


# Singleton instance
_rss_service: Optional[RedditRSSService] = None


def get_rss_service() -> RedditRSSService:
    """Get or create RSS service singleton"""
    global _rss_service
    if _rss_service is None:
        _rss_service = RedditRSSService()
    return _rss_service
