from pydantic import BaseModel
from typing import Optional
from models.enums import ShopStatus


class ProfileBaseSchema(BaseModel):
    display_name: str
    road_no: int
    block_no: int
    building_no: int
    phone_number: str
    branch: Optional[str] = None
    status: Optional[ShopStatus] = None


class ProfileCreateSchema(ProfileBaseSchema):
    pass


class ProfileUpdateSchema(BaseModel):
    display_name: Optional[str] = None
    road_no: Optional[int] = None
    block_no: Optional[int] = None
    building_no: Optional[int] = None
    phone_number: Optional[str] = None
    branch: Optional[str] = None
    status: Optional[ShopStatus] = None


class ProfileSchema(ProfileBaseSchema):
    id: int
    user_id: int

    class Config:
        from_attributes = True