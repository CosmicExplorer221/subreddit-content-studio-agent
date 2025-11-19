"""
Posts API Router
Handles LinkedIn post creation, retrieval, and management
"""
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import List, Optional
import uuid
from datetime import datetime
import logging

from app.models.schemas import (
    Post, PostCreate, PostUpdate, MessageResponse, PostStatus,
    ContentGenerationRequest, JobResponse
)
from app.storage.json_storage import get_storage
from app.services.gemini_service import get_gemini_service

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/", response_model=List[Post])
async def list_posts(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[PostStatus] = Query(None, description="Filter by status"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of posts to return")
):
    """List all posts with optional filters"""
    storage = get_storage()

    posts = storage.list_posts(
        category=category,
        status=status.value if status else None,
        limit=limit
    )

    return posts


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    """Get a specific post by ID"""
    storage = get_storage()
    post = storage.get_post(post_id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    return post


@router.post("/", response_model=Post, status_code=201)
async def create_post(post_data: PostCreate):
    """Create a new post"""
    storage = get_storage()

    # Generate unique post ID
    post_id = str(uuid.uuid4())

    # Convert to dict
    data = post_data.model_dump()

    # Create post
    post = storage.create_post(post_id, data)

    return post


@router.put("/{post_id}", response_model=Post)
async def update_post(post_id: str, updates: PostUpdate):
    """Update a post"""
    storage = get_storage()

    # Check if post exists
    existing = storage.get_post(post_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    # Filter out None values
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    # Update post
    post = storage.update_post(post_id, update_data)

    return post


@router.delete("/{post_id}", response_model=MessageResponse)
async def delete_post(post_id: str):
    """Delete a post"""
    storage = get_storage()

    success = storage.delete_post(post_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    return MessageResponse(
        message=f"Post {post_id} deleted successfully"
    )


@router.get("/stats/summary")
async def get_posts_summary():
    """Get summary statistics for posts"""
    storage = get_storage()
    stats = storage.get_stats()

    # Get posts by category
    all_posts = storage.list_posts()
    categories = {}
    for post in all_posts:
        cat = post.get('category', 'unknown')
        categories[cat] = categories.get(cat, 0) + 1

    return {
        "total_posts": stats['posts'],
        "by_status": stats['posts_by_status'],
        "by_category": categories
    }


@router.post("/generate", response_model=JobResponse)
async def generate_content(
    request: ContentGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate LinkedIn content for posts using Gemini API

    This endpoint queues a background job to generate LinkedIn content
    for the specified posts using the configured LLM (Gemini).

    Args:
        request: Content generation request with post IDs, template, and variations
        background_tasks: FastAPI background tasks handler

    Returns:
        Job ID for tracking the generation progress

    Example:
        POST /api/posts/generate
        {
            "post_ids": ["post-uuid-1", "post-uuid-2"],
            "template_id": "professional",
            "variations": 2
        }
    """
    gemini_service = get_gemini_service()

    # Check if Gemini is configured
    if not gemini_service.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini API not configured. Set GEMINI_API_KEY in .env file."
        )

    # Validate post IDs exist
    storage = get_storage()
    for post_id in request.post_ids:
        post = storage.get_post(post_id)
        if not post:
            raise HTTPException(
                status_code=404,
                detail=f"Post {post_id} not found"
            )

    # Generate job ID
    job_id = str(uuid.uuid4())

    # Background task for content generation
    async def generate_task():
        """Background task to generate content"""
        storage = get_storage()

        try:
            # Initialize job
            job_data = {
                "job_id": job_id,
                "type": "content_generation",
                "status": "processing",
                "post_ids": request.post_ids,
                "template_id": request.template_id,
                "variations": request.variations,
                "started_at": datetime.utcnow().isoformat(),
                "results": []
            }
            storage.storage.write("jobs", job_id, job_data)

            # Generate content
            logger.info(f"Starting content generation job {job_id} for {len(request.post_ids)} posts")

            result = await gemini_service.batch_generate(
                post_ids=request.post_ids,
                template_id=request.template_id,
                variations=request.variations
            )

            # Update job with results
            job_data.update({
                "status": "completed",
                "completed_at": datetime.utcnow().isoformat(),
                "total_posts": result['total_posts'],
                "successful": result['successful'],
                "failed": result['failed'],
                "results": result['results'],
                "errors": result.get('errors', [])
            })

            storage.storage.write("jobs", job_id, job_data)
            logger.info(f"Content generation job {job_id} completed: {result['successful']}/{result['total_posts']} successful")

        except Exception as e:
            logger.error(f"Content generation job {job_id} failed: {e}")

            # Update job with error
            job_data = storage.storage.read("jobs", job_id)
            job_data.update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow().isoformat()
            })
            storage.storage.write("jobs", job_id, job_data)

    # Queue background task
    background_tasks.add_task(generate_task)

    return JobResponse(
        job_id=job_id,
        status="queued",
        message=f"Content generation queued for {len(request.post_ids)} post(s). Use /api/reddit/jobs/{job_id} to track progress."
    )
