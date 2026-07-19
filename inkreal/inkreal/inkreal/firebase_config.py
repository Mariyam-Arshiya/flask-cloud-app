import os
import firebase_admin
from firebase_admin import credentials, firestore
from config import Config

_db = None
_initialized = False


def init_firebase():
    global _initialized, _db
    if _initialized:
        return True
    try:
        if not os.path.exists(Config.FIREBASE_CREDENTIALS):
            print("=" * 60)
            print("FIREBASE KEY MISSING")
            print("=" * 60)
            print(f"Expected file: {Config.FIREBASE_CREDENTIALS}")
            print("Get it from: Firebase Console > Project Settings")
            print("             > Service Accounts > Generate New Private Key")
            print("Then place it in this folder as serviceAccountKey.json")
            print("=" * 60)
            return False
        if not firebase_admin._apps:
            cred = credentials.Certificate(Config.FIREBASE_CREDENTIALS)
            firebase_admin.initialize_app(cred)
        _db = firestore.client()
        _initialized = True
        print("Firebase initialized successfully")
        return True
    except Exception as e:
        print(f"Firebase initialization error: {e}")
        return False


def get_db():
    global _db
    if not _initialized:
        init_firebase()
    if _db is None:
        raise RuntimeError("Firebase not initialized. Add serviceAccountKey.json to project root and restart.")
    return _db


def is_ready():
    return _initialized and _db is not None
