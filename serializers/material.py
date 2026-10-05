from pydantic import BaseModel
from typing import Optional

from models.enums import (
    MaterialTexture,
    MaterialPattern,
    MaterialSeason,
    MaterialStand,
)


class MaterialBaseSchema(BaseModel):
    name: str
    price: float
    description: Optional[str] = None
    colour: str
    texture: MaterialTexture
    pattern: MaterialPattern
    season: MaterialSeason
    stand: MaterialStand
    lead_time_days: Optional[int] = None
    is_available: bool = True
    image_url: Optional[str] = None


class MaterialCreateSchema(MaterialBaseSchema):
    pass


class MaterialUpdateSchema(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = None
    description: Optional[str] = None
    colour: Optional[str] = None
    texture: Optional[MaterialTexture] = None
    pattern: Optional[MaterialPattern] = None
    season: Optional[MaterialSeason] = None
    stand: Optional[MaterialStand] = None
    lead_time_days: Optional[int] = None
    is_available: Optional[bool] = None
    image_url: Optional[str] = None


class MaterialSchema(MaterialBaseSchema):
    id: int
    source_id: int

    class Config:
        from_attributes = True