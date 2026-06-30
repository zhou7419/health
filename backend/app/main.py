from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
import os
import time

from app.config import settings
from app.api.v1 import api_router
from app.database import Base, engine, SessionLocal

# 创建数据库表
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.app_name,
    debug=settings.debug,
)

_start_time = time.time()


@app.get("/health", include_in_schema=False)
def health_check():
    """健康检查接口（不包含在 API 文档中）"""
    db_ok = False
    try:
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        db_ok = True
    except Exception:
        pass
    return JSONResponse(
        content={
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected",
            "uptime": int(time.time() - _start_time),
        },
        status_code=200 if db_ok else 503,
    )

# 配置 CORS 允许跨域请求（针对前端开发服务器等）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 生产环境中建议替换为实际前端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")
