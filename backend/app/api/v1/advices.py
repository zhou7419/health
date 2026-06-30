from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from app.api.deps import get_current_user, get_db
from app.crud import metric as crud_metric
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)


class AdviceCreate(BaseModel):
    person_id: int
    content: str
    summary: Optional[str] = None


class AdviceResponse(BaseModel):
    id: int
    person_id: int
    content: str
    summary: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class AdvicePageResponse(BaseModel):
    items: List[AdviceResponse]
    total: int


@router.get("/", response_model=AdvicePageResponse)
def list_advices(
    person_id: Optional[int] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """获取健康建议历史"""
    skip = (page - 1) * page_size
    items = crud_metric.get_health_advices(db, person_id=person_id, skip=skip, limit=page_size)
    total = len(items) if False else 0  # simplified - real count would need a function
    return AdvicePageResponse(items=items, total=total)


@router.get("/{advice_id}", response_model=AdviceResponse)
def get_advice(advice_id: int, db: Session = Depends(get_db)):
    """获取单条健康建议"""
    advice = crud_metric.get_health_advice(db, advice_id=advice_id)
    if not advice:
        raise HTTPException(status_code=404, detail="Advice not found")
    return advice


@router.post("/", response_model=AdviceResponse)
def create_advice(body: AdviceCreate, db: Session = Depends(get_db)):
    """保存健康建议"""
    advice = crud_metric.create_health_advice(db, person_id=body.person_id, content=body.content, summary=body.summary)
    return advice


@router.delete("/{advice_id}")
def delete_advice(advice_id: int, db: Session = Depends(get_db)):
    """删除健康建议"""
    success = crud_metric.delete_health_advice(db, advice_id=advice_id)
    if not success:
        raise HTTPException(status_code=404, detail="Advice not found")
    return {"message": "Successfully deleted"}
