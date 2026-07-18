from typing import AsyncGenerator
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.settings import get_settings, Settings
from app.database.engine import get_db_session
from app.database.models import User
from app.core.security import verify_access_token
from app.core.exceptions import AuthenticationError, NotFoundError

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to provide a database session."""
    async for session in get_db_session():
        yield session


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """Dependency to retrieve the currently authenticated user."""
    # Verify the token
    user_id_str = verify_access_token(token)
    
    # In a real app, this would be a repository call. 
    # For now, we do a simple DB query.
    # Note: Using UUID requires parsing from string.
    from uuid import UUID
    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise AuthenticationError("Invalid user ID in token")

    # Fetch user from DB
    from sqlalchemy import select
    result = await db.execute(select(User).where(User.id == user_id, User.is_active == True))
    user = result.scalar_one_or_none()
    
    if not user:
        raise NotFoundError("User not found or inactive")
        
    return user
