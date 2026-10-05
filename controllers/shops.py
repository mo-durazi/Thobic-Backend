from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.user import UserModel
from models.profile import ProfileModel  # Adjust path if your profile model is named differently
from models.enums import UserRole, ShopStatus

router = APIRouter(prefix="/shops", tags=["Shops"])

@router.get("/", response_model=List[dict])
def get_shops(
    name: Optional[str] = Query(None, description="Filter by shop/display name"),
    branch: Optional[str] = Query(None, description="Filter by branch name"),
    status: Optional[ShopStatus] = Query(None, description="Filter by shop status (Open, Close, Busy)"),
    db: Session = Depends(get_db)
):
    """
    Public landing page endpoint: Browse and filter tailoring shops.
    Filters by name, branch, and open/busy/close status.
    """
    # Query users who are tailors and have a profile
    query = db.query(UserModel).filter(UserModel.role == UserRole.TAILOR)

    # We join with ProfileModel to filter by profile attributes (display_name, branch, status)
    query = query.join(ProfileModel, UserModel.id == ProfileModel.user_id)

    if name:
        query = query.filter(ProfileModel.display_name.ilike(f"%{name}%"))
    
    if branch:
        query = query.filter(ProfileModel.branch.ilike(f"%{branch}%"))
        
    if status:
        query = query.filter(ProfileModel.status == status)

    tailors = query.all()

    # Format output for the front-end shop cards
    shops_list = []
    for tailor in tailor_users := tailors:
        profile = tailor.profile # assuming a relationship named 'profile' exists on UserModel
        shops_list.append({
            "id": tailor.id,
            "username": tailor.username,
            "display_name": profile.display_name if profile else None,
            "branch": profile.branch if profile else None,
            "status": profile.status if profile else None,
            "road_no": profile.road_no if profile else None,
            "block_no": profile.block_no if profile else None,
            "building_no": profile.building_no if profile else None,
            "phone_number": profile.phone_number if profile else None,
        })

    return shops_list