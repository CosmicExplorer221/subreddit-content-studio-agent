"""
Media API Router
Handles media file management and downloads (structure ready for integration)
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from app.models.schemas import MessageResponse, JobResponse
from app.storage.json_storage import get_storage

router = APIRouter()


@router.post("/download", response_model=JobResponse)
async def download_media(post_id: str, urls: List[str]):
    """
    Download media files for a post

    **Note**: This is a structure endpoint. Actual media download
    will be implemented by the media-handler agent.

    Args:
        post_id: The post ID to associate media with
        urls: List of media URLs to download

    Returns job ID for tracking the download operation.
    """
    storage = get_storage()

    # Verify post exists
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Generate job ID
    job_id = str(uuid.uuid4())

    # TODO: Implement actual media downloading
    # This will be implemented by media-handler agent

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Media download queued for {len(urls)} file(s). "
                f"Integration pending - see media-handler agent."
    )


@router.get("/posts/{post_id}")
async def get_post_media(post_id: str):
    """
    Get all media files associated with a post

    Returns list of media files with metadata.
    """
    storage = get_storage()

    # Verify post exists
    post = storage.get_post(post_id)
    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Get media URLs from post
    reddit_data = post.get('reddit_data', {})
    media_urls = reddit_data.get('media_urls', [])

    # TODO: Return actual downloaded media info
    # This will be implemented by media-handler agent

    return {
        "post_id": post_id,
        "media_count": len(media_urls),
        "media_urls": media_urls,
        "downloaded": [],
        "message": "Media download integration pending - see media-handler agent"
    }


@router.get("/status")
async def get_media_status():
    """Get media storage status and statistics"""
    # TODO: Implement actual storage statistics
    # This will be implemented by media-handler agent

    return {
        "status": "not_configured",
        "storage_path": "storage/",
        "total_files": 0,
        "total_size_gb": 0.0,
        "message": "Media storage integration pending - see media-handler agent"
    }
