# LinkedIn Content Automation - Backend

FastAPI backend for automating LinkedIn content creation from Reddit posts.

## Overview

This backend provides a complete REST API for the LinkedIn Content Automation tool with:

- **JSON File Storage**: Thread-safe, atomic write operations
- **Category Management**: Organize content by topics with subreddit mappings
- **Template System**: Style templates for content generation
- **Post Management**: Full CRUD operations for posts and content
- **Reddit Integration**: Fetch posts from multiple subreddits with filtering
- **Media Handling**: Download and manage images and videos from Reddit
- **Gemini LLM**: Generate LinkedIn content using Google's Gemini API
- **Notion Sync**: Batch sync posts to Notion database with duplicate detection

## Architecture

```
backend/
├── app/
│   ├── main.py                 # FastAPI application
│   ├── core/
│   │   ├── config.py          # Application settings
│   │   └── initialize.py      # Default data initialization
│   ├── models/
│   │   └── schemas.py         # Pydantic models
│   ├── routers/
│   │   ├── config.py          # Categories, templates, settings
│   │   ├── posts.py           # Post management & content generation
│   │   ├── reddit.py          # Reddit integration
│   │   ├── media.py           # Media handling
│   │   └── notion.py          # Notion sync
│   ├── services/
│   │   ├── reddit_service.py  # Reddit API client
│   │   ├── media_service.py   # Media downloader
│   │   ├── gemini_service.py  # Gemini content generator
│   │   └── notion_service.py  # Notion database sync
│   └── storage/
│       └── json_storage.py    # JSON file storage manager
├── data/                       # JSON data storage
│   ├── categories/            # Category definitions
│   ├── templates/             # Style templates
│   ├── posts/                 # Posts and content
│   ├── jobs/                  # Background job tracking
│   └── settings/              # Application settings
├── downloads/                  # Downloaded media files
│   └── {category}/            # Organized by category
│       └── {post_id}/         # Per-post media storage
├── requirements.txt
├── test_reddit_media.py        # Reddit + Media integration test
└── test_complete_pipeline.py   # Complete pipeline integration test
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure API Keys

Copy `.env.example` to `.env` and configure your API credentials:

```bash
cp .env.example .env
```

Edit `.env` with your API keys:

```env
# Reddit API (required for fetching posts)
REDDIT_CLIENT_ID=your_client_id_here
REDDIT_CLIENT_SECRET=your_client_secret_here
REDDIT_USERNAME=your_reddit_username
REDDIT_PASSWORD=your_reddit_password

# Gemini API (required for content generation)
GEMINI_API_KEY=your_gemini_api_key_here

# Notion API (optional - for database sync)
NOTION_API_TOKEN=your_notion_token_here
NOTION_DATABASE_ID=your_database_id_here
```

See `.env.example` for detailed instructions on obtaining each API key.

### 3. Initialize Default Data

```bash
# Initialize Railway category and Professional template
python -m app.core.initialize
```

### 4. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using Python
python -m app.main
```

The server will start at `http://localhost:8000`

### 5. Test the Integration

```bash
# Test Reddit + Media integration
python test_reddit_media.py

# Test complete pipeline (Reddit → Gemini → Notion)
python test_complete_pipeline.py
```

### 6. Access API Documentation

- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc
- **OpenAPI JSON**: http://localhost:8000/api/openapi.json

## API Endpoints

### Health & Info

```bash
GET  /                    # API information
GET  /api/health          # Health check with storage stats
```

### Configuration

```bash
# Categories
GET    /api/config/categories              # List all categories
GET    /api/config/categories/{id}         # Get category
POST   /api/config/categories              # Create category
PUT    /api/config/categories/{id}         # Update category
DELETE /api/config/categories/{id}         # Delete category

# Templates
GET    /api/config/templates               # List all templates
GET    /api/config/templates/{id}          # Get template
POST   /api/config/templates               # Create template
PUT    /api/config/templates/{id}          # Update template
DELETE /api/config/templates/{id}          # Delete template

# Settings
GET    /api/config/settings                # Get settings
PUT    /api/config/settings                # Update settings

# Statistics
GET    /api/config/stats                   # Get overall stats
```

### Posts

```bash
GET    /api/posts                          # List posts (with filters)
GET    /api/posts/{id}                     # Get post
POST   /api/posts                          # Create post
PUT    /api/posts/{id}                     # Update post
DELETE /api/posts/{id}                     # Delete post
GET    /api/posts/stats/summary            # Post statistics
POST   /api/posts/generate                 # Generate LinkedIn content (Gemini)
```

### Reddit Integration

```bash
POST   /api/reddit/fetch                   # Fetch Reddit posts with media
GET    /api/reddit/jobs/{job_id}           # Get job status
GET    /api/reddit/categories/{id}/subreddits  # Get category subreddits
GET    /api/reddit/status                  # Integration status
```

### Media Handling

```bash
POST   /api/media/download                 # Download media files
GET    /api/media/posts/{reddit_post_id}   # Get post media info
GET    /api/media/status                   # Storage statistics
```

### Notion Integration

```bash
POST   /api/notion/sync                    # Batch sync posts to Notion
GET    /api/notion/posts/{id}/status       # Get sync status
PUT    /api/notion/posts/{id}/update-status  # Update status in Notion
GET    /api/notion/status                  # Integration & database status
```

## Default Data

The backend is initialized with:

### Railway Category

```json
{
  "id": "railway",
  "name": "Railway & Train Content",
  "description": "Railway enthusiast content, train photography, and rail industry news",
  "subreddits": ["trains", "railroading", "TrainPorn", "modeltrains", "transit"],
  "default_template": "professional",
  "hashtags": ["#Railway", "#Trains", "#RailwayEngineering", "#Transportation", "#Infrastructure"],
  "filters": {
    "min_score": 100,
    "min_comments": 10,
    "max_age_days": 7,
    "exclude_nsfw": true
  }
}
```

### Professional Template

A versatile template for creating professional LinkedIn posts with:
- Professional tone and authentic voice
- Structured format with hooks and takeaways
- 1300-2000 character target length
- 3-5 hashtags
- Minimal emoji usage

## Complete Workflow

### 1. Fetch Reddit Posts

```bash
curl -X POST http://localhost:8000/api/reddit/fetch \
  -H "Content-Type: application/json" \
  -d '{
    "category": "railway",
    "time_filter": "week",
    "limit": 10
  }' \
  --get --data-urlencode "download_media=true"

# Response: {"job_id": "abc123...", "status": "queued"}

# Check job status
curl http://localhost:8000/api/reddit/jobs/abc123...
```

### 2. Generate LinkedIn Content

```bash
curl -X POST http://localhost:8000/api/posts/generate \
  -H "Content-Type: application/json" \
  -d '{
    "post_ids": ["post-uuid-1", "post-uuid-2"],
    "template_id": "professional",
    "variations": 2
  }'

# Response: {"job_id": "def456...", "status": "queued"}
```

### 3. Sync to Notion

```bash
curl -X POST http://localhost:8000/api/notion/sync \
  -H "Content-Type: application/json" \
  -d '{
    "post_ids": ["post-uuid-1", "post-uuid-2"],
    "update_existing": false
  }'

# Response: {"job_id": "ghi789...", "status": "queued"}
```

## API Examples

### Create a Post Manually

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -d '{
    "category": "railway",
    "reddit_data": {
      "reddit_post_id": "abc123",
      "subreddit": "trains",
      "title": "Amazing vintage locomotive restoration",
      "author": "trainenthusiast",
      "score": 500,
      "num_comments": 45,
      "upvote_ratio": 0.98,
      "created_utc": 1704067200,
      "permalink": "/r/trains/comments/abc123",
      "media_urls": []
    },
    "status": "draft"
  }'
```

### List Categories

```bash
curl http://localhost:8000/api/config/categories
```

### Get Statistics

```bash
curl http://localhost:8000/api/config/stats
```

### Update Post Status

```bash
curl -X PUT http://localhost:8000/api/posts/{post_id} \
  -H "Content-Type: application/json" \
  -d '{"status": "published"}'
```

## JSON Storage

The backend uses JSON files for storage with:

### Features

- **Thread-safe operations**: Locks per file
- **Atomic writes**: Temp file + rename pattern
- **Auto-created directories**: Collections created on demand
- **UTF-8 encoding**: Full Unicode support
- **Pretty-printed JSON**: Human-readable files

### File Structure

```
data/
├── categories/
│   └── railway.json
├── templates/
│   └── professional.json
├── posts/
│   ├── {uuid-1}.json
│   └── {uuid-2}.json
└── settings/
    └── app_settings.json
```

### Storage API

```python
from app.storage.json_storage import get_storage

storage = get_storage()

# Categories
category = storage.get_category("railway")
all_categories = storage.list_categories()

# Templates
template = storage.get_template("professional")

# Posts
posts = storage.list_posts(category="railway", status="draft")
post = storage.get_post(post_id)

# Settings
settings = storage.get_settings()

# Statistics
stats = storage.get_stats()
```

## Integrations

### Reddit Integration ✅ Implemented

**Service**: `app/services/reddit_service.py`
**Features**:
- Multi-subreddit fetching by category
- Content filtering (score, comments, age, NSFW)
- Top comments extraction
- Media URL detection (images, videos, galleries)
- Rate limiting (60 req/min)
- Background job processing

**Configuration**:
```env
REDDIT_CLIENT_ID=your_client_id
REDDIT_CLIENT_SECRET=your_client_secret
REDDIT_USERNAME=your_username
REDDIT_PASSWORD=your_password
```

Get credentials: https://www.reddit.com/prefs/apps

### Media Handling ✅ Implemented

**Service**: `app/services/media_service.py`
**Features**:
- Async media downloads (aiohttp)
- Reddit video support (DASH format with quality fallbacks)
- Image support (JPG, PNG, GIF, WebP)
- File validation with magic numbers
- Organized storage: `downloads/{category}/{post_id}/`
- Storage statistics

### Gemini LLM ✅ Implemented

**Service**: `app/services/gemini_service.py`
**Features**:
- LinkedIn content generation from Reddit posts
- Template-based prompts
- Quality scoring (0-100)
- Multiple variations support
- Hashtag extraction and validation
- Character count validation

**Configuration**:
```env
GEMINI_API_KEY=your_api_key
```

Get API key: https://makersuite.google.com/app/apikey

### Notion Sync ✅ Implemented

**Service**: `app/services/notion_service.py`
**Features**:
- Batch sync to Notion database
- Duplicate detection by Reddit post ID
- Create or update pages
- Rich page content with blocks
- Multi-select hashtags
- Status tracking

**Configuration**:
```env
NOTION_API_TOKEN=your_token
NOTION_DATABASE_ID=your_database_id
```

Get credentials: https://www.notion.so/my-integrations

**Required Database Properties**:
- Title (title)
- Category (select)
- Status (select)
- Reddit Post ID (rich_text)
- Subreddit (rich_text)
- Score (number)
- Comments (number)
- Quality Score (number)
- Character Count (number)
- Template (select)
- Hashtags (multi_select)
- Reddit URL (url)

## Configuration

### Environment Variables

Copy `.env.example` to `.env`:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Required
APP_NAME="LinkedIn Content Automation"
DEBUG=true

# Optional (for integrations)
REDDIT_CLIENT_ID=your_client_id
GEMINI_API_KEY=your_api_key
NOTION_API_TOKEN=your_token
```

### Adding Categories

```python
from app.storage.json_storage import get_storage

storage = get_storage()

storage.create_category("tech", {
    "name": "Technology",
    "description": "Tech industry content",
    "subreddits": ["programming", "technology"],
    "default_template": "professional",
    "hashtags": ["#Tech", "#Innovation"],
    "filters": {
        "min_score": 100,
        "min_comments": 10,
        "max_age_days": 7
    }
})
```

### Adding Templates

```python
storage.create_template("casual", {
    "name": "Casual",
    "description": "Casual conversational style",
    "system_prompt": "Create casual, friendly LinkedIn posts...",
    "task_instruction": "Write in a conversational tone...",
    "target_length": {"min": 1000, "max": 1500},
    "hashtag_count": {"min": 2, "max": 4}
})
```

## Testing

### Integration Tests

```bash
# Test Reddit + Media integration
python test_reddit_media.py

# Test complete pipeline (Reddit → Gemini → Notion)
python test_complete_pipeline.py
```

### Unit Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio httpx

# Run tests
pytest tests/
```

### Code Quality

```bash
# Format code
black app/

# Lint
pylint app/

# Type checking
mypy app/
```

## Production Deployment

### Using Uvicorn

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Gunicorn

```bash
gunicorn app.main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app/ app/
COPY data/ data/

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## Troubleshooting

### Port Already in Use

```bash
# Change port in command
uvicorn app.main:app --port 8001

# Or kill process on port 8000
lsof -ti:8000 | xargs kill -9
```

### JSON Decode Error

If you encounter JSON errors, check that data files are valid JSON:

```bash
python -m json.tool data/categories/railway.json
```

### Permission Errors

Ensure the data directory is writable:

```bash
chmod -R 755 data/
```

## Next Steps

1. ✅ **Reddit Integration**: Implemented - fetch posts from subreddits
2. ✅ **Media Handling**: Implemented - download images and videos
3. ✅ **LLM Generation**: Implemented - generate content with Gemini
4. ✅ **Notion Sync**: Implemented - batch sync to database
5. **Build Frontend**: See `frontend-developer.md` for UI development
6. **Add More Categories**: Create categories for different content types
7. **Customize Templates**: Create templates for different writing styles
8. **Schedule Publishing**: Add scheduling and auto-publish features

## Support

For implementation guidance, see the agent documentation in `.claude/agents/`:

- **Backend Architecture**: `backend-architect.md`
- **Configuration**: `config-manager.md`
- **Testing**: `test-engineer.md`
- **Code Review**: `code-reviewer.md`

## License

MIT
