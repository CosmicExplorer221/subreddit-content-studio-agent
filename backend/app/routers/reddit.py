"""
Reddit API Router
Handles Reddit post fetching and management (structure ready for integration)
"""
from fastapi import APIRouter, HTTPException
from typing import List
import uuid

from app.models.schemas import (
    RedditFetchRequest, JobResponse, MessageResponse
)
from app.storage.json_storage import get_storage

router = APIRouter()


@router.post("/fetch", response_model=JobResponse)
async def fetch_reddit_posts(request: RedditFetchRequest):
    """
    Fetch posts from Reddit by category

    **Note**: This is a structure endpoint. Actual Reddit integration
    will be implemented by the reddit-integration-expert agent.

    Returns a job ID that can be used to track the fetch operation.
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

    # TODO: Implement actual Reddit fetching
    # This will be implemented by reddit-integration-expert agent
    # For now, return a pending job response

    return JobResponse(
        job_id=job_id,
        status="pending",
        message=f"Reddit fetch queued for category '{request.category}' "
                f"(time_filter={request.time_filter}, limit={request.limit}). "
                f"Integration pending - see reddit-integration-expert agent."
    )


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
    # TODO: Check actual Reddit API connection status
    # This will be implemented by reddit-integration-expert agent

    return {
        "status": "not_configured",
        "message": "Reddit API integration pending. Configure API credentials to enable.",
        "integration_agent": "reddit-integration-expert",
        "required_credentials": ["client_id", "client_secret", "username", "password"]
    }
