"""Businessregels en autorisatie voor reservaties.

Elke query filtert op het school-id van de ingelogde gebruiker.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import AuditLog, Reservation, Room, User
from app.schemas import ReservationCreate
from app.services.errors import ConflictError, ForbiddenError, NotFoundError


def list_reservations(db: Session, user: User, mine_only: bool = False) -> list[Reservation]:
    """Reservaties van de eigen school, eventueel alleen die van de gebruiker zelf."""
    stmt = select(Reservation).where(Reservation.school_id == user.school_id)
    if mine_only:
        stmt = stmt.where(Reservation.user_id == user.id)
    return list(db.scalars(stmt.order_by(Reservation.start)))


def create_reservation(db: Session, user: User, data: ReservationCreate) -> Reservation:
    # Het lokaal moet bij de school van de gebruiker horen.
    room = db.scalar(select(Room).where(Room.id == data.room_id, Room.school_id == user.school_id))
    if room is None:
        raise NotFoundError("Lokaal niet gevonden.")

    # Twee reservaties van hetzelfde lokaal overlappen als elk begint voor het andere eindigt.
    # Aansluitende tijden (tot 10u en vanaf 10u) overlappen niet.
    overlap = db.scalar(
        select(Reservation.id).where(
            Reservation.room_id == room.id,
            Reservation.start < data.end,
            Reservation.end > data.start,
        )
    )
    if overlap is not None:
        raise ConflictError("Dit lokaal is al gereserveerd op dat moment.")

    reservation = Reservation(
        school_id=user.school_id,
        room_id=room.id,
        user_id=user.id,
        title=data.title,
        start=data.start,
        end=data.end,
    )
    db.add(reservation)
    db.commit()
    db.refresh(reservation)
    return reservation


def cancel_reservation(db: Session, user: User, reservation_id: int) -> None:
    """Annuleren mag alleen de eigenaar. Het auditspoor wordt in dezelfde transactie bewaard."""
    reservation = db.scalar(
        select(Reservation).where(Reservation.id == reservation_id, Reservation.school_id == user.school_id)
    )
    if reservation is None:
        raise NotFoundError("Reservatie niet gevonden.")
    if reservation.user_id != user.id:
        raise ForbiddenError("Je kan alleen je eigen reservaties annuleren.")

    db.add(AuditLog(user_id=user.id, action="reservation.cancel", entity_type="reservation", entity_id=reservation.id))
    db.delete(reservation)
    db.commit()  # verwijderen en logrij slagen samen of mislukken samen
