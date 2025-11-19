# LinkedIn Content Automation - Backend

FastAPI backend for automating LinkedIn content creation from Reddit posts.

## Overview

This backend provides a complete REST API foundation for the LinkedIn Content Automation tool with:

- **JSON File Storage**: Thread-safe, atomic write operations
- **Category Management**: Organize content by topics with subreddit mappings
- **Template System**: Style templates for content generation
- **Post Management**: Full CRUD operations for posts and content
- **Integration Ready**: Structured endpoints for Reddit, Media, Notion integrations

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
│   │   ├── posts.py           # Post management
│   │   ├── reddit.py          # Reddit integration (structure)
│   │   ├── media.py           # Media handling (structure)
│   │   └── notion.py          # Notion sync (structure)
│   └── storage/
│       └── json_storage.py    # JSON file storage manager
├── data/                       # JSON data storage
│   ├── categories/            # Category definitions
│   ├── templates/             # Style templates
│   ├── posts/                 # Posts and content
│   └── settings/              # Application settings
└── requirements.txt
```

## Quick Start

### 1. Install Dependencies

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Initialize Default Data

```bash
# Initialize Railway category and Professional template
python -m app.core.initialize
```

### 3. Start the Server

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Or using Python
python -m app.main
```

The server will start at `http://localhost:8000`

### 4. Access API Documentation

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
```

### Reddit Integration (Structure)

```bash
POST   /api/reddit/fetch                   # Fetch Reddit posts
GET    /api/reddit/categories/{id}/subreddits  # Get category subreddits
GET    /api/reddit/status                  # Integration status
```

### Media Handling (Structure)

```bash
POST   /api/media/download                 # Download media
GET    /api/media/posts/{id}               # Get post media
GET    /api/media/status                   # Storage status
```

### Notion Integration (Structure)

```bash
POST   /api/notion/sync                    # Sync posts to Notion
GET    /api/notion/posts/{id}/status       # Get sync status
PUT    /api/notion/posts/{id}/update-status  # Update status in Notion
GET    /api/notion/status                  # Integration status
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

## Usage Examples

### Create a Post

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

## Integration Guides

The backend has structured endpoints ready for integration. See the agent documentation for implementation:

### Reddit Integration
- **Agent**: `.claude/agents/reddit-integration-expert.md`
- **Endpoints**: `/api/reddit/*`
- **Implementation**: Add Reddit API client to `app/services/`

### Media Handling
- **Agent**: `.claude/agents/media-handler.md`
- **Endpoints**: `/api/media/*`
- **Implementation**: Add media downloader to `app/services/`

### LLM Integration
- **Agent**: `.claude/agents/llm-integration-expert.md`
- **Implementation**: Add Gemini client to `app/services/`
- **Usage**: Generate LinkedIn content from Reddit posts

### Notion Sync
- **Agent**: `.claude/agents/notion-integration-expert.md`
- **Endpoints**: `/api/notion/*`
- **Implementation**: Add Notion client to `app/services/`

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

## Development

### Running Tests

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

1. **Add Reddit Integration**: See `reddit-integration-expert.md`
2. **Add LLM Generation**: See `llm-integration-expert.md`
3. **Add Media Handling**: See `media-handler.md`
4. **Add Notion Sync**: See `notion-integration-expert.md`
5. **Build Frontend**: See `frontend-developer.md`

## Support

For implementation guidance, see the agent documentation in `.claude/agents/`:

- **Backend Architecture**: `backend-architect.md`
- **Configuration**: `config-manager.md`
- **Testing**: `test-engineer.md`
- **Code Review**: `code-reviewer.md`

## License

MIT
