from fastapi import APIRouter, HTTPException
from app.services.auth import create_user, authenticate_user
from app.models.schemas import UserCreate, UserLogin

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register")
async def register(user: UserCreate):
    try:
        user_id = create_user(user)
        return {"message": "User registered successfully", "user_id": user_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
async def login(user: UserLogin):
    user_data = authenticate_user(user.email, user.password)
    if not user_data:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"access_token": user_data["token"], "token_type": "bearer"}