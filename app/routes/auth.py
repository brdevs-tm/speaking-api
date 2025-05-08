from fastapi import APIRouter, HTTPException, Depends
from app.services.auth import authenticate_user, update_admin_credentials, get_current_admin_credentials
from app.models.schemas import AdminLogin, AdminUpdate
from app.dependencies.auth import get_current_user, require_role
from app.services.telegram_bot import send_telegram_notification

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
    
    # Get current credentials before update
    current_credentials = get_current_admin_credentials()
    success = update_admin_credentials(admin_update.username, admin_update.password)
    if success:
        # Send Telegram notification with old and new credentials
        message = (
            "Admin Credentials Updated:\n"
            f"Old Username: {current_credentials['username']}\n"
            f"Old Password: [Hidden for security]\n"
            f"New Username: {admin_update.username}\n"
            f"New Password: [Hidden for security]"
        )
        await send_telegram_notification(message)
        return {"message": "Admin credentials updated successfully"}
    raise HTTPException(status_code=400, detail="Failed to update credentials")