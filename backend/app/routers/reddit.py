"""
Reddit API Router
Handles Reddit post fetching and management
Uses RSS feeds (no API key required) by default
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
import asyncio
from datetime import datetime
import logging

from app.models.schemas import (
    RedditFetchRequest, JobResponse, MessageResponse
)
from app.storage.json_storage import get_storage
from app.services.reddit_rss_service import get_rss_service
from app.services.media_service import get_media_downloader

router = APIRouter()
logger = logging.getLogger(__name__)


async def fetch_and_save_posts(
    job_id: str,
    category: str,
    time_filter: str,
    limit: int,
    min_score: int = None,
    download_media: bool = True
):
    """
    Background task to fetch Reddit posts using RSS (no API key required)
    and optionally download media
    """
    rss_service = get_rss_service()
    storage = get_storage()

    try:
        # Fetch posts from Reddit via RSS
        result = await rss_service.fetch_posts(
            category=category,
            time_filter=time_filter,
            limit=limit,
            min_score=min_score
        )

        # Save posts to storage
        saved_posts = []
        for post_data in result.get('posts', []):
            # Create post in storage
            post_id = str(uuid.uuid4())

            post = storage.create_post(post_id, {
                "category": category,
                "reddit_data": post_data,
                "status": "draft"
            })

            saved_posts.append(post_id)

            # Download media if enabled
            if download_media and post_data.get("media_urls"):
                try:
                    media_downloader = get_media_downloader()

                    # Run media download
                    media_result = await media_downloader.download_post_media(
                        post_id=post_data["reddit_post_id"],
                        category=category,
                        media_urls=post_data["media_urls"],
                        media_type=post_data.get("media_type")
                    )

                    # Update post with media info
                    if media_result["status"] == "success":
                        storage.update_post(post_id, {
                            "metadata": {
                                "media_downloaded": True,
                                "media_summary": media_result["summary"]
                            }
                        })
                except Exception as e:
                    logger.warning(f"Media download failed for {post_id}: {e}")

        # Store job result
        storage.storage.write("jobs", job_id, {
            "job_id": job_id,
            "status": "completed",
            "category": category,
            "posts_fetched": result.get('total_fetched', 0),
            "posts_saved": saved_posts,
            "errors": result.get("errors", []),
            "completed_at": datetime.utcnow().isoformat()
        })

    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        # Store error
        storage.storage.write("jobs", job_id, {
            "job_id": job_id,
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.utcnow().isoformat()
        })


@router.post("/fetch", response_model=JobResponse)
async def fetch_reddit_posts(
    request: RedditFetchRequest,
    background_tasks: BackgroundTasks,
    download_media: bool = True
):
    """
    Fetch posts from Reddit by category using RSS (no API key required)

    This endpoint queues a background job to:
    1. Fetch posts from all subreddits in the category via RSS
    2. Filter posts based on category settings
    3. Save posts to storage
    4. Optionally download media files

    Returns a job ID that can be tracked.

    Note: Uses public RSS feeds, so no Reddit API credentials needed!
    """
    storage = get_storage()

    # Verify category exists
    category = storage.get_category(request.category)
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category '{request.category}' not found. Please create the category first."
        )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Queue background task
    background_tasks.add_task(
        fetch_and_save_posts,
        job_id=job_id,
        category=request.category,
        time_filter=request.time_filter,
        limit=request.limit,
        min_score=request.min_score,
        download_media=download_media
    )

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"Reddit fetch queued for category '{request.category}' "
                f"({len(category['subreddits'])} subreddits, time_filter={request.time_filter}, limit={request.limit}). "
                f"Check /api/reddit/jobs/{job_id} for status."
    )


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str):
    """Get status of a Reddit fetch job"""
    storage = get_storage()

    try:
        job = storage.storage.read("jobs", job_id)
        return job
    except Exception:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")


@router.get("/categories/{category_id}/subreddits")
async def get_category_subreddits(category_id: str):
    """Get list of subreddits for a category"""
    storage = get_storage()

    category = storage.get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    return {
        "category": category_id,
        "subreddits": category.get('subreddits', []),
        "count": len(category.get('subreddits', []))
    }


@router.get("/status")
async def get_reddit_status():
    """
    Get Reddit integration status

    Returns information about the Reddit RSS integration.
    No API credentials required - uses public RSS feeds!
    """
    return {
        "status": "active",
        "method": "RSS feeds (public, no API key required)",
        "message": "Reddit integration active via RSS feeds. No authentication needed!",
        "features": [
            "Fetch top posts from subreddits",
            "Filter by score and comments",
            "Extract post metadata",
            "Download media files"
        ],
        "limitations": [
            "No top comments (RSS doesn't provide them)",
            "Limited to publicly available data",
            "Upvote ratio is estimated"
        ]
    }
