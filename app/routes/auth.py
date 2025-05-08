from fastapi import APIRouter, HTTPException, Depends
from app.services.auth import authenticate_user, update_admin_credentials
from app.models.schemas import AdminLogin, AdminUpdate
from app.dependencies.auth import get_current_user, require_role

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/admin-login")
async def admin_login(admin: AdminLogin):
    user_data = authenticate_user(admin.username, admin.password)
    if not user_data or user_data["role"] != "admin":
        raise HTTPException(status_code=401, detail="Invalid admin credentials")
    return {"access_token": user_data["token"], "token_type": "bearer"}

@router.put("/admin/update", dependencies=[Depends(require_role("admin"))])
async def update_admin(admin_update: AdminUpdate, current_user: dict = Depends(get_current_user)):
    if current_user["username"] != "iynemlive":  # Faqat asl admin o'zgartirishi mumkin
        raise HTTPException(status_code=403, detail="Only the original admin can update credentials")
    success = update_admin_credentials(admin_update.username, admin_update.password)
    if success:
        return {"message": "Admin credentials updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update credentials")