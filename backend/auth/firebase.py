import os
import logging
from typing import Any, Dict
import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from fastapi import HTTPException, status
from config import settings

logger = logging.getLogger(__name__)


def init_firebase_admin():
    if not firebase_admin._apps:
        service_account_path = settings.FIREBASE_SERVICE_ACCOUNT_PATH
        if os.path.exists(service_account_path):
            try:
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info(f"Firebase Admin initialized from {service_account_path}")
            except Exception as e:
                logger.error(f"Failed to initialize Firebase Admin with service account: {e}")
                try:
                    firebase_admin.initialize_app()
                except Exception:
                    pass
        else:
            logger.warning(f"Service account key not found at {service_account_path}. Initializing default app.")
            try:
                firebase_admin.initialize_app()
            except Exception as e:
                logger.error(f"Firebase Admin fallback initialization error: {e}")


def verify_firebase_token(token: str) -> Dict[str, Any]:
    try:
        decoded = firebase_auth.verify_id_token(token)
        return decoded
    except Exception as e:
        logger.error(f"Firebase token verification failed: {e}")
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))


# initialize on import
init_firebase_admin()
