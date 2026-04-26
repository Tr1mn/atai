from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..schemas.auth import RegisterRequest, LoginRequest, TokenResponse, UserMeResponse
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..core.rate_limit import limiter
from ..config import settings

router = APIRouter(prefix="/api/auth", tags=["auth"])

_COOKIE_MAX_AGE = settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60


def _set_auth_cookie(response: Response, token: str) -> None:
    response.set_cookie(
        key="access_token",
        value=token,
        httponly=True,
        samesite=settings.COOKIE_SAMESITE,
        secure=settings.COOKIE_SECURE,
        max_age=_COOKIE_MAX_AGE,
    )


@router.post("/register", response_model=TokenResponse, status_code=201)
@limiter.limit("5/minute")
def register(request: Request, req: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == req.email).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    if req.age < 18:
        raise HTTPException(status_code=400, detail="Must be 18 or older to register independently")
    user = User(
        email=req.email,
        password_hash=hash_password(req.password),
        full_name=req.full_name,
        age=req.age,
        city=req.city,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token({"sub": str(user.id)})
    _set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user_id=user.id, role=user.role, full_name=user.full_name)


@router.post("/login", response_model=TokenResponse)
@limiter.limit("5/minute")
def login(request: Request, req: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == req.email).first()
    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    if user.status == "blocked":
        raise HTTPException(status_code=403, detail="Account is blocked")
    token = create_access_token({"sub": str(user.id)})
    _set_auth_cookie(response, token)
    return TokenResponse(access_token=token, user_id=user.id, role=user.role, full_name=user.full_name)


@router.get("/me", response_model=UserMeResponse)
def get_me_session(current_user=Depends(get_current_user)):
    """Restore session from HTTP-only cookie. Used by frontend on page load."""
    return UserMeResponse(
        user_id=current_user.id,
        role=current_user.role,
        full_name=current_user.full_name,
    )


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(
        "access_token",
        secure=settings.COOKIE_SECURE,
        samesite=settings.COOKIE_SAMESITE,
    )
    return {"message": "Logged out"}
