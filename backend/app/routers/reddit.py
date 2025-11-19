"""
Reddit API Router
Handles Reddit post fetching and management
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid
import asyncio

from app.models.schemas import (
    RedditFetchRequest, JobResponse, MessageResponse
)
from app.storage.json_storage import get_storage
from app.services.reddit_service import get_reddit_service
from app.services.media_service import get_media_downloader

router = APIRouter()


async def fetch_and_save_posts(
    job_id: str,
    category: str,
    time_filter: str,
    limit: int,
    min_score: int = None,
    download_media: bool = True
):
    """
    Background task to fetch Reddit posts and optionally download media
    """
    reddit_service = get_reddit_service()
    storage = get_storage()

    try:
        # Fetch posts from Reddit
        result = reddit_service.fetch_posts(
            category=category,
            time_filter=time_filter,
            limit=limit,
            min_score=min_score
        )

        if result["status"] != "success":
            # Store error result
            storage.storage.write("jobs", job_id, {
                "job_id": job_id,
                "status": "failed",
                "error": result.get("error", "Unknown error"),
                "completed_at": result.get("fetched_at")
            })
            return

        posts = result["posts"]

        # Save posts to storage
        saved_posts = []
        for post_data in posts:
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

        # Store job result
        storage.storage.write("jobs", job_id, {
            "job_id": job_id,
            "status": "completed",
            "category": category,
            "posts_fetched": len(posts),
            "posts_saved": saved_posts,
            "filters": result["filters"],
            "errors": result.get("errors", []),
            "completed_at": result["fetched_at"]
        })

    except Exception as e:
        # Store error
        storage.storage.write("jobs", job_id, {
            "job_id": job_id,
            "status": "failed",
            "error": str(e)
        })


@router.post("/fetch", response_model=JobResponse)
async def fetch_reddit_posts(
    request: RedditFetchRequest,
    background_tasks: BackgroundTasks,
    download_media: bool = True
):
    """
    Fetch posts from Reddit by category

    This endpoint queues a background job to:
    1. Fetch posts from all subreddits in the category
    2. Filter posts based on category settings
    3. Extract top comments
    4. Save posts to storage
    5. Optionally download media files

    Returns a job ID that can be tracked.
    """
    reddit_service = get_reddit_service()

    # Check if Reddit is configured
    if not reddit_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Reddit API not configured. Please set REDDIT_CLIENT_ID, "
                   "REDDIT_CLIENT_SECRET, REDDIT_USERNAME, and REDDIT_PASSWORD in .env file."
        )

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

    job = storage.storage.read("jobs", job_id)

    if not job:
        raise HTTPException(status_code=404, detail=f"Job {job_id} not found")

    return job


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

    Returns information about the Reddit API connection and configuration.
    """
    reddit_service = get_reddit_service()

    if not reddit_service.is_configured():
        return {
            "status": "not_configured",
            "message": "Reddit API not configured. Set credentials in .env file.",
            "required_credentials": [
                "REDDIT_CLIENT_ID",
                "REDDIT_CLIENT_SECRET",
                "REDDIT_USERNAME",
                "REDDIT_PASSWORD"
            ]
        }

    try:
        # Test connection
        username = reddit_service.reddit.user.me().name

        return {
            "status": "connected",
            "username": username,
            "message": f"Connected to Reddit as u/{username}",
            "rate_limit": "60 requests/minute"
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Reddit API error: {str(e)}"
        }
