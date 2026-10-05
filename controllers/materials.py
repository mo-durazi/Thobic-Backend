from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.user import UserModel
from models.material import MaterialModel
from serializers.material import (
    MaterialSchema,
    MaterialCreateSchema,
    MaterialUpdateSchema,
)

router = APIRouter()


@router.post(
    "/materials",
    response_model=MaterialSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_material(
    material: MaterialCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if current_user.role.value not in ["tailor", "provider"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only tailors and providers can create materials",
        )

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
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    materials = (
        db.query(MaterialModel)
        .filter(
            MaterialModel.is_available == True,
            MaterialModel.is_deleted == False,
        )
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

    if material.source_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to delete this material",
        )

    material.is_deleted = True
    material.is_available = False

    db.commit()

    return None