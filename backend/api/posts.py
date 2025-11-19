"""
Posts API Router - Following backend-architect.md
Endpoints for managing source posts
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import PostResponse, Post
from services.storage_service import get_storage

router = APIRouter(prefix="/posts", tags=["posts"])


@router.get("", response_model=PostResponse)
async def get_posts(
    category: Optional[str] = Query(None, description="Filter by category"),
    limit: int = Query(50, ge=1, le=100, description="Maximum number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip")
):
    """
    Get all source posts with optional filtering

    - **category**: Filter posts by category (e.g., 'railway')
    - **limit**: Maximum number of posts to return (1-100)
    - **offset**: Number of posts to skip for pagination
    """
    storage = get_storage()
    all_posts = storage.get_posts(category=category)

    # Apply pagination
    total = len(all_posts)
    paginated_posts = all_posts[offset:offset + limit]

    return PostResponse(
        posts=paginated_posts,
        total=total,
        category=category
    )


@router.get("/{post_id}", response_model=Post)
async def get_post(post_id: str):
    """
    Get a specific post by ID

    - **post_id**: The unique identifier of the post
    """
    storage = get_storage()
    post = storage.get_post_by_id(post_id)

    if not post:
        raise HTTPException(status_code=404, detail=f"Post {post_id} not found")

    return post
