from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user, get_db
from app.schemas.metric import MetricDefinitionResponse, MetricDefinitionCreate, MetricDefinitionUpdate
from app.crud import metric as crud_metric
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)

@router.get("/", response_model=List[MetricDefinitionResponse])
def read_definitions(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """获取所有指标定义"""
    return crud_metric.get_definitions(db, skip=skip, limit=limit)

@router.post("/", response_model=MetricDefinitionResponse)
def create_definition(def_in: MetricDefinitionCreate, db: Session = Depends(get_db)):
    """创建新的指标定义"""
    return crud_metric.create_definition(db, def_in=def_in)

@router.put("/{def_id}", response_model=MetricDefinitionResponse)
def update_definition(def_id: int, def_in: MetricDefinitionUpdate, db: Session = Depends(get_db)):
    """更新指标定义"""
    db_def = crud_metric.update_definition(db, def_id=def_id, def_in=def_in)
    if not db_def:
        raise HTTPException(status_code=404, detail="Definition not found")
    return db_def

@router.delete("/{def_id}")
def delete_definition(def_id: int, db: Session = Depends(get_db)):
    """删除指标定义（将级联删除相关记录）"""
    success = crud_metric.delete_definition(db, def_id=def_id)
    if not success:
        raise HTTPException(status_code=404, detail="Definition not found")
    return {"message": "Successfully deleted"}
