from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime

from models.enums import MaterialOrderStatus


class MaterialOrderAcceptSchema(BaseModel):
    expected_delivery_date: date
    notes: Optional[str] = None


class MaterialOrderRejectSchema(BaseModel):
    rejection_reason: str = Field(min_length=1)


class MaterialOrderSchema(BaseModel):
    id: int
    provider_id: int
    client_id: int
    thoub_order_id: int
    material_id: int
    amount: float
    price: float
    expected_delivery_date: Optional[date] = None
    status: MaterialOrderStatus
    notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    created_at: Optional[datetime] = None
    tailor_name: Optional[str] = None
    provider_name: Optional[str] = None
    material_name: Optional[str] = None

    class Config:
        from_attributes = True
