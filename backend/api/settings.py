"""
Settings API Router - Following backend-architect.md & config-manager.md
Endpoints for managing application settings
"""
from fastapi import APIRouter
from models.schemas import Settings, SettingsUpdate, APIKeysStatus
from services.storage_service import get_storage
from services.gemini_service import get_gemini_service
from services.notion_service import get_notion_service
import os

router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("", response_model=Settings)
async def get_settings():
    """
    Get application settings

    Returns current configuration including defaults, templates, and UI settings.
    """
    storage = get_storage()
    return storage.get_settings()


@router.get("/api-keys", response_model=APIKeysStatus)
async def get_api_keys_status():
    """
    Get API keys configuration status

    Returns whether each required API key is configured (without exposing actual values).
    """
    gemini = get_gemini_service()
    notion = get_notion_service()

    return APIKeysStatus(
        gemini_configured=gemini.is_configured(),
        notion_configured=notion.api_key is not None,
        notion_database_configured=notion.database_id is not None
    )


@router.put("")
async def update_settings(updates: SettingsUpdate):
    """
    Update application settings

    Can update:
    - API keys (stored in environment, not persisted to JSON)
    - Default template and category
    - Other configuration options

    Note: API keys are only updated for the current session.
    For permanent updates, modify the .env file.
    """
    storage = get_storage()

    # Update environment variables for current session
    if updates.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = updates.gemini_api_key

    if updates.notion_api_key:
        os.environ["NOTION_API_KEY"] = updates.notion_api_key

    if updates.notion_database_id:
        os.environ["NOTION_DATABASE_ID"] = updates.notion_database_id

    # Update persistent settings
    settings_dict = {}

    if updates.default_template:
        settings_dict["default_template"] = updates.default_template

    if updates.default_category:
        settings_dict["default_category"] = updates.default_category

    if settings_dict:
        storage.update_settings(settings_dict)

    return {
        "message": "Settings updated successfully",
        "note": "API keys updated for current session only. Update .env file for permanent changes."
    }
