from sqlalchemy import Column, Integer, Float, String, Enum as SQLEnum, Boolean
from sqlalchemy.orm import relationship
from .base import BaseModel
from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
import jwt
from config.environment import JWT_SECRET



class MaterialModel(BaseModel):
    __tablename__ = "materials"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=False)  # Each material name must be unique
    price = Column(Float, nullable=False)  # Price of the material
    description = Column(String, nullable=True)  # Optional description of the material
    color = Column(String, nullable=False)  # Optional color of the material
    lead_time_days = Column(Integer, nullable=False)  # Lead time in days for the material
    is_available = Column(Boolean, default=True)  # Availability status of the material
    is_deleted = Column(Boolean, default=False)  # Soft delete flag for the material
    image_url = Column(String, nullable=True)  # Optional image URL for the 




    # Relationship to other models (if needed)
    # For example, if a material can be associated with multiple products:
    # products = relationship("ProductModel", back_populates="material")