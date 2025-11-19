"""
Pydantic Models - Following backend-architect.md
Data validation and serialization schemas
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


# === Post Models ===

class Comment(BaseModel):
    """Reddit comment model"""
    author: str
    body: str
    score: int


class Post(BaseModel):
    """Source post model (from sample data)"""
    id: str
    title: str
    content: str
    category: str
    score: int
    num_comments: int
    author: str
    created_utc: int
    has_media: bool = False
    media_type: Optional[str] = None
    media_url: Optional[str] = None
    top_comments: List[Comment] = []


class PostResponse(BaseModel):
    """Response model for post listings"""
    posts: List[Post]
    total: int
    category: Optional[str] = None


# === Generation Models ===

class GenerationRequest(BaseModel):
    """Request to generate LinkedIn content"""
    post_ids: List[str] = Field(..., min_items=1, description="List of post IDs to generate content for")
    template_id: Optional[str] = Field(default="railway_professional", description="Template ID to use")
    variations: int = Field(default=1, ge=1, le=3, description="Number of variations to generate per post")


class GeneratedContent(BaseModel):
    """Generated LinkedIn content"""
    id: str
    source_post_id: str
    content: str
    template_id: str
    quality_score: int = Field(ge=0, le=100)
    hashtags: List[str]
    generated_at: str
    variation_number: int = 1


class GeneratedPost(BaseModel):
    """Complete generated post with source"""
    id: str
    source_post: Post
    generated_content: GeneratedContent
    status: str = "draft"  # draft, review, approved, published
    notion_page_id: Optional[str] = None
    notion_synced_at: Optional[str] = None


class GenerationResponse(BaseModel):
    """Response from generation request"""
    success: bool
    generated_posts: List[GeneratedPost] = []
    failed: List[Dict[str, str]] = []
    message: str


# === Template Models ===

class TemplateRequirements(BaseModel):
    """Template content requirements"""
    target_length: Dict[str, int]
    hashtag_count: Dict[str, int]
    tone: str
    include_call_to_action: bool
    structure: str


class Template(BaseModel):
    """Content generation template"""
    id: str
    name: str
    description: str
    category: str
    system_prompt: str
    task_instruction: str
    requirements: TemplateRequirements
    example_hashtags: List[str]


class TemplateResponse(BaseModel):
    """Response model for template listings"""
    templates: List[Template]
    total: int


# === Category Models ===

class Category(BaseModel):
    """Content category"""
    id: str
    name: str
    description: str
    default_template: str
    hashtags: List[str]
    color: str


class CategoryResponse(BaseModel):
    """Response model for category listings"""
    categories: List[Category]
    total: int


# === Notion Models ===

class NotionSyncRequest(BaseModel):
    """Request to sync posts to Notion"""
    generated_post_ids: List[str] = Field(..., min_items=1, description="List of generated post IDs to sync")
    update_existing: bool = Field(default=False, description="Update posts that are already synced")


class NotionSyncResult(BaseModel):
    """Result of a single Notion sync"""
    generated_post_id: str
    success: bool
    notion_page_id: Optional[str] = None
    error: Optional[str] = None


class NotionSyncResponse(BaseModel):
    """Response from Notion sync request"""
    success: bool
    synced: List[NotionSyncResult] = []
    failed: List[NotionSyncResult] = []
    message: str


# === Settings Models ===

class GenerationSettings(BaseModel):
    """Gemini generation settings"""
    temperature: float = Field(ge=0.0, le=2.0)
    max_output_tokens: int = Field(ge=100, le=8000)
    top_p: float = Field(ge=0.0, le=1.0)
    top_k: int = Field(ge=1, le=100)


class BatchSettings(BaseModel):
    """Batch processing settings"""
    max_batch_size: int = Field(ge=1, le=50)
    delay_between_requests_ms: int = Field(ge=0, le=5000)


class UISettings(BaseModel):
    """UI configuration"""
    posts_per_page: int = Field(ge=6, le=50)
    theme: str = Field(pattern="^(light|dark)$")
    show_scores: bool
    show_comments: bool


class Settings(BaseModel):
    """Application settings"""
    app_name: str
    version: str
    default_category: str
    default_template: str
    gemini_model: str
    generation_settings: GenerationSettings
    batch_settings: BatchSettings
    ui_settings: UISettings


class SettingsUpdate(BaseModel):
    """Settings update request"""
    gemini_api_key: Optional[str] = None
    notion_api_key: Optional[str] = None
    notion_database_id: Optional[str] = None
    default_template: Optional[str] = None
    default_category: Optional[str] = None


# === API Key Models ===

class APIKeysStatus(BaseModel):
    """API keys configuration status"""
    gemini_configured: bool
    notion_configured: bool
    notion_database_configured: bool


# === Error Models ===

class ErrorResponse(BaseModel):
    """Error response model"""
    error: str
    detail: Optional[str] = None
    code: Optional[str] = None
