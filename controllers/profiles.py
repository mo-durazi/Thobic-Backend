from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.user import UserModel
from models.profile import ProfileModel
from serializers.profile import (
    ProfileSchema,
    ProfileCreateSchema,
    ProfileUpdateSchema,
)

router = APIRouter()


@router.post(
    "/profiles",
    response_model=ProfileSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_profile(
    profile: ProfileCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    existing_profile = (
        db.query(ProfileModel)
        .filter(ProfileModel.user_id == current_user.id)
        .first()
    )

    if existing_profile:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Profile already exists",
        )

    new_profile = ProfileModel(
        user_id=current_user.id,
        **profile.model_dump(),
    )

    db.add(new_profile)
    db.commit()
    db.refresh(new_profile)

    return new_profile


@router.get(
    "/profiles/me",
    response_model=ProfileSchema,
)
def get_my_profile(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    profile = (
        db.query(ProfileModel)
        .filter(ProfileModel.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    return profile


@router.put(
    "/profiles/me",
    response_model=ProfileSchema,
)
def update_my_profile(
    profile_data: ProfileUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    profile = (
        db.query(ProfileModel)
        .filter(ProfileModel.user_id == current_user.id)
        .first()
    )

    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found",
        )

    update_data = profile_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(profile, field, value)

    db.commit()
    db.refresh(profile)

    return profile