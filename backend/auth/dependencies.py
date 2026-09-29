from typing import Optional, Dict, Any
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi import Security, HTTPException, status
from .firebase import verify_firebase_token
import logging

logger = logging.getLogger(__name__)

security_scheme = HTTPBearer(auto_error=False)

async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Security(security_scheme)
) -> Dict[str, Any]:
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authorization token provided in Bearer header",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return verify_firebase_token(credentials.credentials)
