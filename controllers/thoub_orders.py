from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from decimal import Decimal

from database import get_db
from models.thoub_order import ThoubOrderModel
from models.user import UserModel
from models.material import MaterialModel
from models.client_measurements import ClientMeasurementsModel
from models.material_order import MaterialOrderModel
from models.enums import OrderStatus, UserRole, MaterialOrderStatus
from dependencies.get_current_user import get_current_user

# Import the existing material order helper function from controllers.material_order
from controllers.material_order import create_material_order

# Import Pydantic validation schemas
from serializers.thoub_order import (
    ThoubOrderCreateSchema,
    ThoubOrderUpdateSchema,
    TailorAcceptSchema,
    ClientRespondSchema,
    ThoubOrderSchema,
)

router = APIRouter(prefix="/orders", tags=["Thoub Orders"])

@router.post("", response_model=ThoubOrderSchema, status_code=status.HTTP_201_CREATED)
def create_thoub_order(
    payload: ThoubOrderCreateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Client creates a thoub order (saved as pending)."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can place orders.")

    # Validate that tailor_id actually exists and is a tailor
    tailor = db.query(UserModel).filter_by(id=payload.tailor_id, role=UserRole.TAILOR).first()
    if not tailor:
        raise HTTPException(status_code=400, detail="The selected tailor does not exist or is not a tailor.")

    measurements = db.query(ClientMeasurementsModel).filter_by(client_id=current_user.id).first()
    if not measurements:
        raise HTTPException(status_code=400, detail="Please add your measurements before placing an order.")

    measurements_snapshot = {
        "neck": measurements.neck, "chest": measurements.chest, "arm": measurements.arm,
        "shoulders": measurements.shoulders, "waist": measurements.waist, "wrist": measurements.wrist,
        "length": measurements.length, "hips": measurements.hips
    }

   
    material = db.query(MaterialModel).filter_by(id=payload.material_id).first()
    if not material or material.is_deleted or not material.is_available:
        raise HTTPException(status_code=400, detail="Selected material is unavailable or deleted.")
    if material.source_id != payload.tailor_id and material.source.role != UserRole.PROVIDER:
        raise HTTPException(status_code=400, detail="This material isn't available from the selected shop.")

    if payload.requested_deadline and payload.requested_deadline < date.today():
        raise HTTPException(status_code=400, detail="Requested deadline must be on or after today.")

    new_order = ThoubOrderModel(
        client_id=current_user.id,
        tailor_id=payload.tailor_id,
        material_id=payload.material_id,
        material_amount=payload.material_amount,
        style=payload.style.model_dump(mode="json"),
        requested_deadline=payload.requested_deadline,
        note=payload.note,
        measurements_snapshot=measurements_snapshot,
        status=OrderStatus.PENDING
    )

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    return new_order

@router.get("/my-orders", response_model=list[ThoubOrderSchema])
def get_my_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """List all orders for the logged-in client or tailor."""
    if current_user.role == UserRole.CLIENT:
        query = db.query(ThoubOrderModel).filter_by(client_id=current_user.id)
    elif current_user.role == UserRole.TAILOR:
        query = db.query(ThoubOrderModel).filter_by(tailor_id=current_user.id)
    else:
        raise HTTPException(status_code=403, detail="Unauthorized access to orders.")

    return query.order_by(ThoubOrderModel.created_at.desc()).all()


@router.get("/{order_id}", response_model=ThoubOrderSchema)
def get_thoub_order_by_id(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Get details for a specific order (accessible by involved client or tailor, or admin)."""
    order = db.query(ThoubOrderModel).filter_by(id=order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    is_involved = current_user.id in (order.client_id, order.tailor_id)
    if not is_involved and current_user.role != UserRole.ADMIN:
        raise HTTPException(status_code=403, detail="Access denied.")

    return order


@router.put("/{order_id}", response_model=ThoubOrderSchema)
def edit_thoub_order(
    order_id: int,
    payload: ThoubOrderUpdateSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Client can edit an order ONLY while it is pending."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can edit their orders.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, client_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=409, detail="Orders can only be edited while they are pending.")

   
    if payload.material_id is not None:
        material = db.query(MaterialModel).filter_by(id=payload.material_id).first()
        if not material or material.is_deleted or not material.is_available:
            raise HTTPException(status_code=400, detail="Selected material is unavailable or deleted.")
        if material.source_id != order.tailor_id and material.source.role != UserRole.PROVIDER:
            raise HTTPException(status_code=400, detail="This material isn't available from the selected shop.")
        order.material_id = payload.material_id

    if payload.material_amount is not None:
        order.material_amount = payload.material_amount
    if payload.style is not None:
        order.style = payload.style.model_dump(mode="json")
    if payload.requested_deadline is not None:
        if payload.requested_deadline < date.today():
            raise HTTPException(status_code=400, detail="Requested deadline must be on or after today.")
        order.requested_deadline = payload.requested_deadline
    if payload.note is not None:
        order.note = payload.note

    db.commit()
    db.refresh(order)
    return order


@router.delete("/{order_id}", status_code=status.HTTP_200_OK)
def delete_thoub_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Client can delete an order ONLY while it is pending."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can delete their orders.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, client_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=409, detail="Orders can only be deleted while they are pending.")

    db.delete(order)
    db.commit()
    return {"message": "Order deleted successfully"}


@router.patch("/{order_id}/tailor-accept", response_model=ThoubOrderSchema)
def tailor_accept_order(
    order_id: int,
    payload: TailorAcceptSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Tailor accepts an order, sets price and final deadline."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(status_code=403, detail="Only tailors can accept orders.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, tailor_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=409, detail="Can only accept pending orders.")

    # Handle Decimal vs float arithmetic safely
    mat_price = Decimal(str(order.material.price))
    mat_amount = Decimal(str(order.material_amount))
    min_price = float(mat_price * mat_amount)

    if payload.price < min_price:
        raise HTTPException(status_code=400, detail=f"Price cannot be less than material cost ({min_price}).")

    if order.requested_deadline and payload.final_deadline < order.requested_deadline:
        raise HTTPException(status_code=400, detail="Final deadline cannot be before the requested deadline.")

    order.price = payload.price
    order.final_deadline = payload.final_deadline
    order.status = OrderStatus.ACCEPTED

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/tailor-reject", response_model=ThoubOrderSchema)
def tailor_reject_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Tailor rejects a pending order."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(status_code=403, detail="Only tailors can reject orders.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, tailor_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.PENDING:
        raise HTTPException(status_code=409, detail="Can only reject pending orders.")

    order.status = OrderStatus.TAILOR_REJECTED
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/client-respond", response_model=ThoubOrderSchema)
def client_respond_order(
    order_id: int,
    payload: ClientRespondSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Client approves (confirmed) or declines (client_rejected) an accepted order."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only clients can respond to orders.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, client_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.ACCEPTED:
        raise HTTPException(status_code=409, detail="Order must be in 'accepted' status.")

    if payload.approve:
        order.status = OrderStatus.CONFIRMED
        create_material_order(order, db)
    else:
        order.status = OrderStatus.CLIENT_REJECTED

    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/in-progress", response_model=ThoubOrderSchema)
def mark_order_in_progress(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Tailor moves order from confirmed to in_progress (compares against MaterialOrderStatus.DELIVERED)."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(status_code=403, detail="Only tailors can update order progress.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, tailor_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.CONFIRMED:
        raise HTTPException(status_code=409, detail="Order must be confirmed before starting work.")

    material_order = db.query(MaterialOrderModel).filter_by(thoub_order_id=order.id).first()
    if material_order and material_order.status != MaterialOrderStatus.DELIVERED:
        raise HTTPException(status_code=409, detail="Cannot start work until the provider material is delivered.")

    order.status = OrderStatus.IN_PROGRESS
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/ready", response_model=ThoubOrderSchema)
def mark_order_ready(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Tailor moves order from in_progress to ready."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(status_code=403, detail="Only tailors can update order progress.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, tailor_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail="Order must be in-progress to be marked ready.")

    order.status = OrderStatus.READY
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/on-the-way", response_model=ThoubOrderSchema)
def mark_order_on_the_way(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Tailor moves order from ready to on_the_way."""
    if current_user.role != UserRole.TAILOR:
        raise HTTPException(status_code=403, detail="Only tailors can update order progress.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, tailor_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.READY:
        raise HTTPException(status_code=409, detail="Order must be ready before sending it on the way.")

    order.status = OrderStatus.ON_THE_WAY
    db.commit()
    db.refresh(order)
    return order


@router.patch("/{order_id}/delivered", response_model=ThoubOrderSchema)
def mark_order_delivered(
    order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """Client marks order as delivered when it is on_the_way."""
    if current_user.role != UserRole.CLIENT:
        raise HTTPException(status_code=403, detail="Only the client can confirm delivery.")

    order = db.query(ThoubOrderModel).filter_by(id=order_id, client_id=current_user.id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    if order.status != OrderStatus.ON_THE_WAY:
        raise HTTPException(status_code=409, detail="Order must be on the way to be confirmed as delivered.")

    order.status = OrderStatus.DELIVERED
    db.commit()
    db.refresh(order)
    return order
