from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.get_current_user import get_current_user
from models.user import UserModel
from serializers.user import AdminCreateUserSchema, UserSchema

router = APIRouter()


@router.post(
    "/admin/users",
    response_model=UserSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_user_by_admin(
    user_data: AdminCreateUserSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user),
):
    if current_user.role.value != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create users with specific roles",
        )

    if user_data.role.value == "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin users cannot be created through this endpoint",
        )

    existing_user = db.query(UserModel).filter(
        (UserModel.username == user_data.username)
        | (UserModel.email == user_data.email)
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username or email already exists",
        )

    new_user = UserModel(
        username=user_data.username,
        email=user_data.email,
        role=user_data.role,
    )

    new_user.set_password(user_data.password)

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user