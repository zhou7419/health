from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
import csv
import io

from app.api.deps import get_current_user, get_db
from app.schemas.metric import MetricRecordResponse, MetricRecordPageResponse, BatchMetricCreate, MetricRecordUpdate, MetricItemCreate
from app.crud import metric as crud_metric
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
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

@router.post("/batch/upload", response_model=List[MetricRecordResponse])
async def upload_metrics_batch(
    person_id: int = Form(...),
    record_date: date = Form(...),
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    通过上传CSV文件批量录入指标
    """
    if not file.filename.endswith('.csv'):
        raise HTTPException(status_code=400, detail="Only CSV files are supported")
    
    try:
        content = await file.read()
        # Decode CSV content
        decoded_content = content.decode('utf-8-sig')
        reader = csv.DictReader(io.StringIO(decoded_content))
        
        items = []
        for row in reader:
            # Skip empty rows or rows without name and value
            if not row.get('指标名称') or not row.get('数值'):
                continue
                
            try:
                value = float(row.get('数值'))
            except ValueError:
                continue # Skip invalid numbers
                
            expected_min = row.get('参考下限')
            expected_max = row.get('参考上限')
            
            item = MetricItemCreate(
                name=row.get('指标名称').strip(),
                value=value,
                unit=row.get('单位', '').strip() or None,
                expected_min=float(expected_min) if expected_min else None,
                expected_max=float(expected_max) if expected_max else None,
                notes=row.get('备注', '').strip() or None
            )
            items.append(item)
            
        if not items:
            raise HTTPException(status_code=400, detail="No valid metric data found in the CSV file")
            
        batch_in = BatchMetricCreate(
            person_id=person_id,
            record_date=record_date,
            metrics=items
        )
        
        logger.info(f"Creating batch metrics from upload for date {record_date}, {len(items)} items")
        metrics = crud_metric.create_metrics_batch(db=db, batch_in=batch_in)
        return metrics
        
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File encoding must be UTF-8")
    except Exception as e:
        logger.error(f"Error processing uploaded file: {str(e)}")
        raise HTTPException(status_code=400, detail=f"Failed to process file: {str(e)}")



@router.get("/", response_model=MetricRecordPageResponse)
def read_metrics(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    person_id: Optional[int] = None,
    metric_id: Optional[int] = None,
    record_date: Optional[date] = None,
    db: Session = Depends(get_db)
):
    """
    获取体检指标记录，支持分页和按人员ID、指标ID或日期过滤
    """
    skip = (page - 1) * page_size
    items = crud_metric.get_metrics(db, skip=skip, limit=page_size, person_id=person_id, metric_id=metric_id, record_date=record_date)
    total = crud_metric.count_metrics(db, person_id=person_id, metric_id=metric_id, record_date=record_date)
    return MetricRecordPageResponse(items=items, total=total, page=page, page_size=page_size)

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

@router.put("/{record_id}", response_model=MetricRecordResponse)
def update_metric(
    record_id: int,
    record_in: MetricRecordUpdate,
    db: Session = Depends(get_db)
):
    """
    更新单条体检指标
    """
    record = crud_metric.update_metric(db, record_id=record_id, record_in=record_in)
    if not record:
        raise HTTPException(status_code=404, detail="Metric record not found")
    return record

@router.delete("/{record_id}")
def delete_metric(
    record_id: int,
    db: Session = Depends(get_db)
):
    """
    删除单条体检指标
    """
    success = crud_metric.delete_metric(db, record_id=record_id)
    if not success:
        raise HTTPException(status_code=404, detail="Metric record not found")
    return {"message": "Successfully deleted"}

@router.delete("/date/{record_date}")
def delete_metrics_by_date(
    record_date: date,
    person_id: Optional[int] = Query(None, description="可选：如果指定了人员ID，则只删除该人员在这一天的体检数据"),
    db: Session = Depends(get_db)
):
    """
    删除指定日期的所有体检数据
    """
    deleted_count = crud_metric.delete_metrics_by_date(db, record_date=record_date, person_id=person_id)
    return {"message": f"Successfully deleted {deleted_count} records", "deleted_count": deleted_count}
