"""
Cleanup script for timing out old help requests.

Run this as a cron job or scheduled task.
"""
import sys
sys.path.append('.')

from src.services.help_request_service import help_request_service
from src.config.firebase_config import firebase_config
from src.utils.logger import logger


def cleanup_old_requests():
    """Check and timeout old pending requests."""
    logger.info("Starting cleanup of old help requests...")
    
    # Initialize Firebase
    firebase_config.initialize()
    
    try:
        timed_out_count = help_request_service.check_and_timeout_old_requests()
        
        if timed_out_count > 0:
            logger.info(f"✅ Timed out {timed_out_count} old requests")
        else:
            logger.info("No requests to timeout")
        
        return timed_out_count
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}")
        return 0


if __name__ == "__main__":
    result = cleanup_old_requests()
    print(f"Cleanup complete. Timed out {result} requests.")