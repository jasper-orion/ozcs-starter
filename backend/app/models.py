"""Databasemodellen (SQLAlchemy 2) en de databaseverbinding.

Records verwijzen naar elkaar met database-id's (foreign keys), nooit met teksten
die iemand intypt.
"""

from collections.abc import Iterator
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column, relationship, sessionmaker

from app.config import settings


def utcnow() -> datetime:
    """Huidige tijd in UTC, zonder tijdzone-info (zo slaat SQLite het op)."""
    return datetime.now(timezone.utc).replace(tzinfo=None)


class Base(DeclarativeBase):
    pass


class School(Base):
    __tablename__ = "schools"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))


class User(Base):
    """Een personeelslid. Enig persoonsgegeven: de weergavenaam."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    display_name: Mapped[str] = mapped_column(String(100))
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)

    school: Mapped[School] = relationship()


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)
    name: Mapped[str] = mapped_column(String(100))
    capacity: Mapped[int]
    location: Mapped[str] = mapped_column(String(100))


class Reservation(Base):
    __tablename__ = "reservations"

    id: Mapped[int] = mapped_column(primary_key=True)
    school_id: Mapped[int] = mapped_column(ForeignKey("schools.id"), index=True)
    room_id: Mapped[int] = mapped_column(ForeignKey("rooms.id"), index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    title: Mapped[str] = mapped_column(String(100))
    start: Mapped[datetime] = mapped_column(DateTime)
    end: Mapped[datetime] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)

    room: Mapped[Room] = relationship()
    user: Mapped[User] = relationship()

    @property
    def room_name(self) -> str:
        return self.room.name

    @property
    def user_display_name(self) -> str:
        return self.user.display_name


class AuditLog(Base):
    """Logrij voor elke destructieve actie: wie, wat, wanneer. Geen persoonlijke inhoud."""

    __tablename__ = "audit_log"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(50))
    entity_type: Mapped[str] = mapped_column(String(50))
    entity_id: Mapped[int]
    created_at: Mapped[datetime] = mapped_column(DateTime, default=utcnow)


def create_db_engine(url: str) -> Engine:
    """Maakt de engine. Voor SQLite zetten we foreign keys aan (staat standaard uit)."""
    is_sqlite = url.startswith("sqlite")
    engine = create_engine(url, connect_args={"check_same_thread": False} if is_sqlite else {})
    if is_sqlite:

        @event.listens_for(engine, "connect")
        def _enable_foreign_keys(dbapi_connection, _record):
            dbapi_connection.execute("PRAGMA foreign_keys=ON")

    return engine


engine = create_db_engine(settings.database_url)
SessionLocal = sessionmaker(bind=engine, expire_on_commit=False)


def get_db() -> Iterator[Session]:
    """FastAPI-dependency: één databasesessie per request."""
    with SessionLocal() as db:
        yield db
