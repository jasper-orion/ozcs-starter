"""HTTP-laag voor reservaties. Geen businesslogica hier: alles gaat via de services."""

from typing import Annotated

from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.models import User, get_db
from app.schemas import ReservationCreate, ReservationOut
from app.services import reservations as reservation_service

router = APIRouter(prefix="/reservations", tags=["reservations"])


@router.get("", response_model=list[ReservationOut])
def list_reservations(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
    mine: bool = False,
):
    return reservation_service.list_reservations(db, user, mine_only=mine)


@router.post("", response_model=ReservationOut, status_code=201)
def create_reservation(
    data: ReservationCreate,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return reservation_service.create_reservation(db, user, data)


@router.delete("/{reservation_id}", status_code=204)
def cancel_reservation(
    reservation_id: int,
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    reservation_service.cancel_reservation(db, user, reservation_id)
    return Response(status_code=204)
