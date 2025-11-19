"""
Media API Router
Handles media file management and downloads
"""
from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import List
import uuid

from app.models.schemas import MessageResponse, JobResponse
from app.storage.json_storage import get_storage
from app.services.media_service import get_media_downloader

router = APIRouter()


@router.post("/download", response_model=JobResponse)
async def download_media(
    post_id: str,
    urls: List[str],
    category: str,
    background_tasks: BackgroundTasks
):
    """
    Download media files for a post

    Args:
        post_id: The Reddit post ID (not the database ID)
        urls: List of media URLs to download
        category: Category for organizing downloads

    Returns job ID for tracking the download operation.
    """
    # Generate job ID
    job_id = str(uuid.uuid4())

    # Download media in background
    async def download_task():
        downloader = get_media_downloader()
        result = await downloader.download_post_media(
            post_id=post_id,
            category=category,
            media_urls=urls
        )

        # Store job result
        storage = get_storage()
        storage.storage.write("jobs", job_id, {
            "job_id": job_id,
            "type": "media_download",
            "status": "completed",
            "result": result
        })

    background_tasks.add_task(download_task)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"Media download queued for {len(urls)} file(s)."
    )


@router.get("/posts/{reddit_post_id}")
async def get_post_media(reddit_post_id: str, category: str):
    """
    Get all media files associated with a Reddit post

    Args:
        reddit_post_id: The Reddit post ID
        category: Category the post belongs to

    Returns list of media files with metadata.
    """
    downloader = get_media_downloader()

    media_info = downloader.get_post_media_info(category, reddit_post_id)

    return media_info


@router.get("/status")
async def get_media_status():
    """Get media storage status and statistics"""
    downloader = get_media_downloader()

    stats = downloader.get_storage_stats()

    return {
        "status": "active",
        "storage_path": str(downloader.base_path),
        **stats
    }
