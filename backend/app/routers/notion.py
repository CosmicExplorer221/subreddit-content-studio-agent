"""
Notion API Router
Handles Notion integration and syncing (structure ready for integration)
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from app.models.schemas import NotionSyncRequest, JobResponse, MessageResponse
from app.storage.json_storage import get_storage

router = APIRouter()


@router.post("/sync", response_model=JobResponse)
async def sync_to_notion(request: NotionSyncRequest):
    """
    Sync posts to Notion database

    **Note**: This is a structure endpoint. Actual Notion integration
    will be implemented by the notion-integration-expert agent.

    Args:
        request: Sync request with post IDs and options

    Returns job ID for tracking the sync operation.
    """
    storage = get_storage()

    # Verify all posts exist
    missing_posts = []
    for post_id in request.post_ids:
        if not storage.get_post(post_id):
            missing_posts.append(post_id)

    if missing_posts:
        raise HTTPException(
            status_code=404,
            detail=f"Posts not found: {', '.join(missing_posts)}"
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # TODO: Implement actual Notion syncing
    # This will be implemented by notion-integration-expert agent

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Notion sync queued for {len(request.post_ids)} post(s). "
                f"Integration pending - see notion-integration-expert agent."
    )


@router.get("/posts/{post_id}/status")
async def get_notion_status(post_id: str):
    """
    Get Notion sync status for a post

    Returns information about the post's Notion page if synced.
    """
    storage = get_storage()

    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    notion_page_id = post.get('notion_page_id')

    if not notion_page_id:
        return {
            "post_id": post_id,
            "synced": False,
            "message": "Post not synced to Notion"
        }

    # TODO: Fetch actual Notion page status
    # This will be implemented by notion-integration-expert agent

    return {
        "post_id": post_id,
        "synced": True,
        "notion_page_id": notion_page_id,
        "message": "Notion integration pending - see notion-integration-expert agent"
    }


@router.put("/posts/{post_id}/update-status")
async def update_notion_status(post_id: str, status: str):
    """
    Update post status in Notion

    Syncs status changes from backend to Notion database.
    """
    storage = get_storage()

    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    notion_page_id = post.get('notion_page_id')
    if not notion_page_id:
        raise HTTPException(
            status_code=400,
            detail="Post not synced to Notion. Sync first using /sync endpoint."
        )

    # TODO: Update status in Notion
    # This will be implemented by notion-integration-expert agent

    # Update local status
    storage.update_post(post_id, {"status": status})

    return MessageResponse(
        message=f"Status update queued for Notion page {notion_page_id}",
        detail="Notion integration pending - see notion-integration-expert agent"
    )


@router.get("/status")
async def get_notion_integration_status():
    """Get Notion integration status"""
    # TODO: Check actual Notion API connection
    # This will be implemented by notion-integration-expert agent

    return {
        "status": "not_configured",
        "message": "Notion API integration pending. Configure API token and database ID to enable.",
        "integration_agent": "notion-integration-expert",
        "required_credentials": ["api_token", "database_id"]
    }
