"""
Notion API Router - Following backend-architect.md & notion-integration-expert.md
Endpoints for syncing content to Notion
"""
from fastapi import APIRouter, HTTPException
from models.schemas import NotionSyncRequest, NotionSyncResponse, NotionSyncResult
from services.storage_service import get_storage
from services.notion_service import get_notion_service
from datetime import datetime

router = APIRouter(prefix="/notion", tags=["notion"])


@router.post("/sync", response_model=NotionSyncResponse)
async def sync_to_notion(request: NotionSyncRequest):
    """
    Sync generated posts to Notion database

    - **generated_post_ids**: List of generated post IDs to sync
    - **update_existing**: If true, update posts that are already synced (default: false)

    Requires NOTION_API_KEY and NOTION_DATABASE_ID to be configured in .env file.
    """
    storage = get_storage()
    notion = get_notion_service()

    # Check if Notion is configured
    if not notion.is_configured():
        raise HTTPException(
            status_code=503,
            detail="Notion not configured. Please add NOTION_API_KEY and NOTION_DATABASE_ID to .env file."
        )

    # Get generated posts
    generated_posts = []
    not_found = []

    for post_id in request.generated_post_ids:
        post = storage.get_generated_post_by_id(post_id)
        if not post:
            not_found.append(post_id)
        else:
            generated_posts.append(post)

    if not_found:
        raise HTTPException(
            status_code=404,
            detail=f"Generated posts not found: {', '.join(not_found)}"
        )

    # Sync to Notion
    sync_results = await notion.sync_multiple(
        generated_posts=generated_posts,
        update_existing=request.update_existing
    )

    # Update storage with Notion page IDs
    synced_results = []
    failed_results = []

    for result in sync_results.get("synced", []):
        post_id = result.get("generated_post_id")
        notion_page_id = result.get("notion_page_id")

        # Update post with Notion info
        storage.update_generated_post(post_id, {
            "notion_page_id": notion_page_id,
            "notion_synced_at": datetime.utcnow().isoformat()
        })

        synced_results.append(NotionSyncResult(
            generated_post_id=post_id,
            success=True,
            notion_page_id=notion_page_id
        ))

    for result in sync_results.get("failed", []):
        failed_results.append(NotionSyncResult(
            generated_post_id=result.get("generated_post_id"),
            success=False,
            error=result.get("error")
        ))

    success = len(synced_results) > 0

    return NotionSyncResponse(
        success=success,
        synced=synced_results,
        failed=failed_results,
        message=f"Successfully synced {len(synced_results)} posts, {len(failed_results)} failed"
    )


@router.get("/status")
async def get_notion_status():
    """
    Check Notion configuration status

    Returns whether Notion API key and database ID are configured.
    """
    notion = get_notion_service()

    return {
        "configured": notion.is_configured(),
        "has_api_key": notion.api_key is not None,
        "has_database_id": notion.database_id is not None
    }
