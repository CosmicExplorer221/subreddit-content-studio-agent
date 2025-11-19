"""
Notion Service - Following notion-integration-expert.md
Sync generated LinkedIn content to Notion database
"""
import os
import logging
from typing import Dict, List, Optional
from notion_client import Client
from datetime import datetime

logger = logging.getLogger(__name__)


class NotionService:
    """Service for syncing content to Notion"""

    def __init__(self, api_key: Optional[str] = None, database_id: Optional[str] = None):
        """Initialize Notion service"""
        self.api_key = api_key or os.getenv("NOTION_API_KEY")
        self.database_id = database_id or os.getenv("NOTION_DATABASE_ID")

        if self.api_key:
            self.client = Client(auth=self.api_key)
            logger.info("Notion service initialized")
        else:
            self.client = None
            logger.warning("Notion API key not configured")

    def is_configured(self) -> bool:
        """Check if Notion is properly configured"""
        return (self.api_key is not None and
                self.client is not None and
                self.database_id is not None)

    def build_page_properties(self, generated_post: Dict) -> Dict:
        """
        Build Notion page properties from generated post
        Following notion-integration-expert.md property structure
        """
        source_post = generated_post.get("source_post", {})
        gen_content = generated_post.get("generated_content", {})

        properties = {
            "Title": {
                "title": [
                    {
                        "text": {
                            "content": source_post.get("title", "Untitled")[:2000]
                        }
                    }
                ]
            },
            "Status": {
                "select": {
                    "name": generated_post.get("status", "Draft").capitalize()
                }
            },
            "Category": {
                "select": {
                    "name": source_post.get("category", "General").capitalize()
                }
            },
            "Source Post ID": {
                "rich_text": [
                    {
                        "text": {
                            "content": source_post.get("id", "")
                        }
                    }
                ]
            },
            "Source Score": {
                "number": source_post.get("score", 0)
            },
            "Quality Score": {
                "number": gen_content.get("quality_score", 0)
            },
            "Template": {
                "rich_text": [
                    {
                        "text": {
                            "content": gen_content.get("template_id", "")
                        }
                    }
                ]
            }
        }

        # Add hashtags if present
        hashtags = gen_content.get("hashtags", [])
        if hashtags:
            properties["Hashtags"] = {
                "multi_select": [
                    {"name": tag.replace("#", "")[:100]} for tag in hashtags[:10]
                ]
            }

        return properties

    def build_page_content(self, generated_post: Dict) -> List[Dict]:
        """
        Build Notion page content blocks
        Following notion-integration-expert.md rich formatting patterns
        """
        gen_content = generated_post.get("generated_content", {})
        source_post = generated_post.get("source_post", {})

        blocks = []

        # LinkedIn Content Section
        blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": [{"text": {"content": "LinkedIn Post"}}]
            }
        })

        # Split content into paragraphs
        content_text = gen_content.get("content", "")
        paragraphs = content_text.split("\n\n")

        for para in paragraphs[:20]:  # Limit to 20 paragraphs
            if para.strip():
                blocks.append({
                    "object": "block",
                    "type": "paragraph",
                    "paragraph": {
                        "rich_text": [
                            {
                                "text": {
                                    "content": para[:2000]  # Notion limit
                                }
                            }
                        ]
                    }
                })

        # Divider
        blocks.append({
            "object": "block",
            "type": "divider",
            "divider": {}
        })

        # Source Section
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"text": {"content": "Source Content"}}]
            }
        })

        # Source title as callout
        blocks.append({
            "object": "block",
            "type": "callout",
            "callout": {
                "icon": {"emoji": "🚂"},
                "rich_text": [
                    {
                        "text": {
                            "content": source_post.get("title", "")[:2000]
                        }
                    }
                ]
            }
        })

        # Source content
        if source_post.get("content"):
            blocks.append({
                "object": "block",
                "type": "paragraph",
                "paragraph": {
                    "rich_text": [
                        {
                            "text": {
                                "content": source_post.get("content", "")[:2000]
                            }
                        }
                    ]
                }
            })

        # Metrics
        blocks.append({
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": [{"text": {"content": "Metrics"}}]
            }
        })

        metrics_text = f"Source Score: {source_post.get('score', 0)} | Comments: {source_post.get('num_comments', 0)} | Quality Score: {gen_content.get('quality_score', 0)}/100"

        blocks.append({
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": [
                    {
                        "text": {
                            "content": metrics_text
                        }
                    }
                ]
            }
        })

        return blocks

    async def sync_post(self, generated_post: Dict) -> Dict:
        """
        Sync a single generated post to Notion
        Returns sync result
        """
        if not self.is_configured():
            return {
                "success": False,
                "error": "Notion not configured. Please add NOTION_API_KEY and NOTION_DATABASE_ID to .env file."
            }

        try:
            post_id = generated_post.get("id")

            # Check if already synced
            existing_page_id = generated_post.get("notion_page_id")

            if existing_page_id:
                # Update existing page
                logger.info(f"Updating existing Notion page {existing_page_id}")

                response = self.client.pages.update(
                    page_id=existing_page_id,
                    properties=self.build_page_properties(generated_post)
                )

                return {
                    "success": True,
                    "generated_post_id": post_id,
                    "notion_page_id": existing_page_id,
                    "action": "updated"
                }

            else:
                # Create new page
                logger.info(f"Creating new Notion page for post {post_id}")

                response = self.client.pages.create(
                    parent={"database_id": self.database_id},
                    properties=self.build_page_properties(generated_post),
                    children=self.build_page_content(generated_post)
                )

                notion_page_id = response["id"]

                return {
                    "success": True,
                    "generated_post_id": post_id,
                    "notion_page_id": notion_page_id,
                    "action": "created"
                }

        except Exception as e:
            logger.error(f"Error syncing to Notion: {e}")
            return {
                "success": False,
                "generated_post_id": generated_post.get("id"),
                "error": str(e)
            }

    async def sync_multiple(
        self,
        generated_posts: List[Dict],
        update_existing: bool = False
    ) -> Dict:
        """
        Sync multiple posts to Notion
        Following notion-integration-expert.md batch operations patterns
        """
        results = {
            "synced": [],
            "failed": []
        }

        for post in generated_posts:
            # Skip if already synced and not updating
            if post.get("notion_page_id") and not update_existing:
                logger.info(f"Skipping already synced post {post.get('id')}")
                continue

            result = await self.sync_post(post)

            if result.get("success"):
                results["synced"].append(result)
            else:
                results["failed"].append(result)

            # Rate limiting: 3 requests per second max
            # In practice, we're well under that with async operations

        return results


# Singleton instance
_notion_service = None

def get_notion_service() -> NotionService:
    """Get Notion service singleton"""
    global _notion_service
    if _notion_service is None:
        _notion_service = NotionService()
    return _notion_service
