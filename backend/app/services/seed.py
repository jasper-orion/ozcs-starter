"""Verzonnen startgegevens voor de workshop. Geen echte scholen, personen of leerlingen."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Room, School, User


def seed_if_empty(db: Session) -> None:
    if db.scalar(select(School.id).limit(1)) is not None:
        return

    noord = School(name="Voorbeeldcollege Noord")
    zuid = School(name="Instituut Zuiderlicht")
    db.add_all([noord, zuid])
    db.flush()

    db.add_all(
        [
            User(display_name="An Testpersoon", school_id=noord.id),
            User(display_name="Bart Voorbeeld", school_id=zuid.id),
            Room(school_id=noord.id, name="Lokaal A1", capacity=24, location="Gebouw A, gelijkvloers"),
            Room(school_id=noord.id, name="Computerlokaal", capacity=16, location="Gebouw A, eerste verdieping"),
            Room(school_id=noord.id, name="Vergaderzaal", capacity=10, location="Administratie"),
            Room(school_id=zuid.id, name="Aula", capacity=80, location="Hoofdgebouw"),
            Room(school_id=zuid.id, name="Lokaal B2", capacity=24, location="Gebouw B, eerste verdieping"),
            Room(school_id=zuid.id, name="Overlegruimte", capacity=8, location="Leraarskamer"),
        ]
    )
    db.commit()
