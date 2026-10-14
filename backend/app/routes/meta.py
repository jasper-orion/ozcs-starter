"""Health, versie en de testgebruikers voor de dev-login."""

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.auth import get_current_user
from app.config import settings
from app.models import User, get_db
from app.schemas import HealthOut, UserOut, VersionOut
from app.services import users as user_service

router = APIRouter(tags=["meta"])


def _user_out(user: User) -> UserOut:
    return UserOut(id=user.id, display_name=user.display_name, school_name=user.school.name)


@router.get("/health", response_model=HealthOut)
def health():
    return HealthOut(status="ok")


@router.get("/version", response_model=VersionOut)
def version():
    return VersionOut(version=settings.app_version)


@router.get("/dev/users", response_model=list[UserOut])
def dev_users(db: Annotated[Session, Depends(get_db)]):
    """Lijst voor de testgebruiker-kiezer. Bestaat alleen zolang de dev-login aanstaat."""
    if not settings.dev_auth_enabled:
        raise HTTPException(status_code=404, detail="Niet gevonden.")
    return [_user_out(u) for u in user_service.list_users(db)]


@router.get("/me", response_model=UserOut)
def me(user: Annotated[User, Depends(get_current_user)]):
    return _user_out(user)
