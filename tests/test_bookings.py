from datetime import date, timedelta

import pytest
from fastapi.testclient import TestClient

TODAY = date.today()
TOMORROW = (TODAY + timedelta(days=1)).isoformat()


def booking_payload(**overrides) -> dict:
    payload = {
        "name": "Иван Петров",
        "phone": "+79991234567",
        "booking_date": TOMORROW,
        "booking_time": "19:00",
        "guests": 2,
    }
    payload.update(overrides)
    return payload


def create_booking(client: TestClient, **overrides):
    return client.post("/api/v1/bookings", json=booking_payload(**overrides))


def test_create_booking(client: TestClient):
    response = create_booking(client)

    assert response.status_code == 201
    body = response.json()
    assert body["id"] == 1
    assert body["status"] == "active"
    assert body["name"] == "Иван Петров"
    assert body["booking_date"] == TOMORROW


def test_create_booking_on_taken_slot_returns_409(client: TestClient):
    create_booking(client)

    response = create_booking(client, name="Другой гость", guests=4)

    assert response.status_code == 409
    assert response.json() == {"detail": "Slot is already booked"}


def test_cancelled_slot_can_be_booked_again(client: TestClient):
    booking_id = create_booking(client).json()["id"]

    cancel_response = client.delete(f"/api/v1/bookings/{booking_id}")
    assert cancel_response.status_code == 200
    assert cancel_response.json()["status"] == "cancelled"

    rebook_response = create_booking(client)
    assert rebook_response.status_code == 201
    assert rebook_response.json()["status"] == "active"


def test_cancel_is_idempotent(client: TestClient):
    booking_id = create_booking(client).json()["id"]

    assert client.delete(f"/api/v1/bookings/{booking_id}").status_code == 200
    second_cancel = client.delete(f"/api/v1/bookings/{booking_id}")

    assert second_cancel.status_code == 200
    assert second_cancel.json()["status"] == "cancelled"


def test_get_unknown_booking_returns_404(client: TestClient):
    response = client.get("/api/v1/bookings/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


def test_cancel_unknown_booking_returns_404(client: TestClient):
    response = client.delete("/api/v1/bookings/999")

    assert response.status_code == 404
    assert response.json() == {"detail": "Booking not found"}


def test_list_bookings_sorted_and_filtered_by_date(client: TestClient):
    later_date = (TODAY + timedelta(days=2)).isoformat()
    create_booking(client, booking_date=later_date, booking_time="20:00")
    create_booking(client, booking_time="18:00")

    all_bookings = client.get("/api/v1/bookings")
    assert all_bookings.status_code == 200
    assert [item["booking_time"] for item in all_bookings.json()] == [
        "18:00:00",
        "20:00:00",
    ]

    filtered = client.get("/api/v1/bookings", params={"date": later_date})
    assert filtered.status_code == 200
    assert len(filtered.json()) == 1
    assert filtered.json()[0]["booking_date"] == later_date


def test_list_includes_cancelled_bookings(client: TestClient):
    booking_id = create_booking(client).json()["id"]
    client.delete(f"/api/v1/bookings/{booking_id}")

    response = client.get("/api/v1/bookings")

    assert [item["status"] for item in response.json()] == ["cancelled"]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("name", "A"),
        ("name", "x" * 51),
        ("phone", "89991234567"),
        ("phone", "+7999123456"),
        ("phone", "+799912345678"),
        ("guests", 0),
        ("guests", 11),
        ("booking_date", (TODAY - timedelta(days=1)).isoformat()),
        ("booking_date", (TODAY + timedelta(days=31)).isoformat()),
        ("booking_time", "11:00"),
        ("booking_time", "23:00"),
        ("booking_time", "12:30"),
        ("booking_time", "19:00:30"),
    ],
)
def test_invalid_payload_returns_422(client: TestClient, field: str, value):
    response = create_booking(client, **{field: value})

    assert response.status_code == 422


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("booking_date", TODAY.isoformat()),
        ("booking_date", (TODAY + timedelta(days=30)).isoformat()),
        ("booking_time", "12:00"),
        ("booking_time", "22:00"),
    ],
)
def test_boundary_values_are_accepted(client: TestClient, field: str, value):
    response = create_booking(client, **{field: value})

    assert response.status_code == 201
