from sqlalchemy import Column, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship

from .base import BaseModel


class ClientMeasurementsModel(BaseModel):
    __tablename__ = "client_measurements"

    client_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
        unique=True
    )

    neck = Column(Float, nullable=False)
    chest = Column(Float, nullable=False)
    arm = Column(Float, nullable=False)
    shoulders = Column(Float, nullable=False)
    waist = Column(Float, nullable=False)
    wrist = Column(Float, nullable=False)
    length = Column(Float, nullable=False)
    hips = Column(Float, nullable=False)

    client = relationship("UserModel")