from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from database import get_db
from models.user import UserModel
from models.profile import ProfileModel
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
    query = db.query(UserModel).filter(UserModel.role == UserRole.TAILOR)
    query = query.join(ProfileModel, UserModel.id == ProfileModel.user_id)

    if name:
        query = query.filter(ProfileModel.display_name.ilike(f"%{name}%"))
    
    if branch:
        query = query.filter(ProfileModel.branch.ilike(f"%{branch}%"))
        
    if status:
        query = query.filter(ProfileModel.status == status)

    tailors = query.all()

    shops_list = []
    for tailor in tailors:
        profile = tailor.profile if hasattr(tailor, "profile") else None
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


@router.get("/{shop_id}")
def get_shop_profile(
    shop_id: int,
    db: Session = Depends(get_db)
):
    """
    Shop Profile page: Show specific shop details and in-stock materials to start an order.
    """
    tailor = db.query(UserModel).filter(UserModel.id == shop_id, UserModel.role == UserRole.TAILOR).first()
    
    if not tailor:
        raise HTTPException(status_code=404, detail="Tailoring shop not found.")

    profile = db.query(ProfileModel).filter_by(user_id=tailor.id).first()

    materials = [
        {
            "id": mat.id,
            "name": mat.name,
            "price": mat.price,
            "colour": mat.colour,
            "texture": mat.texture,
            "pattern": mat.pattern,
            "season": mat.season,
            "stand": mat.stand,
            "is_available": mat.is_available,
            "image_url": mat.image_url
        }
        for mat in tailor.materials if not mat.is_deleted
    ] if hasattr(tailor, "materials") else []

    return {
        "id": tailor.id,
        "username": tailor.username,
        "display_name": profile.display_name if profile else "Unknown Shop",
        "branch": profile.branch if profile else None,
        "status": profile.status if profile else None,
        "address": {
            "road_no": profile.road_no if profile else None,
            "block_no": profile.block_no if profile else None,
            "building_no": profile.building_no if profile else None,
        },
        "phone_number": profile.phone_number if profile else None,
        "materials": materials
    }
    