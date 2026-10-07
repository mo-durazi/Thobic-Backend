from sqlalchemy import (
    Column,
    Integer,
    Float,
    String,
    Enum as SQLEnum,
    ForeignKey,
    Date,
)
from sqlalchemy.orm import relationship, backref

from .base import BaseModel
from models.enums import MaterialOrderStatus


class MaterialOrderModel(BaseModel):
    __tablename__ = "material_orders"

    id = Column(Integer, primary_key=True, index=True)

    provider_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    thoub_order_id = Column(
        Integer,
        ForeignKey("thoub_orders.id"),
        nullable=False,
        unique=True
    )

    material_id = Column(
        Integer,
        ForeignKey("materials.id"),
        nullable=False
    )

    amount = Column(Float, nullable=False)

    price = Column(Float, nullable=False)

    # Set by the provider when accepting the order
    expected_delivery_date = Column(Date, nullable=True)

    status = Column(
        SQLEnum(
            MaterialOrderStatus,
            name="material_order_status",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False,
        default=MaterialOrderStatus.PENDING,
        server_default=MaterialOrderStatus.PENDING.value
    )

    notes = Column(String, nullable=True)

    rejection_reason = Column(String, nullable=True)

    provider = relationship(
        "UserModel",
        foreign_keys=[provider_id]
    )

    client = relationship(
        "UserModel",
        foreign_keys=[client_id]
    )

    thoub_order = relationship(
        "ThoubOrderModel",
        foreign_keys=[thoub_order_id],
        backref=backref("material_order", uselist=False)
    )

    material = relationship(
        "MaterialModel",
        foreign_keys=[material_id]
    )

    @property
    def tailor_name(self):
        if not self.thoub_order or not self.thoub_order.tailor:
            return None
        tailor = self.thoub_order.tailor
        if tailor.profile:
            return tailor.profile.display_name
        return tailor.username

    @property
    def provider_name(self):
        if not self.provider:
            return None
        if self.provider.profile:
            return self.provider.profile.display_name
        return self.provider.username

    @property
    def material_name(self):
        if not self.material:
            return None
        return self.material.name
