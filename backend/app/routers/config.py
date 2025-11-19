"""
Configuration API Router
Handles categories, templates, and settings management
"""
from fastapi import APIRouter, HTTPException
from typing import List

from app.models.schemas import (
    Category, CategoryCreate, CategoryUpdate,
    Template, TemplateCreate, TemplateUpdate,
    Settings, SettingsUpdate,
    MessageResponse, StatsResponse
)
from app.storage.json_storage import get_storage

router = APIRouter()


# ===== Categories =====

@router.get("/categories", response_model=List[Category])
async def list_categories():
    """List all categories"""
    storage = get_storage()
    return storage.list_categories()


@router.get("/categories/{category_id}", response_model=Category)
async def get_category(category_id: str):
    """Get a specific category"""
    storage = get_storage()
    category = storage.get_category(category_id)

    if not category:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    return category


@router.post("/categories", response_model=Category, status_code=201)
async def create_category(category: CategoryCreate):
    """Create a new category"""
    storage = get_storage()

    # Check if category already exists
    if storage.get_category(category.id):
        raise HTTPException(
            status_code=400,
            detail=f"Category '{category.id}' already exists"
        )

    # Create category
    data = category.model_dump()
    created = storage.create_category(category.id, data)

    return created


@router.put("/categories/{category_id}", response_model=Category)
async def update_category(category_id: str, updates: CategoryUpdate):
    """Update a category"""
    storage = get_storage()

    # Check if exists
    if not storage.get_category(category_id):
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    # Filter out None values
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    # Update
    updated = storage.update_category(category_id, update_data)

    return updated


@router.delete("/categories/{category_id}", response_model=MessageResponse)
async def delete_category(category_id: str):
    """Delete a category"""
    storage = get_storage()

    success = storage.delete_category(category_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Category '{category_id}' not found")

    return MessageResponse(message=f"Category '{category_id}' deleted successfully")


# ===== Templates =====

@router.get("/templates", response_model=List[Template])
async def list_templates():
    """List all templates"""
    storage = get_storage()
    return storage.list_templates()


@router.get("/templates/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """Get a specific template"""
    storage = get_storage()
    template = storage.get_template(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    return template


@router.post("/templates", response_model=Template, status_code=201)
async def create_template(template: TemplateCreate):
    """Create a new template"""
    storage = get_storage()

    # Check if template already exists
    if storage.get_template(template.id):
        raise HTTPException(
            status_code=400,
            detail=f"Template '{template.id}' already exists"
        )

    # Create template
    data = template.model_dump()
    created = storage.create_template(template.id, data)

    return created


@router.put("/templates/{template_id}", response_model=Template)
async def update_template(template_id: str, updates: TemplateUpdate):
    """Update a template"""
    storage = get_storage()

    # Check if exists
    if not storage.get_template(template_id):
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    # Filter out None values
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    # Update
    updated = storage.update_template(template_id, update_data)

    return updated


@router.delete("/templates/{template_id}", response_model=MessageResponse)
async def delete_template(template_id: str):
    """Delete a template"""
    storage = get_storage()

    success = storage.delete_template(template_id)

    if not success:
        raise HTTPException(status_code=404, detail=f"Template '{template_id}' not found")

    return MessageResponse(message=f"Template '{template_id}' deleted successfully")


# ===== Settings =====

@router.get("/settings", response_model=Settings)
async def get_settings():
    """Get application settings"""
    storage = get_storage()
    return storage.get_settings()


@router.put("/settings", response_model=Settings)
async def update_settings(updates: SettingsUpdate):
    """Update application settings"""
    storage = get_storage()

    # Filter out None values
    update_data = {k: v for k, v in updates.model_dump().items() if v is not None}

    if not update_data:
        raise HTTPException(status_code=400, detail="No valid updates provided")

    updated = storage.update_settings(update_data)

    return updated


# ===== Statistics =====

@router.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get overall statistics"""
    storage = get_storage()
    return storage.get_stats()
