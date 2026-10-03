from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.entities import User
from app.auth.security import get_current_user, require_roles
router = APIRouter(prefix="/auth", tags=["auth"])
class ProfileUpdate(BaseModel):
    displayName: str | None = None
    full_name: str | None = None
    language: str | None = None
    timezone: str | None = None
    role: str | None = None

class RoleUpdate(BaseModel):
    role: str

@router.post("/verify")
def verify_firebase(user=Depends(get_current_user)):
    return {"success": True, "user": {"uid": user.firebase_uid, "id": user.id, "email": user.email, "displayName": user.name, "full_name": user.name, "role": user.role}}

@router.post("/sync-user")
def sync_firebase_user(user=Depends(get_current_user)):
    return {"success": True, "user": {"uid": user.firebase_uid, "id": user.id, "email": user.email, "displayName": user.name, "full_name": user.name, "role": user.role}}

@router.put("/profile")
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    if body.displayName or body.full_name:
        user.name = (body.displayName or body.full_name).strip()
    # Roles are never accepted from the client; admins use PUT /users/{id}/role.
    db.commit()
    db.refresh(user)
    return {"success": True, "user": {"uid": user.firebase_uid, "id": user.id, "email": user.email, "displayName": user.name, "full_name": user.name, "role": user.role}}

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, body: RoleUpdate, db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    if body.role not in {"writer", "reviewer", "approver", "admin"}:
        raise HTTPException(400, "Invalid role")
    target = db.get(User, user_id)
    if not target:
        raise HTTPException(404, "User not found")
    target.role = body.role
    db.commit()
    return {"success": True, "user": {"id": target.id, "email": target.email, "name": target.name, "role": target.role}}

@router.get("/users")
def list_users(db: Session = Depends(get_db), admin=Depends(require_roles("admin"))):
    return [{"id": row.id, "email": row.email, "name": row.name, "role": row.role} for row in db.query(User).order_by(User.email).all()]

@router.get("/me")
def me(user=Depends(get_current_user)):
    return {"id": user.id, "email": user.email, "name": user.name, "role": user.role}
