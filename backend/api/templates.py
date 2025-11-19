"""
Templates API Router - Following backend-architect.md
Endpoints for managing content generation templates
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from models.schemas import TemplateResponse, Template
from services.storage_service import get_storage

router = APIRouter(prefix="/templates", tags=["templates"])


@router.get("", response_model=TemplateResponse)
async def get_templates(
    category: Optional[str] = Query(None, description="Filter by category")
):
    """
    Get all templates with optional filtering

    - **category**: Filter templates by category (e.g., 'railway')
    """
    storage = get_storage()
    templates = storage.get_templates(category=category)

    return TemplateResponse(
        templates=templates,
        total=len(templates)
    )


@router.get("/{template_id}", response_model=Template)
async def get_template(template_id: str):
    """
    Get a specific template by ID

    - **template_id**: The unique identifier of the template
    """
    storage = get_storage()
    template = storage.get_template_by_id(template_id)

    if not template:
        raise HTTPException(status_code=404, detail=f"Template {template_id} not found")

    return template
