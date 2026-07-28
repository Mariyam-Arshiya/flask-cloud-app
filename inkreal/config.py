import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "inkreal-secret-key-change-in-production-2024")
    FIREBASE_CREDENTIALS = os.environ.get("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
    FIREBASE_DATABASE_URL = os.environ.get("FIREBASE_DATABASE_URL", "https://your-project.firebaseio.com")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "your-project.appspot.com")
    FIREBASE_API_KEY = os.environ.get("FIREBASE_API_KEY", "your-api-key")
    FIREBASE_AUTH_DOMAIN = os.environ.get("FIREBASE_AUTH_DOMAIN", "your-project.firebaseapp.com")
    FIREBASE_PROJECT_ID = os.environ.get("FIREBASE_PROJECT_ID", "your-project-id")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    POSTS_PER_PAGE = 20
