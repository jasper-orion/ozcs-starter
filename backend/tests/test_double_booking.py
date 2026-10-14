"""Een lokaal kan niet twee keer tegelijk gereserveerd worden."""

from tests.conftest import AN, ROOM_NOORD


def payload(start: str, end: str, room_id: int = ROOM_NOORD) -> dict:
    return {"room_id": room_id, "title": "Vergadering", "start": start, "end": end}


def test_overlapping_reservation_of_same_room_is_rejected(client):
    first = client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00"), headers=AN)
    assert first.status_code == 201

    second = client.post("/reservations", json=payload("2026-10-20T09:30", "2026-10-20T10:30"), headers=AN)

    assert second.status_code == 409
    assert len(client.get("/reservations", headers=AN).json()) == 1


def test_reservation_inside_existing_one_is_rejected(client):
    client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T12:00"), headers=AN)

    response = client.post("/reservations", json=payload("2026-10-20T10:00", "2026-10-20T11:00"), headers=AN)

    assert response.status_code == 409


def test_back_to_back_reservations_are_allowed(client):
    client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00"), headers=AN)

    response = client.post("/reservations", json=payload("2026-10-20T10:00", "2026-10-20T11:00"), headers=AN)

    assert response.status_code == 201


def test_same_time_in_another_room_is_allowed(client):
    client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00"), headers=AN)

    response = client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00", room_id=2), headers=AN)

    assert response.status_code == 201


def test_cancelled_slot_can_be_booked_again(client):
    first = client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00"), headers=AN).json()
    client.delete(f"/reservations/{first['id']}", headers=AN)

    response = client.post("/reservations", json=payload("2026-10-20T09:00", "2026-10-20T10:00"), headers=AN)

    assert response.status_code == 201
