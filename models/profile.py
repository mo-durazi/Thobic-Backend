from sqlalchemy import Column, Integer, String, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from models.enums import ShopStatus


class ProfileModel(BaseModel):
    __tablename__ = "profiles"

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False
    )

    display_name = Column(String, nullable=False)
    road_no = Column(Integer, nullable=False)
    block_no = Column(Integer, nullable=False)
    building_no = Column(Integer, nullable=False)
    phone_number = Column(String, nullable=False)

    branch = Column(String, nullable=True)

    status = Column(
        SQLEnum(
            ShopStatus,
            name="shop_status",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=True
    )

    user = relationship(
        "UserModel",
        back_populates="profile"
    )