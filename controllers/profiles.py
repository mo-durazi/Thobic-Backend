import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.user import UserModel
from models.profile import ProfileModel
from models.enums import UserRole
from services.cloudinary_service import upload_image_with_metadata, delete_image
from serializers.profile import (
    ProfileSchema,
    ProfileCreateSchema,
    ProfileUpdateSchema,
)

router = APIRouter()
logger = logging.getLogger(__name__)

MAX_SHOP_PHOTO_BYTES = 5 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}


class ProfilePhotoSchema(BaseModel):
    shop_photo_url: str
    shop_photo_public_id: str


def _image_type_matches(content: bytes, content_type: str) -> bool:
    signatures = {
        "image/jpeg": content.startswith(b"\xff\xd8\xff"),
        "image/png": content.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": (
            len(content) >= 12
            and content.startswith(b"RIFF")
            and content[8:12] == b"WEBP"
        ),
    }
    return signatures.get(content_type, False)


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


@router.put(
    "/profiles/me/photo",
    response_model=ProfilePhotoSchema,
)
def upload_my_shop_photo(
    image: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    """Upload or replace the authenticated tailor's public shop photo."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tailors can upload a shop photo.",
        )

    profile = db.query(ProfileModel).filter_by(user_id=current_user.id).first()
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Profile not found. Create a profile before uploading a shop photo.",
        )

    if image.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
            detail="Upload a JPEG, PNG, or WebP image.",
        )

    content = image.file.read(MAX_SHOP_PHOTO_BYTES + 1)
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The uploaded image is empty.")
    if len(content) > MAX_SHOP_PHOTO_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="The shop photo must be 5 MB or smaller.",
        )
    if not _image_type_matches(content, image.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="The file contents do not match the declared image type.",
        )

    from io import BytesIO

    try:
        uploaded = upload_image_with_metadata(BytesIO(content))
    except Exception as exc:
        logger.exception("Cloudinary shop photo upload failed")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Unable to upload the shop photo right now.",
        ) from exc

    old_public_id = profile.shop_photo_public_id
    profile.shop_photo_url = uploaded["url"]
    profile.shop_photo_public_id = uploaded["public_id"]
    try:
        db.commit()
    except Exception as exc:
        db.rollback()
        try:
            delete_image(uploaded["public_id"])
        except Exception:
            logger.exception("Failed to clean up an uncommitted Cloudinary shop photo")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to save the shop photo.",
        ) from exc

    if old_public_id and old_public_id != uploaded["public_id"]:
        try:
            delete_image(old_public_id)
        except Exception:
            # The profile now points at the new asset; stale asset cleanup can be retried.
            logger.exception("Failed to remove replaced Cloudinary shop photo")

    return {
        "shop_photo_url": uploaded["url"],
        "shop_photo_public_id": uploaded["public_id"],
    }
