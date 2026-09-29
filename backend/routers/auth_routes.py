import logging
from typing import Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Request, Header, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from auth import verify_firebase_token, get_current_user
from database import get_db, get_profile_by_firebase_uid, create_or_update_profile
import os
import firebase_admin
from firebase_admin import auth as firebase_admin_auth

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/auth", tags=["Auth & Profiles"])

class VerifyTokenRequest(BaseModel):
    token: Optional[str] = None

class SyncUserRequest(BaseModel):
    uid: Optional[str] = None
    email: Optional[str] = None
    displayName: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None

class UpdateProfileRequest(BaseModel):
    displayName: Optional[str] = None
    full_name: Optional[str] = None
    role: Optional[str] = None
    language: Optional[str] = None
    timezone: Optional[str] = None

def format_profile(profile: Any) -> Dict[str, Any]:
    if isinstance(profile, dict):
        if "displayName" not in profile and "full_name" in profile:
            profile["displayName"] = profile["full_name"]
        return profile
    elif hasattr(profile, "to_dict"):
        return profile.to_dict()
    return dict(profile)

@router.post("/verify")
async def verify_token(
    request: Request,
    body: Optional[VerifyTokenRequest] = None,
    authorization: Optional[str] = Header(None),
    db: Session = Depends(get_db)
):
    """
    POST /api/auth/verify
    Verifies Firebase ID Token using Firebase Admin SDK.
    Stores/syncs profile in Supabase profiles table.
    """
    token = None
    if body and body.token:
        token = body.token
    elif authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No authentication token provided"
        )

    decoded_token = verify_firebase_token(token)
    uid = decoded_token.get("uid")
    email = decoded_token.get("email", "")
    name = decoded_token.get("name") or (email.split("@")[0] if email else "User")

    profile = create_or_update_profile(
        db=db,
        firebase_uid=uid,
        email=email,
        full_name=name,
        role="user"
    )

    return {
        "success": True,
        "message": "Token verified successfully",
        "user": format_profile(profile),
        "uid": uid
    }

@router.post("/sync-user")
async def sync_user(
    body: SyncUserRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /api/auth/sync-user
    Syncs user profile details into Supabase.
    """
    target_uid = body.uid or current_user.get("uid")

    if current_user.get("uid") != target_uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Forbidden: Cannot update another user's profile"
        )

    email = body.email or current_user.get("email", "")
    name = body.full_name or body.displayName or current_user.get("name", "User")
    role = body.role or "user"

    profile = create_or_update_profile(
        db=db,
        firebase_uid=target_uid,
        email=email,
        full_name=name,
        role=role
    )

    return {
        "success": True,
        "user": format_profile(profile)
    }

@router.get("/me")
async def get_my_profile(
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /api/auth/me
    Retrieves current user profile from Supabase profiles table.
    """
    uid = current_user.get("uid")
    profile = get_profile_by_firebase_uid(db, uid)

    if not profile:
        email = current_user.get("email", "")
        name = current_user.get("name") or (email.split("@")[0] if email else "User")
        profile = create_or_update_profile(
            db=db,
            firebase_uid=uid,
            email=email,
            full_name=name,
            role="user"
        )

    return {
        "success": True,
        "user": format_profile(profile)
    }

@router.put("/profile")
@router.post("/profile")
async def update_profile(
    body: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT/POST /api/auth/profile
    Updates profile details in Supabase profiles table.
    """
    uid = current_user.get("uid")
    name = body.full_name or body.displayName or ""
    role = body.role or "user"

    profile = create_or_update_profile(
        db=db,
        firebase_uid=uid,
        email=current_user.get("email", ""),
        full_name=name,
        role=role
    )

    return {
        "success": True,
        "message": "Profile updated successfully",
        "user": format_profile(profile)
    }


class DevCreateUserRequest(BaseModel):
    email: Optional[str] = None
    password: Optional[str] = None
    displayName: Optional[str] = None


@router.post("/dev/create-user")
async def dev_create_user(
    body: DevCreateUserRequest,
):
    """
    DEV ONLY: Creates a Firebase user using the Admin SDK and syncs to Supabase.
    This endpoint is gated by the environment variable `ENABLE_DEV_USER_CREATION`.
    It should NOT be enabled in production.
    """
    if os.getenv("ENABLE_DEV_USER_CREATION", "false").lower() not in ("1", "true", "yes"):
        raise HTTPException(status_code=403, detail="Dev user creation disabled")

    if not body.email or not body.password:
        raise HTTPException(status_code=400, detail="email and password required")

    # Create Firebase user
    try:
        user_record = firebase_admin_auth.create_user(
            email=body.email,
            password=body.password,
            display_name=body.displayName,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Firebase create user failed: {e}")

    # Sync to Supabase via ORM / helper
    profile = create_or_update_profile(
        db=get_db().__next__(),
        firebase_uid=user_record.uid,
        email=user_record.email or "",
        full_name=user_record.display_name or "",
        role="dev",
    )

    return {"success": True, "user": format_profile(profile)}
