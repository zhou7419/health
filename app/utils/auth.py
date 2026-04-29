from __future__ import annotations

import base64
import hashlib
import hmac
import json
import os
import time
from typing import Any

from app.config import settings


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("utf-8").rstrip("=")


def _b64url_decode(data: str) -> bytes:
    padded = data + "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(padded.encode("utf-8"))


def _require_secret_key() -> str:
    if not settings.secret_key:
        raise ValueError("未配置 SECRET_KEY")
    return settings.secret_key


def hash_password(password: str, salt: str | None = None) -> str:
    if salt is None:
        salt = _b64url_encode(os.urandom(16))
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return f"pbkdf2_sha256${salt}${_b64url_encode(dk)}"


def verify_password(password: str, hashed: str) -> bool:
    try:
        scheme, salt, digest = hashed.split("$", 2)
    except ValueError:
        return False
    if scheme != "pbkdf2_sha256":
        return False
    dk = hashlib.pbkdf2_hmac(
        "sha256", password.encode("utf-8"), salt.encode("utf-8"), 100_000
    )
    return hmac.compare_digest(_b64url_encode(dk), digest)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    secret = _require_secret_key().encode("utf-8")
    if expires_minutes is None:
        expires_minutes = settings.access_token_expires_minutes

    header = {"alg": "HS256", "typ": "JWT"}
    payload: dict[str, Any] = {
        "sub": subject,
        "exp": int(time.time()) + int(expires_minutes) * 60,
    }

    header_b64 = _b64url_encode(json.dumps(header, separators=(",", ":")).encode("utf-8"))
    payload_b64 = _b64url_encode(json.dumps(payload, separators=(",", ":")).encode("utf-8"))
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    return f"{header_b64}.{payload_b64}.{_b64url_encode(sig)}"


def decode_access_token(token: str) -> dict[str, Any]:
    secret = _require_secret_key().encode("utf-8")
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("token 格式错误")

    header_b64, payload_b64, sig_b64 = parts
    signing_input = f"{header_b64}.{payload_b64}".encode("utf-8")
    expected_sig = hmac.new(secret, signing_input, hashlib.sha256).digest()
    if not hmac.compare_digest(_b64url_encode(expected_sig), sig_b64):
        raise ValueError("token 签名无效")

    payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
    exp = payload.get("exp")
    if not isinstance(exp, int) or exp < int(time.time()):
        raise ValueError("token 已过期")
    return payload
