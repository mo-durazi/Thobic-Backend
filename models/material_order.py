from sqlalchemy import Column, Integer, Float, String, Enum as SQLEnum, Boolean, ForeignKey, Date, Numeric, DateTime
from sqlalchemy.orm import relationship
from .base import BaseModel
from datetime import datetime, timedelta, timezone
from models.enums import MaterialOrderStatus


class MaterialOrderModel(BaseModel):

    __tablename__ = "material_orders"

    #-----------------ATTRIBUTES---------------------
    id = Column(Integer, primary_key=True, index=True)

    # Who is the provider of the material
    ordered_from = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Connected Thoub order
    # thoub_order_id = Column(Integer, ForeignKey("thoub_orders.id"), nullable=False, unique = True)
    
    # Amount of material ordered in metre
    amount = Column(Numeric(8, 2), nullable=False)

    # Price of the order, will be calculated by: amount * price_per_metre 
    price = Column(Numeric(10, 3), nullable=False) #TODO: need a function to calculate price based on material price and amount

    # Expected delivery date of the order
    expected_delivery_date = Column(Date, nullable=True)
    
    # Status of the order
    status = Column(
        SQLEnum(MaterialOrderStatus, name="material_order_status", 
                values_callable=lambda e: [m.value for m in e]),
                nullable=False,
                default=MaterialOrderStatus.PENDING,
                server_default=MaterialOrderStatus.PENDING.value
    )

    # When was the order created
    created_at = Column(
        DateTime(timezone=True), 
        default=datetime.now(timezone.utc)
    )  # Timestamp for when the order was created

    notes = Column(String, nullable=True)  # Optional notes for the order
    
    rejection_reason = Column(String, nullable=True)


    #-------------RELATIONSHIPS-----------------
    provider = relationship("UserModel", foreign_keys=[ordered_from])
    # thoub_order = relationship("ThoubOrderModel", back_populates="material_order", uselist=False)

    