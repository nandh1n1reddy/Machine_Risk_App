import os

import requests


BASE_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")


def request_json(method: str, path: str, **kwargs):
    try:
        response = requests.request(
            method,
            f"{BASE_URL}{path}",
            timeout=10,
            **kwargs,
        )
    except requests.RequestException as exc:
        raise RuntimeError(
            f"Cannot reach the backend at {BASE_URL}. Is it running?"
        ) from exc

    if not response.ok:
        try:
            detail = response.json().get("detail", response.text)
        except ValueError:
            detail = response.text
        raise RuntimeError(str(detail))

    return response.json()


def get_fields():
    return request_json("GET", "/api/fields")


def get_machines():
    return request_json("GET", "/api/machines")


def create_machine(data: dict):
    return request_json("POST", "/api/machines", json={"data": data})


def update_machine(machine_id: int, data: dict):
    return request_json(
        "PUT",
        f"/api/machines/{machine_id}",
        json={"data": data},
    )


def delete_machine(machine_id: int):
    return request_json("DELETE", f"/api/machines/{machine_id}")

def predict_machine(machine_id: int):
    return request_json(
        "POST",
        f"/api/machines/{machine_id}/predict",
    )

def create_field(
    name: str,
    field_type: str,
    required: bool,
    options: list[str] | None = None,
):
    return request_json(
        "POST",
        "/api/fields",
        json={
            "name": name,
            "field_type": field_type,
            "required": required,
            "options": options,
        },
    )


def update_field(
    field_id: int,
    required: bool,
    options: list[str] | None = None,
):
    return request_json(
        "PUT",
        f"/api/fields/{field_id}",
        json={
            "required": required,
            "options": options,
        },
    )


def delete_field(field_id: int):
    return request_json("DELETE", f"/api/fields/{field_id}")