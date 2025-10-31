"""
Firebase initialization and configuration.
"""
import firebase_admin
from firebase_admin import credentials, db
from src.config.settings import settings
from src.utils.logger import logger


class FirebaseConfig:
    """Firebase configuration and initialization."""
    
    _initialized = False
    _db_ref = None
    
    @classmethod
    def initialize(cls):
        """Initialize Firebase Admin SDK."""
        if cls._initialized:
            logger.info("Firebase already initialized")
            return
        
        try:
            cred = credentials.Certificate(settings.firebase_credentials_path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': settings.firebase_database_url
            })
            cls._initialized = True
            logger.info("Firebase initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Firebase: {str(e)}")
            raise
    
    @classmethod
    def get_database(cls):
        """Get Firebase Realtime Database reference."""
        if not cls._initialized:
            cls.initialize()
        return db.reference()


# Initialize on import
firebase_config = FirebaseConfig()