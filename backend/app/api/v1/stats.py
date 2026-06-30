from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import date, timedelta
import os
import shutil
import tempfile

from app.api.deps import get_current_user, get_db
from app.config import settings
from app.models.metric import MetricRecord, Person, MetricDefinition
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)


def _get_db_path() -> str:
    """从数据库 URL 解析出数据库文件路径"""
    url = settings.database_url
    # sqlite:///path  ->  /path
    path = url.replace("sqlite:///", "", 1)
    # Docker 中是绝对路径 /app/database/app.db，本地是相对路径
    if not os.path.isabs(path):
        # 从当前文件位置推算 backend 根目录
        base = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        path = os.path.join(base, path)
    return path


@router.get("/stats")
def get_stats(db: Session = Depends(get_db)):
    """获取仪表盘统计数据"""
    total_persons = db.query(func.count(Person.id)).scalar()
    total_definitions = db.query(func.count(MetricDefinition.id)).scalar()
    total_records = db.query(func.count(MetricRecord.id)).scalar()

    # 最近7天新增记录数
    week_ago = date.today() - timedelta(days=7)
    recent_records = db.query(func.count(MetricRecord.id)).filter(
        MetricRecord.record_date >= week_ago
    ).scalar()

    # 各人员记录数排行
    person_rank = (
        db.query(Person.name, func.count(MetricRecord.id).label("cnt"))
        .join(MetricRecord, Person.id == MetricRecord.person_id)
        .group_by(Person.id)
        .order_by(func.count(MetricRecord.id).desc())
        .limit(5)
        .all()
    )

    return {
        "total_persons": total_persons,
        "total_definitions": total_definitions,
        "total_records": total_records,
        "recent_7d_records": recent_records,
        "person_rank": [{"name": r[0], "count": r[1]} for r in person_rank],
    }


@router.get("/backup")
def backup_database():
    """下载数据库备份文件"""
    db_path = _get_db_path()
    if not os.path.exists(db_path):
        raise HTTPException(status_code=404, detail="Database file not found")
    logger.info(f"Creating backup: {db_path}")
    return FileResponse(
        db_path,
        media_type="application/octet-stream",
        filename=f"health-backup-{date.today().isoformat()}.db",
    )


@router.post("/restore")
async def restore_database(file: UploadFile = File(...)):
    """上传数据库文件进行恢复"""
    db_path = _get_db_path()
    if not file.filename.endswith(".db"):
        raise HTTPException(status_code=400, detail="Only .db files are supported")

    try:
        content = await file.read()
        # 先备份当前数据库
        if os.path.exists(db_path):
            backup_path = db_path + ".bak"
            shutil.copy2(db_path, backup_path)
            logger.info(f"Current database backed up to {backup_path}")

        # 写入新数据库文件
        with open(db_path, "wb") as f:
            f.write(content)
        logger.info(f"Database restored from upload: {file.filename}")
        return {"message": "Database restored successfully"}
    except Exception as e:
        logger.error(f"Restore failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Restore failed: {str(e)}")
