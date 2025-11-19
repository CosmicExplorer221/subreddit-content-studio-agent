"""
FastAPI Application Main Entry Point
LinkedIn Content Automation Backend
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from datetime import datetime
import uvicorn

from app.routers import reddit, media, posts, notion, config
from app.core.config import settings
from app.storage.json_storage import get_storage

# Create FastAPI app
app = FastAPI(
    title="LinkedIn Content Automation API",
    description="Backend API for automating LinkedIn content creation from Reddit",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "name": "LinkedIn Content Automation API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/api/docs",
        "health": "/api/health"
    }


# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    storage = get_storage()
    stats = storage.get_stats()

    return {
        "status": "healthy",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat(),
        "storage": {
            "connected": True,
            "stats": stats
        }
    }


# Include routers
app.include_router(reddit.router, prefix="/api/reddit", tags=["Reddit"])
app.include_router(media.router, prefix="/api/media", tags=["Media"])
app.include_router(posts.router, prefix="/api/posts", tags=["Posts"])
app.include_router(notion.router, prefix="/api/notion", tags=["Notion"])
app.include_router(config.router, prefix="/api/config", tags=["Configuration"])


# Exception handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Not found", "detail": str(exc)}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": str(exc)}
    )


# Startup event
@app.on_event("startup")
async def startup_event():
    """Initialize application on startup"""
    print("=" * 60)
    print("🚀 LinkedIn Content Automation API Starting...")
    print("=" * 60)

    # Initialize storage
    storage = get_storage()
    stats = storage.get_stats()

    print(f"✓ Storage initialized")
    print(f"  - Categories: {stats['categories']}")
    print(f"  - Templates: {stats['templates']}")
    print(f"  - Posts: {stats['posts']}")

    # Check for initial data
    if stats['categories'] == 0:
        print("⚠ No categories found - run initialization script")

    print("=" * 60)
    print("✓ Server ready at http://localhost:8000")
    print("✓ API docs at http://localhost:8000/api/docs")
    print("=" * 60)


# Shutdown event
@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    print("\n" + "=" * 60)
    print("👋 Shutting down LinkedIn Content Automation API")
    print("=" * 60)


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
