from sqlalchemy import Column, Integer, Float, String, Enum as SQLEnum, Boolean, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from config.environment import JWT_SECRET
from models.enums import MaterialOrderStatus


class MaterialOrderModel(BaseModel):

    __tablename__ = "material_orders"

    #ATTRIBUTES
    id = Column(Integer, primary_key=True, index=True)
    order_from = Column(Integer, ForeignKey("users.id"), nullable=False) 
    # thoub_order_id = Column(Integer, nullable=False)  #TODO:waiting fo thoubOrderModel to be created
    amount = Column(Float, nullable=False)
    status = Column(
        SQLEnum(MaterialOrderStatus, name="material_order_status", value_callable=lambda e: [m.value for m in e]),
        nullable=False,
        default=MaterialOrderStatus.PENDING,
        server_default=MaterialOrderStatus.PENDING.value
    )
    created_at = Column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc)
    )  # Timestamp for when the order was created
    notes = Column(String, nullable=True)  # Optional notes for the order
    rejection_reason = Column(String, nullable=True)
    expected_delivery_date = Column(
        DateTime(timezone=True), 
        nullable=False)
    price = Column(Float, nullable=False) #TODO: need a function to calculate price based on material price and amount





    #RELATIONSHIPS
    order_from_user = relationship("UserModel", foreign_keys=[order_from])

    