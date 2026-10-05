from datetime import date

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from dependencies.role_required import require_role
from models.user import UserModel
from models.material_order import MaterialOrderModel
from models.thoub_order import ThoubOrderModel
from models.enums import MaterialOrderStatus, OrderStatus, UserRole
from serializers.material_order import (
    MaterialOrderSchema,
    MaterialOrderAcceptSchema,
    MaterialOrderRejectSchema,
)

router = APIRouter()


def create_material_order(thoub_order: ThoubOrderModel, db: Session):
    material = thoub_order.material

    if material.source.role != UserRole.PROVIDER:
        return None

    existing_order = (
        db.query(MaterialOrderModel)
        .filter(MaterialOrderModel.thoub_order_id == thoub_order.id)
        .first()
    )

    if existing_order:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A material order already exists for this thoub order",
        )

    new_order = MaterialOrderModel(
        provider_id=material.source_id,
        client_id=thoub_order.client_id,
        thoub_order_id=thoub_order.id,
        material_id=material.id,
        amount=thoub_order.material_amount,
        price=round(float(material.price) * thoub_order.material_amount, 2),
    )

    db.add(new_order)

    return new_order


def get_material_order_or_404(material_order_id: int, db: Session):
    order = (
        db.query(MaterialOrderModel)
        .filter(MaterialOrderModel.id == material_order_id)
        .first()
    )

    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Material order not found",
        )

    return order


def check_provider(order: MaterialOrderModel, current_user: UserModel):
    if order.provider_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the provider of this material order",
        )


def check_status(order: MaterialOrderModel, expected_status: MaterialOrderStatus):
    if order.status != expected_status:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Material order must be '{expected_status.value}', "
                   f"but it is '{order.status.value}'",
        )


# Routes

@router.get(
    "/material-orders",
    response_model=list[MaterialOrderSchema],
)
def get_material_orders(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("provider", "tailor")),
):
    query = db.query(MaterialOrderModel)

    if current_user.role == UserRole.PROVIDER:
        query = query.filter(MaterialOrderModel.provider_id == current_user.id)
    else:
        query = query.join(ThoubOrderModel).filter(
            ThoubOrderModel.tailor_id == current_user.id
        )

    return query.order_by(MaterialOrderModel.created_at.desc()).all()


@router.get(
    "/material-orders/{material_order_id}",
    response_model=MaterialOrderSchema,
)
def get_material_order(
    material_order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("provider", "tailor")),
):
    order = get_material_order_or_404(material_order_id, db)

    if current_user.id not in (order.provider_id, order.thoub_order.tailor_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to view this material order",
        )

    return order


@router.put(
    "/material-orders/{material_order_id}/accept",
    response_model=MaterialOrderSchema,
)
def accept_material_order(
    material_order_id: int,
    accept_data: MaterialOrderAcceptSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("provider")),
):
    order = get_material_order_or_404(material_order_id, db)
    check_provider(order, current_user)
    check_status(order, MaterialOrderStatus.PENDING)

    if accept_data.expected_delivery_date < date.today():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Expected delivery date can't be in the past",
        )

    order.status = MaterialOrderStatus.ACCEPTED
    order.expected_delivery_date = accept_data.expected_delivery_date
    order.notes = accept_data.notes

    db.commit()
    db.refresh(order)

    return order


@router.put(
    "/material-orders/{material_order_id}/reject",
    response_model=MaterialOrderSchema,
)
def reject_material_order(
    material_order_id: int,
    reject_data: MaterialOrderRejectSchema,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("provider")),
):
    order = get_material_order_or_404(material_order_id, db)
    check_provider(order, current_user)
    check_status(order, MaterialOrderStatus.PENDING)

    order.status = MaterialOrderStatus.REJECTED
    order.rejection_reason = reject_data.rejection_reason

    # The thoub order can't be made without its material
    if order.thoub_order.status == OrderStatus.CONFIRMED:
        order.thoub_order.status = OrderStatus.CANCELED

    db.commit()
    db.refresh(order)

    return order


@router.put(
    "/material-orders/{material_order_id}/on-the-way",
    response_model=MaterialOrderSchema,
)
def mark_material_order_on_the_way(
    material_order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("provider")),
):
    order = get_material_order_or_404(material_order_id, db)
    check_provider(order, current_user)
    check_status(order, MaterialOrderStatus.ACCEPTED)

    order.status = MaterialOrderStatus.ON_THE_WAY

    db.commit()
    db.refresh(order)

    return order


@router.put(
    "/material-orders/{material_order_id}/delivered",
    response_model=MaterialOrderSchema,
)
def mark_material_order_delivered(
    material_order_id: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(require_role("tailor")),
):
    order = get_material_order_or_404(material_order_id, db)

    if order.thoub_order.tailor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You are not the tailor of this order",
        )

    check_status(order, MaterialOrderStatus.ON_THE_WAY)

    order.status = MaterialOrderStatus.DELIVERED

    db.commit()
    db.refresh(order)

    return order
