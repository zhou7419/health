from sqlalchemy.orm import Session, joinedload
from sqlalchemy import asc, func
from typing import List, Optional
from datetime import date
from app.models.metric import MetricRecord, MetricDefinition, Person
from app.schemas.metric import (
    MetricRecordCreate,
    BatchMetricCreate,
    MetricRecordUpdate,
    MetricDefinitionCreate,
    MetricDefinitionUpdate,
    PersonCreate
)

# --- Persons ---
def get_persons(db: Session, skip: int = 0, limit: int = 100) -> List[Person]:
    return db.query(Person).offset(skip).limit(limit).all()

def count_persons(db: Session) -> int:
    return db.query(func.count(Person.id)).scalar()

def create_person(db: Session, person_in: PersonCreate) -> Person:
    db_person = Person(name=person_in.name, gender=person_in.gender)
    db.add(db_person)
    db.commit()
    db.refresh(db_person)
    return db_person

def delete_person(db: Session, person_id: int) -> bool:
    db_person = db.query(Person).filter(Person.id == person_id).first()
    if not db_person:
        return False
    
    db.delete(db_person)
    db.commit()
    return True

# --- Metric Definitions ---
def get_definitions(db: Session, skip: int = 0, limit: int = 100, name: Optional[str] = None) -> List[MetricDefinition]:
    query = db.query(MetricDefinition)
    if name:
        query = query.filter(MetricDefinition.name.like(f"%{name}%"))
    return query.order_by(MetricDefinition.id.asc()).offset(skip).limit(limit).all()

def count_definitions(db: Session, name: Optional[str] = None) -> int:
    query = db.query(func.count(MetricDefinition.id))
    if name:
        query = query.filter(MetricDefinition.name.like(f"%{name}%"))
    return query.scalar()

def create_definition(db: Session, def_in: MetricDefinitionCreate) -> MetricDefinition:
    db_def = MetricDefinition(**def_in.model_dump())
    db.add(db_def)
    db.commit()
    db.refresh(db_def)
    return db_def

def update_definition(db: Session, def_id: int, def_in: MetricDefinitionUpdate) -> Optional[MetricDefinition]:
    db_def = db.query(MetricDefinition).filter(MetricDefinition.id == def_id).first()
    if not db_def:
        return None
    
    update_data = def_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_def, field, value)
        
    db.commit()
    db.refresh(db_def)
    return db_def

def delete_definition(db: Session, def_id: int) -> bool:
    db_def = db.query(MetricDefinition).filter(MetricDefinition.id == def_id).first()
    if not db_def:
        return False
    
    db.delete(db_def)
    db.commit()
    return True

# --- Metric Records ---
def create_metrics_batch(db: Session, batch_in: BatchMetricCreate) -> List[MetricRecord]:
    db_metrics = []
    
    for item in batch_in.metrics:
        metric_id = item.metric_id
        
        # If no metric_id is provided, try to find by name or create a new definition
        if not metric_id and item.name:
            db_def = db.query(MetricDefinition).filter(MetricDefinition.name == item.name).first()
            if not db_def:
                db_def = MetricDefinition(
                    name=item.name, 
                    unit=item.unit,
                    expected_min=item.expected_min,
                    expected_max=item.expected_max
                )
                db.add(db_def)
                db.commit()
                db.refresh(db_def)
            metric_id = db_def.id
            
        if metric_id:
                db_metric = MetricRecord(
                    person_id=batch_in.person_id,
                    metric_id=metric_id,
                    value=item.value,
                    notes=item.notes,
                    record_date=batch_in.record_date
                )
                db_metrics.append(db_metric)
    
    if db_metrics:
        db.add_all(db_metrics)
        db.commit()
        for metric in db_metrics:
            db.refresh(metric)
    return db_metrics

def get_metrics(
    db: Session, skip: int = 0, limit: int = 100, metric_id: Optional[int] = None, record_date: Optional[date] = None, person_id: Optional[int] = None
) -> List[MetricRecord]:
    query = db.query(MetricRecord).options(joinedload(MetricRecord.metric), joinedload(MetricRecord.person))
    if person_id is not None:
        query = query.filter(MetricRecord.person_id == person_id)
    if metric_id is not None:
        query = query.filter(MetricRecord.metric_id == metric_id)
    if record_date:
        query = query.filter(MetricRecord.record_date == record_date)
    return query.order_by(MetricRecord.record_date.desc()).offset(skip).limit(limit).all()

def count_metrics(
    db: Session, metric_id: Optional[int] = None, record_date: Optional[date] = None, person_id: Optional[int] = None
) -> int:
    query = db.query(func.count(MetricRecord.id))
    if person_id is not None:
        query = query.filter(MetricRecord.person_id == person_id)
    if metric_id is not None:
        query = query.filter(MetricRecord.metric_id == metric_id)
    if record_date:
        query = query.filter(MetricRecord.record_date == record_date)
    return query.scalar()

def get_metric_history(db: Session, metric_id: int, person_id: int) -> List[MetricRecord]:
    return db.query(MetricRecord)\
        .options(joinedload(MetricRecord.metric), joinedload(MetricRecord.person))\
        .filter(MetricRecord.metric_id == metric_id, MetricRecord.person_id == person_id)\
        .order_by(asc(MetricRecord.record_date))\
        .all()

def update_metric(db: Session, record_id: int, record_in: MetricRecordUpdate) -> Optional[MetricRecord]:
    db_record = db.query(MetricRecord).filter(MetricRecord.id == record_id).first()
    if not db_record:
        return None
    
    update_data = record_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_record, field, value)
        
    db.commit()
    db.refresh(db_record)
    return db_record

def delete_metric(db: Session, record_id: int) -> bool:
    db_record = db.query(MetricRecord).filter(MetricRecord.id == record_id).first()
    if not db_record:
        return False
    
    db.delete(db_record)
    db.commit()
    return True

def delete_metrics_by_date(db: Session, record_date: date, person_id: Optional[int] = None) -> int:
    query = db.query(MetricRecord).filter(MetricRecord.record_date == record_date)
    if person_id is not None:
        query = query.filter(MetricRecord.person_id == person_id)
    
    deleted_count = query.delete(synchronize_session=False)
    db.commit()
    return deleted_count
