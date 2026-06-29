from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.api.deps import get_current_user, get_db
from app.schemas.metric import PersonResponse, PersonCreate, PersonPageResponse
from app.crud import metric as crud_metric
from app.utils.logger import get_logger

router = APIRouter(dependencies=[Depends(get_current_user)])
logger = get_logger(__name__)

@router.get("/", response_model=PersonPageResponse)
def read_persons(
    page: int = Query(1, ge=1, description="页码"),
    page_size: int = Query(20, ge=1, le=100, description="每页条数"),
    db: Session = Depends(get_db)
):
    """获取所有人员列表，支持分页"""
    skip = (page - 1) * page_size
    items = crud_metric.get_persons(db, skip=skip, limit=page_size)
    total = crud_metric.count_persons(db)
    return PersonPageResponse(items=items, total=total, page=page, page_size=page_size)

@router.post("/", response_model=PersonResponse)
def create_person(person_in: PersonCreate, db: Session = Depends(get_db)):
    """新增人员"""
    return crud_metric.create_person(db, person_in=person_in)

@router.delete("/{person_id}")
def delete_person(person_id: int, db: Session = Depends(get_db)):
    """删除人员及该人员的所有体检记录"""
    success = crud_metric.delete_person(db, person_id=person_id)
    if not success:
        raise HTTPException(status_code=404, detail="Person not found")
    return {"message": "Successfully deleted"}
