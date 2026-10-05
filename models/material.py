from sqlalchemy import Column, String, Float, Integer, Boolean, ForeignKey, Enum as SQLEnum, Numeric, CheckConstraint
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
    __table_args__ = (CheckConstraint("price >= 0.01", name="check_price_positive"),)

    source_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    name = Column(String, nullable=False)
    price = Column(Numeric(10, 2), nullable=False)
    description = Column(String, nullable=True)
    colour = Column(String, nullable=False)

    texture = Column(
        SQLEnum(
            MaterialTexture,
            name="material_texture",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    pattern = Column(
        SQLEnum(
            MaterialPattern,
            name="material_pattern",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    season = Column(
        SQLEnum(
            MaterialSeason,
            name="material_season",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    stand = Column(
        SQLEnum(
            MaterialStand,
            name="material_stand",
            values_callable=lambda e: [m.value for m in e]
        ),
        nullable=False
    )

    lead_time_days = Column(Integer, nullable=True)

    is_available = Column(Boolean, nullable=False, default=True)
    is_deleted = Column(Boolean, nullable=False, default=False)

    image_url = Column(String, nullable=True)

    source = relationship("UserModel")

    @property
    def source_name(self):
        # to display the tailor or provider name on the material cards
        if self.source.profile:
            return self.source.profile.display_name
        return self.source.username
