import json
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.config import settings
from app.db.session import get_db
from app.models.entities import User

bearer = HTTPBearer(auto_error=False)

def _firebase_app():
    try:
        return firebase_admin.get_app()
    except ValueError:
        if not settings.firebase_project_id:
            raise HTTPException(status_code=503, detail="Firebase authentication is not configured")
        options = {"projectId": settings.firebase_project_id}
        if settings.firebase_service_account_json:
            credential = credentials.Certificate(json.loads(settings.firebase_service_account_json))
        elif settings.firebase_service_account_path:
            credential = credentials.Certificate(settings.firebase_service_account_path)
        else:
            credential = credentials.ApplicationDefault()
        return firebase_admin.initialize_app(credential, options)

def get_current_user(creds: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)):
    if not creds:
        raise HTTPException(status_code=401, detail="Authentication required")

    if settings.auth_provider.lower() != "firebase":
        raise HTTPException(status_code=503, detail="Only Firebase authentication is enabled")

    try:
        claims = firebase_auth.verify_id_token(creds.credentials, app=_firebase_app(), check_revoked=True)
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid or expired Firebase token")

    uid = claims.get("uid")
    user = db.query(User).filter_by(firebase_uid=uid).first()
    if user:
        return user

    email = (claims.get("email") or "").lower()
    if not email:
        raise HTTPException(status_code=400, detail="Firebase account must have an email")

    user = db.query(User).filter_by(email=email).first()
    if user:
        if user.role != "writer":
            raise HTTPException(status_code=409, detail="This email is already linked to another role. Ask an administrator to confirm the Firebase mapping.")
        user.firebase_uid = uid
    else:
        user = User(firebase_uid=uid, email=email, name=claims.get("name") or email.split("@")[0], role="writer")
        db.add(user)

    db.commit()
    db.refresh(user)
    return user

def require_roles(*roles):
    def dep(user=Depends(get_current_user)):
        if user.role not in roles: raise HTTPException(status_code=403, detail="Insufficient permissions")
        return user
    return dep
