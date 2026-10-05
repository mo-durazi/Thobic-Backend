from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.user import UserModel
from models.client_measurements import ClientMeasurementsModel
from serializers.client_measurements import (
    ClientMeasurementsSchema,
    ClientMeasurementsCreateSchema,
    ClientMeasurementsUpdateSchema,
)

router = APIRouter()


@router.post(
    "/measurements",
    response_model=ClientMeasurementsSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_measurements(
    measurements: ClientMeasurementsCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    existing_measurements = (
        db.query(ClientMeasurementsModel)
        .filter(ClientMeasurementsModel.client_id == current_user.id)
        .first()
    )

    if existing_measurements:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Measurements already exist",
        )

    new_measurements = ClientMeasurementsModel(
        client_id=current_user.id,
        **measurements.model_dump(),
    )

    db.add(new_measurements)
    db.commit()
    db.refresh(new_measurements)

    return new_measurements


@router.get(
    "/measurements/me",
    response_model=ClientMeasurementsSchema,
)
def get_my_measurements(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    measurements = (
        db.query(ClientMeasurementsModel)
        .filter(ClientMeasurementsModel.client_id == current_user.id)
        .first()
    )

    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurements not found",
        )

    return measurements


@router.put(
    "/measurements/me",
    response_model=ClientMeasurementsSchema,
)
def update_my_measurements(
    measurements_data: ClientMeasurementsUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    measurements = (
        db.query(ClientMeasurementsModel)
        .filter(ClientMeasurementsModel.client_id == current_user.id)
        .first()
    )

    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurements not found",
        )

    update_data = measurements_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(measurements, field, value)

    db.commit()
    db.refresh(measurements)

    return measurements


@router.delete(
    "/measurements/me",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_my_measurements(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    measurements = (
        db.query(ClientMeasurementsModel)
        .filter(ClientMeasurementsModel.client_id == current_user.id)
        .first()
    )

    if not measurements:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Measurements not found",
        )

    db.delete(measurements)
    db.commit()

    return None