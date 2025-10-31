"""
Main entry point to run the API server.
"""
import uvicorn
from src.config.settings import settings
from src.utils.logger import logger


if __name__ == "__main__":
    logger.info("Starting AI Supervisor System...")
    logger.info(f"Environment: {settings.app_env}")
    logger.info(f"Host: {settings.app_host}:{settings.app_port}")
    
    uvicorn.run(
        "src.api.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.app_env == "development",
        log_level=settings.log_level.lower()
    )