"""
FastAPI application setup with modern lifespan event handlers.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.api.routes import help_requests, knowledge, supervisor
from src.utils.logger import logger
from src.config.firebase_config import firebase_config


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for startup and shutdown events.
    Replaces deprecated @app.on_event decorators.
    """
    # Startup
    logger.info("AI Supervisor System starting up...")
    firebase_config.initialize()
    logger.info("Firebase initialized")
    logger.info("API ready to accept requests")
    
    yield  # Application runs here
    
    # Shutdown
    logger.info("AI Supervisor System shutting down...")


# Create FastAPI app with lifespan handler
app = FastAPI(
    title="AI Supervisor System",
    description="Human-in-the-loop AI agent system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure properly in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    help_requests.router,
    prefix="/api/help-requests",
    tags=["Help Requests"]
)
app.include_router(
    knowledge.router,
    prefix="/api/knowledge",
    tags=["Knowledge Base"]
)
app.include_router(
    supervisor.router,
    prefix="/api/supervisor",
    tags=["Supervisor Actions"]
)


@app.get("/")
async def root():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "AI Supervisor System",
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Detailed health check."""
    return {
        "status": "healthy",
        "firebase": "connected",
        "api": "running"
    }


if __name__ == "__main__":
    import uvicorn
    from src.config.settings import settings
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development"
    )