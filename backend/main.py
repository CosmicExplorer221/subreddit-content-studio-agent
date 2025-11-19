"""
FastAPI Main Application - Following backend-architect.md
LinkedIn Content Studio - Railway Edition
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Import routers
from api import posts, templates, categories, generation, notion, settings

# Create FastAPI app
app = FastAPI(
    title="LinkedIn Content Studio API",
    description="AI-powered LinkedIn content generation from Railway/Transit content",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(posts.router, prefix="/api")
app.include_router(templates.router, prefix="/api")
app.include_router(categories.router, prefix="/api")
app.include_router(generation.router, prefix="/api")
app.include_router(notion.router, prefix="/api")
app.include_router(settings.router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "LinkedIn Content Studio API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "status": "running"
    }


@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    from services.storage_service import get_storage
    from services.gemini_service import get_gemini_service
    from services.notion_service import get_notion_service

    storage = get_storage()
    gemini = get_gemini_service()
    notion = get_notion_service()

    # Check data availability
    posts_count = len(storage.get_posts())
    templates_count = len(storage.get_templates())

    return {
        "status": "healthy",
        "services": {
            "storage": "ok",
            "gemini": "configured" if gemini.is_configured() else "not_configured",
            "notion": "configured" if notion.is_configured() else "not_configured"
        },
        "data": {
            "posts": posts_count,
            "templates": templates_count
        }
    }


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting LinkedIn Content Studio API...")
    logger.info("Docs available at: http://localhost:8000/api/docs")

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
