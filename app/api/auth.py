from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import async_session_maker
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin, TokenResponse
from app.core.security import hash_password, verify_password, create_access_token

router = APIRouter(prefix="/auth", tags=["Auth"])

# регистрация
@router.post("/register", status_code=201)
async def register(user_data: UserCreate):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == user_data.email))
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="User already exists")

        new_user = User(
            email=user_data.email,
            hashed_password=hash_password(user_data.password),
            full_name=user_data.full_name
        )
        session.add(new_user)
        await session.commit()
        return {"message": "User created successfully"}

# вход
@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin):
    async with async_session_maker() as session:
        result = await session.execute(select(User).where(User.email == user_data.email))
        user = result.scalar_one_or_none()

        if not user or not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        token = create_access_token({"sub": user.email})
        return TokenResponse(access_token=token)
