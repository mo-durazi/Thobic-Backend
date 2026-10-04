from sqlalchemy import Column, Integer, Float, String, Date, JSON, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from models.enums import OrderStatus


class ThoubOrderModel(BaseModel):
    __tablename__ = "thoub_orders"

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    tailor_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    price = Column(Float, nullable=True)

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=False
    )

    measurements_snapshot = Column(JSON, nullable=False)

    status = Column(
        SQLEnum(
            OrderStatus,
            name="order_status",
            value_callable=lambda e: [m.value for m in e]
        ),
        nullable=False,
        default=OrderStatus.PENDING
    )

    style = Column(JSON, nullable=False)

    requested_deadline = Column(Date, nullable=True)

    final_deadline = Column(Date, nullable=True)

    material_amount = Column(Float, nullable=False)

    note = Column(String, nullable=True)

    client = relationship(
        "UserModel",
        foreign_keys=[client_id]
    )

    tailor = relationship(
        "UserModel",
        foreign_keys=[tailor_id]
    )

    material = relationship("MaterialModel")