from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt 
from passlib.context import CryptContext
from app.config import settings
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

router = APIRouter(prefix="/auth", tags=["Authentication"])
# prefix="/auth" -> all routes here start with /auth
# tags -> group routes in Swagger UI

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# CryptContext handles hashing and verification
# schemas=["bcrypt"] means we use bcrypt algorithm
# deprecated"auto" means old hashes get upgraded automatically.

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain: str, hashed: str) -> bool:
    return pwd_context.verify(plain, hashed)

def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() +timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    # "exp" is a standard JWT claim for expiry.
    # Jose will automatically reject expired tokens
    return jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)


@router.post('/register', response_model=UserResponse, status_code=201)
async def register(user_data: UserCreate):
    # Check uniqueness before insert - better error message than DB exception 
    existing = await User.filter(
        username=user_data.username
    ).exists()
    if existing:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    user = await User.create(
        username=user_data.username,
        email=user_data.email,
        hash_password=hash_password(user_data.password),
    )
    return user 


@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    # OAuth2PasswordRequestForm expects form fields: username + password.
    # This is the OAUth2 spec - client sends form data, not JSON.
    user =  await User.get_or_none(username=form_data.username)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    token = create_access_token({"sub": user.username})
    return {"access_token": token, "token_type": "bearer"}
    