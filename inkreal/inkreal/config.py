import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "inkreal-secret-key-change-in-production-2024")
    FIREBASE_CREDENTIALS = os.environ.get("FIREBASE_CREDENTIALS", "serviceAccountKey.json")
    FIREBASE_STORAGE_BUCKET = os.environ.get("FIREBASE_STORAGE_BUCKET", "your-project.appspot.com")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024
    POSTS_PER_PAGE = 20
