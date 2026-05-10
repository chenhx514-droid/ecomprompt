from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from database import get_connection
from models import UserRegister, UserLogin, TokenResponse, UserResponse
from auth_utils import hash_password, verify_password, create_access_token, decode_access_token

router = APIRouter(prefix="/auth", tags=["auth"])
security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> dict:
    if credentials is None:
        raise HTTPException(status_code=401, detail="Not authenticated")
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return {"user_id": int(payload["sub"]), "email": payload["email"]}


def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[dict]:
    if credentials is None:
        return None
    payload = decode_access_token(credentials.credentials)
    if payload is None:
        return None
    return {"user_id": int(payload["sub"]), "email": payload["email"]}


@router.post("/register", response_model=TokenResponse)
def register(body: UserRegister):
    if not body.email or "@" not in body.email or "." not in body.email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email address")
    if len(body.password) < 6:
        raise HTTPException(status_code=400, detail="Password must be at least 6 characters")
    conn = get_connection()
    existing = conn.execute("SELECT id FROM users WHERE email = ?", (body.email,)).fetchone()
    if existing:
        conn.close()
        raise HTTPException(status_code=409, detail="Email already registered")
    pw_hash = hash_password(body.password)
    cursor = conn.execute(
        "INSERT INTO users (email, hashed_password) VALUES (?, ?)",
        (body.email, pw_hash)
    )
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    token = create_access_token(user_id, body.email)
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=user_id, email=body.email)
    )


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin):
    conn = get_connection()
    row = conn.execute("SELECT * FROM users WHERE email = ?", (body.email,)).fetchone()
    conn.close()
    if not row or not verify_password(body.password, row["hashed_password"]):
        raise HTTPException(status_code=401, detail="Invalid email or password")
    token = create_access_token(row["id"], row["email"])
    return TokenResponse(
        access_token=token,
        user=UserResponse(id=row["id"], email=row["email"], created_at=row["created_at"])
    )


@router.get("/me", response_model=UserResponse)
def get_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(id=current_user["user_id"], email=current_user["email"])
