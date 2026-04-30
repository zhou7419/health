from typing import Generator

from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database import SessionLocal
from app.config import settings
from app.utils.auth import decode_access_token

def get_db() -> Generator:
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


bearer_scheme = HTTPBearer(auto_error=False)


def get_client_ip(request: Request) -> str:
    xff = request.headers.get("x-forwarded-for")
    if xff:
        first = xff.split(",")[0].strip()
        if first:
            return first
    xrip = request.headers.get("x-real-ip")
    if xrip:
        return xrip.strip()
    if request.client and request.client.host:
        return request.client.host
    return "unknown"


def get_current_user(
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
    if not settings.admin_password:
        raise HTTPException(status_code=500, detail="未配置 ADMIN_PASSWORD")
    if not settings.secret_key:
        raise HTTPException(status_code=500, detail="未配置 SECRET_KEY")

    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="未登录")

    token = credentials.credentials
    try:
        payload = decode_access_token(token)
    except Exception:
        raise HTTPException(status_code=401, detail="登录已失效")

    sub = payload.get("sub")
    if sub != settings.admin_username:
        raise HTTPException(status_code=401, detail="登录已失效")

    return str(sub)
