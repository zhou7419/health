from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date, datetime

class PersonBase(BaseModel):
    name: str = Field(..., description="人员名称")
    gender: Optional[str] = Field(None, description="人员性别（如'男', '女'）")

class PersonCreate(PersonBase):
    pass

class PersonResponse(PersonBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MetricDefinitionBase(BaseModel):
    name: str = Field(..., description="指标名称，如'体重', '收缩压'")
    unit: Optional[str] = Field(None, description="单位，如'kg', 'mmHg'")
    expected_min: Optional[float] = Field(None, description="期望最小值")
    expected_max: Optional[float] = Field(None, description="期望最大值")

class MetricDefinitionCreate(MetricDefinitionBase):
    pass

class MetricDefinitionUpdate(BaseModel):
    name: Optional[str] = Field(None, description="指标名称")
    unit: Optional[str] = Field(None, description="单位")
    expected_min: Optional[float] = Field(None, description="期望最小值")
    expected_max: Optional[float] = Field(None, description="期望最大值")

class MetricDefinitionResponse(MetricDefinitionBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class MetricItemCreate(BaseModel):
    metric_id: Optional[int] = Field(None, description="已存在的指标ID")
    name: Optional[str] = Field(None, description="自定义指标名称（仅当metric_id为空时使用）")
    unit: Optional[str] = Field(None, description="自定义指标单位")
    expected_min: Optional[float] = Field(None, description="自定义指标期望最小值")
    expected_max: Optional[float] = Field(None, description="自定义指标期望最大值")
    value: float = Field(..., description="指标数值")
    notes: Optional[str] = Field(None, description="备注信息")

class MetricRecordBase(BaseModel):
    value: float = Field(..., description="指标数值")
    record_date: date = Field(..., description="体检日期")
    notes: Optional[str] = Field(None, description="备注信息")

class MetricRecordCreate(MetricRecordBase):
    metric_id: int

class MetricRecordUpdate(BaseModel):
    value: Optional[float] = Field(None, description="指标数值")
    record_date: Optional[date] = Field(None, description="体检日期")
    notes: Optional[str] = Field(None, description="备注信息")

class MetricRecordResponse(MetricRecordBase):
    id: int
    person_id: int
    metric_id: int
    created_at: datetime
    updated_at: datetime
    metric: MetricDefinitionResponse
    person: PersonResponse

    class Config:
        from_attributes = True

class BatchMetricCreate(BaseModel):
    person_id: int = Field(..., description="人员ID")
    record_date: date = Field(..., description="统一的体检日期")
    metrics: List[MetricItemCreate] = Field(..., description="指标列表")

class SmartParseRequest(BaseModel):
    text: str = Field(..., description="待解析的自然语言文本")
    images: Optional[List[str]] = Field(None, description="图片的base64编码列表")

class HealthAdviceRequest(BaseModel):
    person_id: int = Field(..., description="需要生成健康建议的人员ID")
