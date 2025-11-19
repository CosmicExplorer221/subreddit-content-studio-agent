"""
Categories API Router - Following backend-architect.md
Endpoints for managing content categories
"""
from fastapi import APIRouter, HTTPException
from models.schemas import CategoryResponse, Category
from services.storage_service import get_storage

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("", response_model=CategoryResponse)
async def get_categories():
    """Get all content categories"""
    storage = get_storage()
    categories = storage.get_categories()

    return CategoryResponse(
        categories=categories,
        total=len(categories)
    )


@router.get("/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """
    Get a specific category by ID

    - **category_id**: The unique identifier of the category
    """
    storage = get_storage()
    category = storage.get_category_by_id(category_id)

    if not category:
        raise HTTPException(status_code=404, detail=f"Category {category_id} not found")

    return category
