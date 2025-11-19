"""
Notion API Router
Handles Notion integration and syncing
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
from datetime import datetime
import logging

from app.models.schemas import NotionSyncRequest, JobResponse, MessageResponse
from app.storage.json_storage import get_storage
from app.services.notion_service import get_notion_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/sync", response_model=JobResponse)
async def sync_to_notion(
    request: NotionSyncRequest,
    background_tasks: BackgroundTasks
):
    """
    Sync posts to Notion database

    This endpoint queues a background job to sync posts to a Notion database.
    It includes automatic duplicate detection based on Reddit post IDs.

    Args:
        request: Sync request with post IDs and update options
        background_tasks: FastAPI background tasks handler

    Returns:
        Job ID for tracking the sync operation

    Example:
        POST /api/notion/sync
        {
            "post_ids": ["post-uuid-1", "post-uuid-2"],
            "update_existing": false
        }
    """
    notion_service = get_notion_service()
    storage = get_storage()

    # Check if Notion is configured
    if not notion_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Notion API not configured. Set NOTION_API_TOKEN and NOTION_DATABASE_ID in .env file."
        )

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

    # Background task for Notion syncing
    async def sync_task():
        """Background task to sync posts to Notion"""
        storage = get_storage()

        try:
            # Initialize job
            job_data = {
                "job_id": job_id,
                "type": "notion_sync",
                "status": "processing",
                "post_ids": request.post_ids,
                "update_existing": request.update_existing,
                "started_at": datetime.utcnow().isoformat()
            }
            storage.storage.write("jobs", job_id, job_data)

            # Sync to Notion
            logger.info(f"Starting Notion sync job {job_id} for {len(request.post_ids)} posts")

            result = await notion_service.batch_sync(
                post_ids=request.post_ids,
                update_existing=request.update_existing
            )

            # Update job with results
            job_data.update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "total_posts": result['total_posts'],
                "created": result['created'],
                "updated": result['updated'],
                "duplicates": result['duplicates'],
                "failed": result['failed'],
                "results": result['results']
            })

            storage.storage.write("jobs", job_id, job_data)
            logger.info(
                f"Notion sync job {job_id} completed: "
                f"{result['created']} created, {result['updated']} updated, "
                f"{result['duplicates']} duplicates, {result['failed']} failed"
            )

        except Exception as e:
            logger.error(f"Notion sync job {job_id} failed: {e}")

            # Update job with error
            job_data = storage.storage.read("jobs", job_id)
            job_data.update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })
            storage.storage.write("jobs", job_id, job_data)

    # Queue background task
    background_tasks.add_task(sync_task)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"Notion sync queued for {len(request.post_ids)} post(s). Use /api/reddit/jobs/{job_id} to track progress."
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
    """
    Get Notion integration status

    Returns information about the Notion API connection and database.
    """
    notion_service = get_notion_service()

    if not notion_service.is_configured():
        return {
            "status": "not_configured",
            "message": "Notion API not configured. Set NOTION_API_TOKEN and NOTION_DATABASE_ID in .env file.",
            "required_credentials": ["NOTION_API_TOKEN", "NOTION_DATABASE_ID"]
        }

    # Get database info
    db_info = notion_service.get_database_info()

    return db_info
