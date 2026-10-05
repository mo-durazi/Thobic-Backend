# serializers/thoub_order.py
from pydantic import BaseModel, Field
from datetime import date, datetime
from typing import Optional, Dict, Any
from models.enums import OrderStatus

class ThoubOrderCreateSchema(BaseModel):
    tailor_id: int
    material_id: int
    material_amount: float = Field(gt=0)
    style: Dict[str, Any]
    requested_deadline: Optional[date] = None
    note: Optional[str] = None

class ThoubOrderUpdateSchema(BaseModel):
    material_id: Optional[int] = None
    material_amount: Optional[float] = Field(default=None, gt=0)
    style: Optional[Dict[str, Any]] = None
    requested_deadline: Optional[date] = None
    note: Optional[str] = None

class TailorAcceptSchema(BaseModel):
    price: float = Field(gt=0)
    final_deadline: date

class ClientRespondSchema(BaseModel):
    approve: bool


class ThoubOrderSchema(BaseModel):
    id: int
    client_id: int
    tailor_id: int
    material_id: int
    material_amount: float
    price: Optional[float] = None
    measurements_snapshot: Dict[str, Any]
    style: Dict[str, Any]
    status: OrderStatus
    requested_deadline: Optional[date] = None
    final_deadline: Optional[date] = None
    note: Optional[str] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
