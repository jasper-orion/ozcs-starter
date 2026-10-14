"""Tests die gedrag bewijzen: aanmaken, validatie, schoolgrenzen, eigenaar-only annuleren, auditspoor."""

from sqlalchemy import select

from app.models import AuditLog
from tests.conftest import AN, BART, ROOM_NOORD, ROOM_ZUID


def reservation_payload(room_id=ROOM_NOORD, start="2026-10-20T09:00", end="2026-10-20T10:00", title="Oudercontact"):
    return {"room_id": room_id, "title": title, "start": start, "end": end}


def test_create_reservation(client):
    response = client.post("/reservations", json=reservation_payload(), headers=AN)

    assert response.status_code == 201
    body = response.json()
    assert body["room_name"] == "Lokaal A1"
    assert body["user_display_name"] == "An Testpersoon"
    assert body["start"] == "2026-10-20T09:00:00"


def test_rejects_end_before_start(client):
    payload = reservation_payload(start="2026-10-20T10:00", end="2026-10-20T09:00")

    response = client.post("/reservations", json=payload, headers=AN)

    assert response.status_code == 422


def test_rejects_too_long_reservation(client):
    payload = reservation_payload(start="2026-10-20T08:00", end="2026-10-20T18:00")

    response = client.post("/reservations", json=payload, headers=AN)

    assert response.status_code == 422


def test_rejects_title_that_is_too_short(client):
    response = client.post("/reservations", json=reservation_payload(title="  a "), headers=AN)

    assert response.status_code == 422


def test_requires_login(client):
    assert client.get("/reservations").status_code == 401
    assert client.get("/reservations", headers={"X-Dev-User": "999"}).status_code == 401


def test_user_of_other_school_cannot_see_reservations(client):
    client.post("/reservations", json=reservation_payload(), headers=AN)

    own = client.get("/reservations", headers=AN).json()
    other_school = client.get("/reservations", headers=BART).json()

    assert len(own) == 1
    assert other_school == []


def test_user_cannot_reserve_room_of_other_school(client):
    response = client.post("/reservations", json=reservation_payload(room_id=ROOM_ZUID), headers=AN)

    assert response.status_code == 404


def test_rooms_are_limited_to_own_school(client):
    names = {room["name"] for room in client.get("/rooms", headers=AN).json()}

    assert names == {"Lokaal A1", "Computerlokaal", "Vergaderzaal"}


def test_user_of_other_school_cannot_cancel(client):
    created = client.post("/reservations", json=reservation_payload(), headers=AN).json()

    response = client.delete(f"/reservations/{created['id']}", headers=BART)

    assert response.status_code == 404


def test_only_owner_can_cancel(client, colleague):
    created = client.post("/reservations", json=reservation_payload(), headers=AN).json()

    by_colleague = client.delete(f"/reservations/{created['id']}", headers=colleague)
    assert by_colleague.status_code == 403
    assert len(client.get("/reservations", headers=AN).json()) == 1

    by_owner = client.delete(f"/reservations/{created['id']}", headers=AN)
    assert by_owner.status_code == 204
    assert client.get("/reservations", headers=AN).json() == []


def test_cancel_writes_audit_row(client, db):
    created = client.post("/reservations", json=reservation_payload(), headers=AN).json()

    client.delete(f"/reservations/{created['id']}", headers=AN)

    rows = list(db.scalars(select(AuditLog)))
    assert len(rows) == 1
    assert rows[0].user_id == 1
    assert rows[0].action == "reservation.cancel"
    assert rows[0].entity_id == created["id"]
    assert rows[0].created_at is not None


def test_refused_cancel_writes_no_audit_row(client, db, colleague):
    created = client.post("/reservations", json=reservation_payload(), headers=AN).json()

    client.delete(f"/reservations/{created['id']}", headers=colleague)

    assert list(db.scalars(select(AuditLog))) == []


def test_health_and_version(client):
    assert client.get("/health").json() == {"status": "ok"}
    assert client.get("/version").json() == {"version": "dev"}
