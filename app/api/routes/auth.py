from fastapi import APIRouter, Depends, HTTPException, status, Response
from app.schemas.auth import RegisterRequest, LoginRequest
from app.db.session import get_async_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.user import User
from app.core.security import get_password_hash, verify_password
from app.core.jwt import create_access_token
from app.api.deps import get_current_user


router = APIRouter()


@router.post("/register")
async def register(
    data: RegisterRequest, response: Response, db: AsyncSession = Depends(get_async_db)
):

    # check if user already exists
    result = await db.execute(select(User).where(User.email == data.email))
    existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # create a user
    user = User(
        name=data.name,
        email=data.email,
        hashed_password=get_password_hash(data.password),
        is_active=True,
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)

    access_token = create_access_token(data={"sub": str(user.id), "name": str(user.name)})

    return {
        "message": "User registered successfully",
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.post("/login")
async def user_login(
    data: LoginRequest, response: Response, db: AsyncSession = Depends(get_async_db)
):
    result = await db.execute(select(User).where(User.email == data.email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    if not verify_password(data.password, str(user.hashed_password)):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid password",
        )

    access_token = create_access_token(data={"sub": str(user.id), "name": str(user.name)})

    return {
        "message": "Login successful",
        "email": user.email,
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/me")
async def get_current_user(current_user: User = Depends(get_current_user)):
    return {
        "id": current_user.id,
        "name": current_user.name,
        "email": current_user.email,
        "created_at": current_user.created_at,
    }
