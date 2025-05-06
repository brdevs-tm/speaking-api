from fastapi import APIRouter, HTTPException
from app.services.auth import create_user, authenticate_user
from app.models.schemas import UserCreate, UserLogin
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
async def register(user: UserCreate):
    try:
        user_id = create_user(user)
        return {"message": "User registered successfully", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(form_data: OAuth2PasswordRequestForm):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": user["token"], "token_type": "bearer"}