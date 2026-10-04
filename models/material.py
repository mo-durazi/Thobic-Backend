from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship

from .base import BaseModel
from models.enums import (
    MaterialTexture,
    MaterialPattern,
    MaterialSeason,
    MaterialStand,
)


class MaterialModel(BaseModel):
    __tablename__ = "materials"

    source_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    name = Column(String, nullable=False)
    price = Column(Float, nullable=False)
    description = Column(String, nullable=True)
    colour = Column(String, nullable=False)

    texture = Column(
        SQLEnum(
            MaterialTexture,
            name="material_texture",
            value_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    pattern = Column(
        SQLEnum(
            MaterialPattern,
            name="material_pattern",
            value_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    season = Column(
        SQLEnum(
            MaterialSeason,
            name="material_season",
            value_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    stand = Column(
        SQLEnum(
            MaterialStand,
            name="material_stand",
            value_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    lead_time_days = Column(Integer, nullable=True)

    is_available = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    image_url = Column(String, nullable=True)

    source = relationship("UserModel")