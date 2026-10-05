from pydantic import BaseModel
from typing import Optional


class ClientMeasurementsBaseSchema(BaseModel):
    neck: float
    chest: float
    arm: float
    shoulders: float
    waist: float
    wrist: float
    length: float
    hips: float


class ClientMeasurementsCreateSchema(ClientMeasurementsBaseSchema):
    pass


class ClientMeasurementsUpdateSchema(BaseModel):
    neck: Optional[float] = None
    chest: Optional[float] = None
    arm: Optional[float] = None
    shoulders: Optional[float] = None
    waist: Optional[float] = None
    wrist: Optional[float] = None
    length: Optional[float] = None
    hips: Optional[float] = None


class ClientMeasurementsSchema(ClientMeasurementsBaseSchema):
    id: int
    client_id: int

    class Config:
        from_attributes = True