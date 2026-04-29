from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_client_ip, get_current_user, get_db
from app.config import settings
from app.models.auth import LoginAttempt
from app.schemas.auth import LoginRequest, MeResponse, TokenResponse
from app.utils.auth import create_access_token
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.post("/login", response_model=TokenResponse)
def login(request: Request, body: LoginRequest, db: Session = Depends(get_db)):
    if not settings.secret_key:
        raise HTTPException(status_code=500, detail="未配置 SECRET_KEY")
    if not settings.admin_password:
        raise HTTPException(status_code=500, detail="未配置 ADMIN_PASSWORD")

    ip = get_client_ip(request)
    now = datetime.utcnow()

    attempt = db.query(LoginAttempt).filter(LoginAttempt.ip == ip).first()
    if attempt and attempt.locked_until and attempt.locked_until > now:
        raise HTTPException(status_code=429, detail="该 IP 登录失败次数过多，已被临时封禁")

    if body.username != settings.admin_username or body.password != settings.admin_password:
        if attempt is None:
            attempt = LoginAttempt(ip=ip, fail_count=0, locked_until=None)
            db.add(attempt)

        attempt.fail_count = int(attempt.fail_count or 0) + 1
        if attempt.fail_count >= settings.login_lock_max_failures:
            attempt.locked_until = now + timedelta(minutes=settings.login_lock_minutes)
        db.commit()
        raise HTTPException(status_code=401, detail="用户名或密码错误")

    if attempt is None:
        attempt = LoginAttempt(ip=ip, fail_count=0, locked_until=None)
        db.add(attempt)

    attempt.fail_count = 0
    attempt.locked_until = None
    db.commit()

    token = create_access_token(subject=settings.admin_username)
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=settings.access_token_expires_minutes * 60,
    )


@router.get("/me", response_model=MeResponse)
def me(username: str = Depends(get_current_user)):
    return MeResponse(username=username)
