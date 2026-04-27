from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date

from app.api.deps import get_db
from app.schemas.metric import MetricRecordResponse, BatchMetricCreate, MetricRecordUpdate
from app.crud import metric as crud_metric
from app.utils.logger import get_logger

router = APIRouter()
logger = get_logger(__name__)

@router.post("/batch", response_model=List[MetricRecordResponse])
def create_metrics_batch(
    batch_in: BatchMetricCreate,
    db: Session = Depends(get_db)
):
    """
    批量录入同一天的体检指标
    """
    logger.info(f"Creating batch metrics for date {batch_in.record_date}")
    metrics = crud_metric.create_metrics_batch(db=db, batch_in=batch_in)
    return metrics



@router.get("/", response_model=List[MetricRecordResponse])
def read_metrics(
    skip: int = 0,
    limit: int = 100,
    person_id: Optional[int] = None,
    metric_id: Optional[int] = None,
    record_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    获取所有指标记录，支持按人员ID、指标ID或日期过滤
    """
    return crud_metric.get_metrics(db, skip=skip, limit=limit, person_id=person_id, metric_id=metric_id, record_date=record_date)

@router.get("/{metric_id}/history", response_model=List[MetricRecordResponse])
def get_metric_history(
    metric_id: int,
    person_id: int = Query(..., description="必须指定查询哪个人员的历史数据"),
    db: Session = Depends(get_db)
):
    """
    获取某人某一指标所有的历史数据，按时间升序排列，用于生成图表
    """
    history = crud_metric.get_metric_history(db, metric_id=metric_id, person_id=person_id)
    if not history:
        raise HTTPException(status_code=404, detail=f"Metric {metric_id} history for person {person_id} not found")
    return history

@router.put("/{metric_id}", response_model=MetricRecordResponse)
def update_metric(
    metric_id: int,
    metric_in: MetricRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新单条体检指标
    """
    metric = crud_metric.update_metric(db, metric_id=metric_id, metric_in=metric_in)
    if not metric:
        raise HTTPException(status_code=404, detail="Metric record not found")
    return metric

@router.delete("/{metric_id}")
def delete_metric(
    metric_id: int,
    db: Session = Depends(get_db)
):
    """
    删除单条体检指标
    """
    success = crud_metric.delete_metric(db, metric_id=metric_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metric record not found")
    return {"message": "Successfully deleted"}
