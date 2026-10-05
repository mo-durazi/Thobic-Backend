from pydantic import BaseModel, Field
from typing import Optional

from models.enums import (
    MaterialTexture,
    MaterialPattern,
    MaterialSeason,
    MaterialStand,
)


class MaterialBaseSchema(BaseModel):
    name: str = Field(min_length=1)
    price: float = Field(gt=0)
    description: Optional[str] = None
    colour: str = Field(min_length=1)
    texture: MaterialTexture
    pattern: MaterialPattern
    season: MaterialSeason
    stand: MaterialStand
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    is_available: bool = True
    image_url: Optional[str] = None


class MaterialCreateSchema(MaterialBaseSchema):
    pass


class MaterialUpdateSchema(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1)
    price: Optional[float] = Field(default=None, gt=0)
    description: Optional[str] = None
    colour: Optional[str] = Field(default=None, min_length=1)
    texture: Optional[MaterialTexture] = None
    pattern: Optional[MaterialPattern] = None
    season: Optional[MaterialSeason] = None
    stand: Optional[MaterialStand] = None
    lead_time_days: Optional[int] = Field(default=None, ge=0)
    is_available: Optional[bool] = None
    image_url: Optional[str] = None


class MaterialSchema(MaterialBaseSchema):
    id: int
    source_id: int

    class Config:
        from_attributes = True