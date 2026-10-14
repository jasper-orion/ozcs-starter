"""Testopzet: elke test krijgt een verse database in het geheugen met de verzonnen seed-data."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.models import Base, User, get_db
from app.services.seed import seed_if_empty

# Seed-gebruikers: 1 = An (Voorbeeldcollege Noord), 2 = Bart (Instituut Zuiderlicht).
AN = {"X-Dev-User": "1"}
BART = {"X-Dev-User": "2"}
# Seed-lokalen: 1 = Lokaal A1 (school Noord), 4 = Aula (school Zuid).
ROOM_NOORD = 1
ROOM_ZUID = 4


@pytest.fixture()
def session_factory():
    # StaticPool: alle sessies delen dezelfde in-memory database.
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    with factory() as db:
        seed_if_empty(db)
    yield factory
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    def override_get_db():
        with session_factory() as db:
            yield db

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def db(session_factory):
    with session_factory() as session:
        yield session


@pytest.fixture()
def colleague(db):
    """Een tweede gebruiker op school Noord, om 'alleen de eigenaar' te testen."""
    user = User(display_name="Carla Collega", school_id=1)
    db.add(user)
    db.commit()
    return {"X-Dev-User": str(user.id)}
