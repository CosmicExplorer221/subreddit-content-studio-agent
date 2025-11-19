"""
Generation API Router - Following backend-architect.md & llm-integration-expert.md
Endpoints for generating LinkedIn content
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid
from models.schemas import (
    GenerationRequest,
    GenerationResponse,
    GeneratedPost
)
from services.storage_service import get_storage
from services.gemini_service import get_gemini_service

router = APIRouter(prefix="/generate", tags=["generation"])


@router.post("", response_model=GenerationResponse)
async def generate_content(request: GenerationRequest):
    """
    Generate LinkedIn content from source posts

    - **post_ids**: List of source post IDs to generate content for
    - **template_id**: Template to use for generation (default: railway_professional)
    - **variations**: Number of variations to generate per post (1-3)

    Requires GEMINI_API_KEY to be configured in .env file.
    """
    storage = get_storage()
    gemini = get_gemini_service()

    # Check if Gemini is configured
    if not gemini.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Gemini API not configured. Please add GEMINI_API_KEY to .env file."
        )

    # Get template
    template = storage.get_template_by_id(request.template_id)
    if not template:
        raise HTTPException(
            status_code=404,
            detail=f"Template {request.template_id} not found"
        )

    # Get source posts
    source_posts = []
    for post_id in request.post_ids:
        post = storage.get_post_by_id(post_id)
        if not post:
            raise HTTPException(
                status_code=404,
                detail=f"Post {post_id} not found"
            )
        source_posts.append(post)

    # Generate content
    gen_results = await gemini.generate_multiple(
        posts=source_posts,
        template=template,
        variations=request.variations
    )

    # Create generated posts and save them
    generated_posts = []
    failed = []

    for gen_content in gen_results.get("success", []):
        # Get source post
        source_post = next(
            (p for p in source_posts if p.get("id") == gen_content["source_post_id"]),
            None
        )

        if not source_post:
            failed.append({
                "post_id": gen_content["source_post_id"],
                "error": "Source post not found"
            })
            continue

        # Create generated post object
        generated_post = {
            "id": str(uuid.uuid4()),
            "source_post": source_post,
            "generated_content": gen_content,
            "status": "draft",
            "notion_page_id": None,
            "notion_synced_at": None
        }

        # Save to storage
        storage.save_generated_post(generated_post)

        generated_posts.append(generated_post)

    # Add failures from generation
    for failure in gen_results.get("failed", []):
        failed.append({
            "post_id": failure.get("post_id"),
            "error": failure.get("error", "Generation failed")
        })

    success = len(generated_posts) > 0

    return GenerationResponse(
        success=success,
        generated_posts=generated_posts,
        failed=failed,
        message=f"Successfully generated {len(generated_posts)} posts, {len(failed)} failed"
    )


@router.get("/posts", response_model=List[GeneratedPost])
async def get_generated_posts():
    """
    Get all generated posts

    Returns list of all LinkedIn content that has been generated.
    """
    storage = get_storage()
    posts = storage.get_generated_posts()
    return posts


@router.get("/posts/{post_id}", response_model=GeneratedPost)
async def get_generated_post(post_id: str):
    """
    Get a specific generated post by ID

    - **post_id**: The unique identifier of the generated post
    """
    storage = get_storage()
    post = storage.get_generated_post_by_id(post_id)

    if not post:
        raise HTTPException(
            status_code=404,
            detail=f"Generated post {post_id} not found"
        )

    return post


@router.delete("/posts/{post_id}")
async def delete_generated_post(post_id: str):
    """
    Delete a generated post

    - **post_id**: The unique identifier of the generated post to delete
    """
    storage = get_storage()

    success = storage.delete_generated_post(post_id)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"Generated post {post_id} not found"
        )

    return {"message": f"Successfully deleted post {post_id}"}


@router.put("/posts/{post_id}")
async def update_generated_post(post_id: str, updates: dict):
    """
    Update a generated post

    - **post_id**: The unique identifier of the generated post
    - **updates**: Dictionary of fields to update

    Can update: status, generated_content.content, etc.
    """
    storage = get_storage()

    updated_post = storage.update_generated_post(post_id, updates)

    if not updated_post:
        raise HTTPException(
            status_code=404,
            detail=f"Generated post {post_id} not found"
        )

    return updated_post
