"""
Pydantic models and schemas for API requests/responses
"""
from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# Enums
class PostStatus(str, Enum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"
    SCHEDULED = "scheduled"
    PUBLISHED = "published"
    REJECTED = "rejected"


class MediaType(str, Enum):
    IMAGE = "image"
    VIDEO = "video"
    GALLERY = "gallery"


# Category Models
class CategoryBase(BaseModel):
    name: str = Field(..., description="Category name")
    description: str = Field(..., description="Category description")
    subreddits: List[str] = Field(..., description="List of subreddit names")
    default_template: str = Field(..., description="Default template ID")
    hashtags: List[str] = Field(default_factory=list, description="Default hashtags")
    filters: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "min_score": 100,
            "min_comments": 10,
            "max_age_days": 7,
            "exclude_nsfw": True
        },
        description="Content filters"
    )


class CategoryCreate(CategoryBase):
    id: str = Field(..., description="Unique category identifier")


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    subreddits: Optional[List[str]] = None
    default_template: Optional[str] = None
    hashtags: Optional[List[str]] = None
    filters: Optional[Dict[str, Any]] = None


class Category(CategoryBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Template Models
class TemplateBase(BaseModel):
    name: str = Field(..., description="Template name")
    description: str = Field(..., description="Template description")
    system_prompt: str = Field(..., description="System prompt for LLM")
    task_instruction: str = Field(..., description="Task instruction for LLM")
    requirements: List[str] = Field(default_factory=list, description="Content requirements")
    target_length: Dict[str, int] = Field(
        default_factory=lambda: {"min": 1300, "max": 2000},
        description="Target character length"
    )
    hashtag_count: Dict[str, int] = Field(
        default_factory=lambda: {"min": 3, "max": 5},
        description="Hashtag count range"
    )
    style: Dict[str, str] = Field(
        default_factory=lambda: {
            "tone": "professional",
            "voice": "authoritative",
            "emoji_usage": "minimal"
        },
        description="Style settings"
    )
    examples: List[str] = Field(default_factory=list, description="Example posts")


class TemplateCreate(TemplateBase):
    id: str = Field(..., description="Unique template identifier")


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    task_instruction: Optional[str] = None
    requirements: Optional[List[str]] = None
    target_length: Optional[Dict[str, int]] = None
    hashtag_count: Optional[Dict[str, int]] = None
    style: Optional[Dict[str, str]] = None
    examples: Optional[List[str]] = None


class Template(TemplateBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Post Models
class RedditPostData(BaseModel):
    reddit_post_id: str
    subreddit: str
    title: str
    content: Optional[str] = None
    url: Optional[str] = None
    author: str
    score: int
    num_comments: int
    upvote_ratio: float
    created_utc: int
    permalink: str
    flair: Optional[str] = None
    media_type: Optional[MediaType] = None
    media_urls: List[str] = Field(default_factory=list)


class LinkedInContent(BaseModel):
    content: str = Field(..., description="Generated LinkedIn post content")
    quality_score: Optional[float] = Field(None, ge=0, le=100, description="Quality score 0-100")
    hashtags: List[str] = Field(default_factory=list)
    char_count: Optional[int] = None

    @validator('char_count', always=True)
    def set_char_count(cls, v, values):
        if 'content' in values:
            return len(values['content'])
        return v


class PostBase(BaseModel):
    category: str = Field(..., description="Content category")
    reddit_data: RedditPostData
    linkedin_content: Optional[LinkedInContent] = None
    template_id: Optional[str] = None
    status: PostStatus = Field(default=PostStatus.DRAFT)
    scheduled_date: Optional[str] = None
    published_date: Optional[str] = None
    notion_page_id: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    category: Optional[str] = None
    linkedin_content: Optional[LinkedInContent] = None
    template_id: Optional[str] = None
    status: Optional[PostStatus] = None
    scheduled_date: Optional[str] = None
    published_date: Optional[str] = None
    notion_page_id: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class Post(PostBase):
    id: str
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


# Reddit Fetch Request
class RedditFetchRequest(BaseModel):
    category: str = Field(..., description="Category to fetch posts from")
    time_filter: str = Field(default="week", description="Time filter: hour, day, week, month, year")
    limit: int = Field(default=50, ge=1, le=100, description="Number of posts to fetch")
    min_score: Optional[int] = Field(None, description="Minimum score filter")


# Content Generation Request
class ContentGenerationRequest(BaseModel):
    post_ids: List[str] = Field(..., description="List of post IDs to generate content for")
    template_id: Optional[str] = Field(None, description="Template to use (uses category default if not specified)")
    variations: int = Field(default=1, ge=1, le=3, description="Number of variations to generate")


# Notion Sync Request
class NotionSyncRequest(BaseModel):
    post_ids: List[str] = Field(..., description="List of post IDs to sync")
    update_existing: bool = Field(default=False, description="Update existing pages")


# Settings Models
class Settings(BaseModel):
    app_name: str = "LinkedIn Content Automation"
    version: str = "1.0.0"
    reddit: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "rate_limit_rpm": 60,
            "retry_attempts": 3
        }
    )
    gemini: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "model": "gemini-1.5-pro",
            "temperature": 0.7,
            "max_tokens": 2048
        }
    )
    notion: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "rate_limit_rps": 3
        }
    )
    storage: Optional[Dict[str, Any]] = Field(
        default_factory=lambda: {
            "max_size_gb": 50,
            "cleanup_days": 30
        }
    )


class SettingsUpdate(BaseModel):
    reddit: Optional[Dict[str, Any]] = None
    gemini: Optional[Dict[str, Any]] = None
    notion: Optional[Dict[str, Any]] = None
    storage: Optional[Dict[str, Any]] = None


# Response Models
class MessageResponse(BaseModel):
    message: str
    detail: Optional[str] = None


class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str


class StatsResponse(BaseModel):
    categories: int
    templates: int
    posts: int
    posts_by_status: Dict[str, int]


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
