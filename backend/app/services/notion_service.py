"""
Notion Integration Service
Handles syncing posts to Notion database
"""
from notion_client import Client, AsyncClient
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import asyncio

from app.core.config import settings
from app.storage.json_storage import get_storage
from app.models.schemas import PostStatus

logger = logging.getLogger(__name__)


class NotionService:
    """Service for syncing content to Notion database"""

    def __init__(self):
        """Initialize Notion client"""
        self.api_token = settings.notion_api_token
        self.database_id = settings.notion_database_id
        self.rate_limit_rps = 3  # Notion rate limit: 3 requests per second
        self.storage = get_storage()

        if self.api_token:
            self.client = Client(auth=self.api_token)
            self.async_client = AsyncClient(auth=self.api_token)
            logger.info("Notion service initialized")
        else:
            self.client = None
            self.async_client = None
            logger.warning("Notion API not configured")

    def is_configured(self) -> bool:
        """Check if Notion is properly configured"""
        return (
            self.api_token is not None
            and self.database_id is not None
            and self.client is not None
        )

    async def check_duplicate(self, reddit_post_id: str) -> Optional[str]:
        """
        Check if a post already exists in Notion database

        Args:
            reddit_post_id: Reddit post ID to check

        Returns:
            Notion page ID if exists, None otherwise
        """
        if not self.is_configured():
            raise ValueError("Notion API not configured")

        try:
            # Query database for existing post
            response = await self.async_client.databases.query(
                database_id=self.database_id,
                filter={
                    "property": "Reddit Post ID",
                    "rich_text": {
                        "equals": reddit_post_id
                    }
                }
            )

            results = response.get('results', [])
            if results:
                return results[0]['id']

            return None

        except Exception as e:
            logger.error(f"Error checking duplicate for {reddit_post_id}: {e}")
            return None

    def build_notion_page(self, post_data: Dict) -> Dict[str, Any]:
        """
        Build Notion page properties from post data

        Args:
            post_data: Post data dictionary

        Returns:
            Notion page properties
        """
        reddit_data = post_data.get('reddit_data', {})
        linkedin_content = post_data.get('linkedin_content', {})

        # Extract data
        title = reddit_data.get('title', 'Untitled')
        subreddit = reddit_data.get('subreddit', '')
        reddit_post_id = reddit_data.get('reddit_post_id', '')
        score = reddit_data.get('score', 0)
        num_comments = reddit_data.get('num_comments', 0)
        permalink = reddit_data.get('permalink', '')
        category = post_data.get('category', '')
        status = post_data.get('status', 'draft')
        template_id = post_data.get('template_id', '')

        # LinkedIn content
        content = linkedin_content.get('content', '')
        quality_score = linkedin_content.get('quality_score', 0)
        hashtags = linkedin_content.get('hashtags', [])
        char_count = linkedin_content.get('char_count', 0)

        # Build properties
        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": title[:2000]  # Notion limit
                        }
                    }
                ]
            },
            "Category": {
                "select": {
                    "name": category.capitalize()
                }
            },
            "Status": {
                "select": {
                    "name": self._map_status(status)
                }
            },
            "Reddit Post ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": reddit_post_id
                        }
                    }
                ]
            },
            "Subreddit": {
                "rich_text": [
                    {
                        "text": {
                            "content": f"r/{subreddit}"
                        }
                    }
                ]
            },
            "Score": {
                "number": score
            },
            "Comments": {
                "number": num_comments
            },
            "Quality Score": {
                "number": quality_score
            },
            "Character Count": {
                "number": char_count
            },
            "Template": {
                "select": {
                    "name": template_id.capitalize() if template_id else "None"
                }
            }
        }

        # Add hashtags if present
        if hashtags:
            properties["Hashtags"] = {
                "multi_select": [
                    {"name": tag[:100]} for tag in hashtags[:10]  # Limit to 10 tags
                ]
            }

        # Add Reddit URL
        if permalink:
            reddit_url = f"https://reddit.com{permalink}"
            properties["Reddit URL"] = {
                "url": reddit_url
            }

        # Build page content (children blocks)
        children = []

        # Add LinkedIn content if available
        if content:
            # Split content into chunks (Notion has a 2000 char limit per block)
            content_chunks = self._chunk_text(content, 1900)

            children.append({
                "object": "block",
                "type": "heading_2",
                "heading_2": {
                    "rich_text": [{"type": "text", "text": {"content": "LinkedIn Post"}}]
                }
            })

            for chunk in content_chunks:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": chunk}
                            }
                        ]
                    }
                })

        # Add Reddit original content
        reddit_content = reddit_data.get('content', '')
        if reddit_content:
            content_chunks = self._chunk_text(reddit_content, 1900)

            children.append({
                "object": "block",
                "type": "heading_3",
                "heading_3": {
                    "rich_text": [{"type": "text", "text": {"content": "Original Reddit Post"}}]
                }
            })

            for chunk in content_chunks:
                children.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "type": "text",
                                "text": {"content": chunk}
                            }
                        ]
                    }
                })

        return {
            "properties": properties,
            "children": children if children else None
        }

    def _map_status(self, status: str) -> str:
        """Map internal status to Notion status"""
        status_map = {
            'draft': 'Draft',
            'review': 'In Review',
            'approved': 'Approved',
            'scheduled': 'Scheduled',
            'published': 'Published',
            'rejected': 'Rejected'
        }
        return status_map.get(status, 'Draft')

    def _chunk_text(self, text: str, chunk_size: int = 1900) -> List[str]:
        """Split text into chunks for Notion blocks"""
        if len(text) <= chunk_size:
            return [text]

        chunks = []
        while text:
            if len(text) <= chunk_size:
                chunks.append(text)
                break

            # Try to split at paragraph break
            split_pos = text[:chunk_size].rfind('\n\n')
            if split_pos == -1:
                # Try to split at sentence break
                split_pos = text[:chunk_size].rfind('. ')
                if split_pos == -1:
                    # Split at space
                    split_pos = text[:chunk_size].rfind(' ')
                    if split_pos == -1:
                        split_pos = chunk_size

            chunks.append(text[:split_pos].strip())
            text = text[split_pos:].strip()

        return chunks

    async def create_page(self, post_id: str) -> Dict[str, Any]:
        """
        Create a Notion page for a post

        Args:
            post_id: ID of the post to sync

        Returns:
            Result with Notion page ID and status
        """
        if not self.is_configured():
            raise ValueError("Notion API not configured. Set NOTION_API_TOKEN and NOTION_DATABASE_ID in .env")

        # Load post
        try:
            post_data = self.storage.storage.read("posts", post_id)
        except Exception as e:
            raise ValueError(f"Post {post_id} not found: {e}")

        reddit_post_id = post_data.get('reddit_data', {}).get('reddit_post_id')

        # Check for duplicates
        existing_page_id = await self.check_duplicate(reddit_post_id)
        if existing_page_id:
            return {
                'post_id': post_id,
                'notion_page_id': existing_page_id,
                'status': 'duplicate',
                'message': f'Post already exists in Notion'
            }

        # Build Notion page
        page_data = self.build_notion_page(post_data)

        try:
            # Create page in Notion
            response = await self.async_client.pages.create(
                parent={"database_id": self.database_id},
                properties=page_data['properties'],
                children=page_data['children']
            )

            notion_page_id = response['id']

            # Update post with Notion page ID
            post_data['notion_page_id'] = notion_page_id
            post_data['updated_at'] = datetime.utcnow().isoformat()
            self.storage.storage.write("posts", post_id, post_data)

            logger.info(f"Created Notion page {notion_page_id} for post {post_id}")

            return {
                'post_id': post_id,
                'notion_page_id': notion_page_id,
                'status': 'created',
                'message': 'Page created successfully',
                'url': response.get('url', '')
            }

        except Exception as e:
            logger.error(f"Error creating Notion page for post {post_id}: {e}")
            raise ValueError(f"Failed to create Notion page: {e}")

    async def update_page(self, post_id: str) -> Dict[str, Any]:
        """
        Update an existing Notion page

        Args:
            post_id: ID of the post to update

        Returns:
            Result with update status
        """
        if not self.is_configured():
            raise ValueError("Notion API not configured")

        # Load post
        try:
            post_data = self.storage.storage.read("posts", post_id)
        except Exception as e:
            raise ValueError(f"Post {post_id} not found: {e}")

        notion_page_id = post_data.get('notion_page_id')
        if not notion_page_id:
            # Try to find existing page
            reddit_post_id = post_data.get('reddit_data', {}).get('reddit_post_id')
            notion_page_id = await self.check_duplicate(reddit_post_id)

            if not notion_page_id:
                return await self.create_page(post_id)

        # Build updated page data
        page_data = self.build_notion_page(post_data)

        try:
            # Update page properties
            await self.async_client.pages.update(
                page_id=notion_page_id,
                properties=page_data['properties']
            )

            logger.info(f"Updated Notion page {notion_page_id} for post {post_id}")

            return {
                'post_id': post_id,
                'notion_page_id': notion_page_id,
                'status': 'updated',
                'message': 'Page updated successfully'
            }

        except Exception as e:
            logger.error(f"Error updating Notion page for post {post_id}: {e}")
            raise ValueError(f"Failed to update Notion page: {e}")

    async def batch_sync(
        self,
        post_ids: List[str],
        update_existing: bool = False
    ) -> Dict[str, Any]:
        """
        Sync multiple posts to Notion

        Args:
            post_ids: List of post IDs to sync
            update_existing: Whether to update existing pages

        Returns:
            Batch sync results
        """
        results = {
            'created': [],
            'updated': [],
            'duplicates': [],
            'errors': []
        }

        for post_id in post_ids:
            try:
                # Rate limiting
                await asyncio.sleep(1 / self.rate_limit_rps)

                if update_existing:
                    result = await self.update_page(post_id)
                else:
                    result = await self.create_page(post_id)

                status = result['status']
                if status == 'created':
                    results['created'].append(result)
                elif status == 'updated':
                    results['updated'].append(result)
                elif status == 'duplicate':
                    results['duplicates'].append(result)

            except Exception as e:
                logger.error(f"Error syncing post {post_id}: {e}")
                results['errors'].append({
                    'post_id': post_id,
                    'error': str(e)
                })

        return {
            'total_posts': len(post_ids),
            'created': len(results['created']),
            'updated': len(results['updated']),
            'duplicates': len(results['duplicates']),
            'failed': len(results['errors']),
            'results': results
        }

    def get_database_info(self) -> Dict[str, Any]:
        """Get Notion database information"""
        if not self.is_configured():
            return {
                'status': 'not_configured',
                'message': 'Notion API not configured'
            }

        try:
            database = self.client.databases.retrieve(database_id=self.database_id)

            return {
                'status': 'connected',
                'database_id': self.database_id,
                'title': database.get('title', [{}])[0].get('plain_text', 'Untitled'),
                'properties': list(database.get('properties', {}).keys())
            }

        except Exception as e:
            logger.error(f"Error retrieving database info: {e}")
            return {
                'status': 'error',
                'error': str(e)
            }


# Singleton instance
_notion_service: Optional[NotionService] = None


def get_notion_service() -> NotionService:
    """Get or create Notion service singleton"""
    global _notion_service
    if _notion_service is None:
        _notion_service = NotionService()
    return _notion_service
