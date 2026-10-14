"""HTTP-laag voor lokalen. Geen businesslogica hier: alles gaat via de services."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.models import User, get_db
from app.schemas import RoomOut
from app.services import rooms as room_service

router = APIRouter(prefix="/rooms", tags=["rooms"])


@router.get("", response_model=list[RoomOut])
def list_rooms(
    db: Annotated[Session, Depends(get_db)],
    user: Annotated[User, Depends(get_current_user)],
):
    return room_service.list_rooms(db, user)
