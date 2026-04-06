from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from app.config import settings
from app.models.user import User
from app.schemas.user import TokenData


# OAUth2PasswordBearer tells FastAPI:
# "look for a Bearer token in the Authorization header"
# tokenUrl is just for the Swagger UI login button


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """
    Dependency function. FastAPI calls this automatically when a
    route declares 'user: User = Depends(get_current_user)'.

    Why use Depends? Because:
    1. It's reusable - any route can require auth with one line.
    2. It's testable - you can override dependencies in tests.
    3. FastAPI shows it in the OpenAPI docs automatically.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        username = payload.get("sub") # "sub" = subject (standard JWT claim)
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    
    user = await User.get_or_none(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """Chains on top of get_current_user. Only admins pass through."""
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user

