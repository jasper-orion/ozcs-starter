"""Businessregels voor lokalen."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Room, User


def list_rooms(db: Session, user: User) -> list[Room]:
    """Alleen de lokalen van de eigen school."""
    stmt = select(Room).where(Room.school_id == user.school_id).order_by(Room.name)
    return list(db.scalars(stmt))
