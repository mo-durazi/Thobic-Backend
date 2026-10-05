from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from database import get_db
from models.thoub_order import ThoubOrderModel
from models.user import UserModel
from models.material import MaterialModel
from models.client_measurements import ClientMeasurementsModel
from models.material_order import MaterialOrderModel
from models.enums import OrderStatus, UserRole
from dependencies.get_current_user import get_current_user


router = APIRouter(prefix="/orders", tags=["Thoub Orders"])

@router.post("/", status_code=status.HTTP_201_CREATED)
def create_thoub_order(
    order_data: dict, 
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Client creates a thoub order (saved as pending).
    Automatically takes a snapshot of the client's current measurements.
    """
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can place orders.")

    #Fetch client measurements for snapshot
    measurements = db.query(ClientMeasurementsModel).filter_by(client_id=current_user.id).first()
    if not measurements:
        raise HTTPException(status_code=400, detail="Please add your measurements before placing an order.")

    measurements_snapshot = {
        "neck": measurements.neck,
        "chest": measurements.chest,
        "arm": measurements.arm,
        "shoulders": measurements.shoulders,
        "waist": measurements.waist,
        "wrist": measurements.wrist,
        "length": measurements.length,
        "hips": measurements.hips
    }

    #Check material availability & status rules
    material = db.query(MaterialModel).filter_by(id=order_data.get("material_id")).first()
    if not material or material.is_deleted or not material.is_available:
        raise HTTPException(status_code=400, detail="Selected material is unavailable or deleted.")

    #Check requested deadline constraint (must be on or after creation date)
    req_deadline = order_data.get("requested_deadline")
    if req_deadline and req_deadline < date.today():
        raise HTTPException(status_code=400, detail="Requested deadline must be on or after today.")

    #Create the Thoub Order
    new_order = ThoubOrderModel(
        client_id=current_user.id,
        tailor_id=order_data.get("tailor_id"),
        material_id=order_data.get("material_id"),
        material_amount=order_data.get("material_amount"),
        style=order_data.get("style"),
        requested_deadline=req_deadline,
        note=order_data.get("note"),
        measurements_snapshot=measurements_snapshot,
        status=OrderStatus.PENDING
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/my-orders", response_model=List[dict])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """List all orders for the logged-in client or tailor."""
    if current_user.role == UserRole.CLIENT:
        orders = db.query(ThoubOrderModel).filter_by(client_id=current_user.id).all()
    elif current_user.role == UserRole.TAILOR:
        orders = db.query(ThoubOrderModel).filter_by(tailor_id=current_user.id).all()
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access to orders.")
    return orders




db.commit()
    db.refresh(order)
    return {"message": f"Order status updated to {order.status}", "order": order}