import firebase_admin
from firebase_admin import credentials, firestore, auth as firebase_auth, storage
from config import Config

_app_initialized = False


def init_firebase():
    global _app_initialized
    if not _app_initialized:
        try:
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred, {
                "storageBucket": Config.FIREBASE_STORAGE_BUCKET
            })
            _app_initialized = True
            print("Firebase initialized successfully")
        except Exception as e:
            print(f"Firebase initialization error: {e}")


def get_db():
    init_firebase()
    return firestore.client()


def get_auth():
    init_firebase()
    return firebase_auth


def get_storage():
    init_firebase()
    return storage.bucket()
