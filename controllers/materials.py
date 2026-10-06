from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.orm import Session, joinedload

from database import get_db
from dependencies.get_current_user import get_current_user
from dependencies.role_required import require_role
from models.user import UserModel
from models.material import MaterialModel
from models.enums import (
    UserRole,
    MaterialTexture,
    MaterialPattern,
    MaterialSeason,
    MaterialStand,
)
from serializers.material import (
    MaterialSchema,
    MaterialCreateSchema,
    MaterialUpdateSchema,
)
from services.cloudinary_service import upload_image


router = APIRouter()


@router.post("/materials/upload-image")
def upload_material_image(
    image: UploadFile = File(...),
    current_user: UserModel = Depends(require_role("tailor", "provider")),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image files are allowed",
        )

    image_url = upload_image(image.file)

    return {
        "image_url": image_url,
    }


@router.post(
    "/materials",
    response_model=MaterialSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_material(
    material: MaterialCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("tailor", "provider")),
):
    new_material = MaterialModel(
        source_id=current_user.id,
        **material.model_dump(),
    )

    db.add(new_material)
    db.commit()
    db.refresh(new_material)

    return new_material


@router.get(
    "/materials",
    response_model=list[MaterialSchema],
)
def get_materials(
    source_id: Optional[int] = None,
    source_role: Optional[UserRole] = None,
    texture: Optional[MaterialTexture] = None,
    pattern: Optional[MaterialPattern] = None,
    season: Optional[MaterialSeason] = None,
    stand: Optional[MaterialStand] = None,
    colour: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if min_price is not None and max_price is not None and min_price > max_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_price can't be greater than max_price",
        )

    query = (
        db.query(MaterialModel)
        .options(joinedload(MaterialModel.source).joinedload(UserModel.profile))
        .filter(
            MaterialModel.is_available == True,
            MaterialModel.is_deleted == False,
        )
    )

    if source_id is not None:
        query = query.filter(MaterialModel.source_id == source_id)

    # P07 provider materials: ?source_role=provider
    if source_role is not None:
        query = query.join(MaterialModel.source).filter(
            UserModel.role == source_role
        )

    if texture is not None:
        query = query.filter(MaterialModel.texture == texture)

    if pattern is not None:
        query = query.filter(MaterialModel.pattern == pattern)

    if season is not None:
        query = query.filter(MaterialModel.season == season)

    if stand is not None:
        query = query.filter(MaterialModel.stand == stand)

    if colour:
        query = query.filter(MaterialModel.colour.ilike(colour))

    if min_price is not None:
        query = query.filter(MaterialModel.price >= min_price)

    if max_price is not None:
        query = query.filter(MaterialModel.price <= max_price)

    return query.order_by(MaterialModel.created_at.desc()).all()


@router.get(
    "/materials/mine",
    response_model=list[MaterialSchema],
)
def get_my_materials(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("tailor", "provider")),
):
    # Includes unavailable materials so the owner can switch them back on
    materials = (
        db.query(MaterialModel)
        .filter(
            MaterialModel.source_id == current_user.id,
            MaterialModel.is_deleted == False,
        )
        .order_by(MaterialModel.created_at.desc())
        .all()
    )

    return materials


@router.get(
    "/materials/{material_id}",
    response_model=MaterialSchema,
)
def get_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    material = (
        db.query(MaterialModel)
        .filter(
            MaterialModel.id == material_id,
            MaterialModel.is_deleted == False,
        )
        .first()
    )

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )

    return material


@router.put(
    "/materials/{material_id}",
    response_model=MaterialSchema,
)
def update_material(
    material_id: int,
    material_data: MaterialUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("tailor", "provider")),
):
    material = (
        db.query(MaterialModel)
        .filter(
            MaterialModel.id == material_id,
            MaterialModel.is_deleted == False,
        )
        .first()
    )

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )

    if material.source_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to update this material",
        )

    update_data = material_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(material, field, value)

    db.commit()
    db.refresh(material)

    return material


@router.delete(
    "/materials/{material_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_material(
    material_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("tailor", "provider")),
):
    material = (
        db.query(MaterialModel)
        .filter(
            MaterialModel.id == material_id,
            MaterialModel.is_deleted == False,
        )
        .first()
    )

    if not material:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material not found",
        )

    if material.source_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this material",
        )

    material.is_deleted = True
    material.is_available = False

    db.commit()

    return None