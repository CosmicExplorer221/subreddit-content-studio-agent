"""
Posts API Router
Handles LinkedIn post creation, retrieval, and management
"""
from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
import uuid
from datetime import datetime

from app.models.schemas import (
    Post, PostCreate, PostUpdate, MessageResponse, PostStatus
)
from app.storage.json_storage import get_storage

router = APIRouter()


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
