from fastapi import Depends, HTTPException, status
from models.user import UserModel
from dependencies.get_current_user import get_current_user


def require_role(*allowed_roles):
    def role_checker(
        current_user: UserModel = Depends(get_current_user)
    ):
        if current_user.role.value not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to access this resource"
            )

        return current_user

    return role_checker