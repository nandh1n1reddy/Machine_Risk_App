import re
import math

from ml.predictor import predict_risk

from typing import Any
from backend.models import FieldDefinition, Machine

from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field, field_validator

from backend.database import SessionLocal
from backend.models import FieldDefinition



app = FastAPI(
    title="Machine Risk App API",
    description="Backend API for dynamic machine field configuration.",
    version="1.0.0"
)

VALID_FIELD_TYPES = {"text", "number", "dropdown"}

def generate_key(name: str) -> str:
    key = name.strip().lower()

    key = re.sub(r"[^a-z0-9]+", "_", key)

    key = key.strip("_")

    return key

class FieldCreate(BaseModel):
    name: str
    field_type: str
    required: bool = False
    options: list[str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError("Field name cannot be empty")

        return value

    @field_validator("field_type")
    @classmethod
    def validate_field_type(cls, value):
        value = value.lower().strip()

        if value not in VALID_FIELD_TYPES:
            raise ValueError(
                "field_type must be one of: text, number, dropdown"
            )

        return value

    @field_validator("options")
    @classmethod
    def validate_options(cls, value, info):
        field_type = info.data.get("field_type")

        if field_type == "dropdown":
            if not value or len(value) == 0:
                raise ValueError(
                    "Dropdown fields must have at least one option"
                )

            cleaned_options = [
                option.strip()
                for option in value
                if option.strip()
            ]

            if not cleaned_options:
                raise ValueError(
                    "Dropdown fields must have at least one valid option"
                )

            return cleaned_options

        return None

def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


class MachinePayload(BaseModel):
    data: dict[str, Any]


def validate_machine_data(
    data: dict[str, Any],
    fields: list[FieldDefinition]
) -> dict[str, Any]:
    """Validate submitted values against the current field definitions."""
    known_keys = {field.key for field in fields}
    unknown_keys = set(data) - known_keys

    if unknown_keys:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown fields: {', '.join(sorted(unknown_keys))}"
        )

    cleaned: dict[str, Any] = {}

    for field in fields:
        value = data.get(field.key)

        is_blank = value is None or value == ""
        if field.field_type == "text" and isinstance(value, str):
            value = value.strip()
            is_blank = not value

        if is_blank:
            if field.required:
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.name} is required."
                )
            continue

        if field.field_type == "text":
            if not isinstance(value, str):
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.name} must be text."
                )

        elif field.field_type == "number":
            if (
                isinstance(value, bool)
                or not isinstance(value, (int, float))
                or not math.isfinite(value)
            ):
                raise HTTPException(
                    status_code=400,
                    detail=f"{field.name} must be a valid number."
                )

        elif field.field_type == "dropdown":
            if not isinstance(value, str) or value not in (field.options or []):
                raise HTTPException(
                    status_code=400,
                    detail=f"Choose a valid option for {field.name}."
                )

        cleaned[field.key] = value

    return cleaned


def machine_to_dict(machine: Machine) -> dict[str, Any]:
    return {
        "id": machine.id,
        "data": machine.data or {},
        "created_at": machine.created_at,
        "updated_at": machine.updated_at,
    }

@app.get("/")

def root():
    return {
        "message": "Machine Risk App API is running"
    }

@app.get("/api/fields")
def get_fields(db: Session = Depends(get_db)):
    fields = (
        db.query(FieldDefinition)
        .order_by(FieldDefinition.display_order)
        .all()
    )

    return [
        {
            "id": field.id,
            "name": field.name,
            "key": field.key,
            "field_type": field.field_type,
            "required": field.required,
            "options": field.options,
            "display_order": field.display_order,
            "created_at": field.created_at,
        }
        for field in fields
    ]

@app.post("/api/fields")
def create_field(
    field_data: FieldCreate,
    db: Session = Depends(get_db)
):
    # Check duplicate field name
    existing_name = (
        db.query(FieldDefinition)
        .filter(
            FieldDefinition.name.ilike(field_data.name)
        )
        .first()
    )

    if existing_name:
        raise HTTPException(
            status_code=400,
            detail="A field with this name already exists."
        )

    # Generate key automatically
    key = generate_key(field_data.name)

    # Check duplicate key
    existing_key = (
        db.query(FieldDefinition)
        .filter(FieldDefinition.key == key)
        .first()
    )

    if existing_key:
        raise HTTPException(
            status_code=400,
            detail="A field with this name would create a duplicate key."
        )

    # Determine display order
    last_field = (
        db.query(FieldDefinition)
        .order_by(FieldDefinition.display_order.desc())
        .first()
    )

    next_order = (
        last_field.display_order + 1
        if last_field
        else 1
    )

    new_field = FieldDefinition(
        name=field_data.name,
        key=key,
        field_type=field_data.field_type,
        required=field_data.required,
        options=field_data.options,
        display_order=next_order
    )

    db.add(new_field)
    db.commit()
    db.refresh(new_field)

    return {
        "message": "Field created successfully",
        "field": {
            "id": new_field.id,
            "name": new_field.name,
            "key": new_field.key,
            "field_type": new_field.field_type,
            "required": new_field.required,
            "options": new_field.options,
            "display_order": new_field.display_order
        }
    }

class FieldUpdate(BaseModel):
    name: str | None = None
    required: bool | None = None
    options: list[str] | None = None

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError("Field name cannot be empty")

        return value


@app.put("/api/fields/{field_id}")
def update_field(
    field_id: int,
    field_data: FieldUpdate,
    db: Session = Depends(get_db)
):
    field = (
        db.query(FieldDefinition)
        .filter(FieldDefinition.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found."
        )

    # Update name if provided
    if field_data.name is not None:

        existing_name = (
            db.query(FieldDefinition)
            .filter(
                FieldDefinition.name.ilike(field_data.name),
                FieldDefinition.id != field_id
            )
            .first()
        )

        if existing_name:
            raise HTTPException(
                status_code=400,
                detail="A field with this name already exists."
            )

        new_key = generate_key(field_data.name)

        existing_key = (
            db.query(FieldDefinition)
            .filter(
                FieldDefinition.key == new_key,
                FieldDefinition.id != field_id
            )
            .first()
        )

        if existing_key:
            raise HTTPException(
                status_code=400,
                detail="This name would create a duplicate field key."
            )

        field.name = field_data.name
        field.key = new_key

    # Update required
    if field_data.required is not None:
        field.required = field_data.required

    # Update options
    if field_data.options is not None:

        if field.field_type == "dropdown":

            cleaned_options = [
                option.strip()
                for option in field_data.options
                if option.strip()
            ]

            if not cleaned_options:
                raise HTTPException(
                    status_code=400,
                    detail="Dropdown fields must have at least one option."
                )

            field.options = cleaned_options

        else:
            field.options = None

    db.commit()
    db.refresh(field)

    return {
        "message": "Field updated successfully",
        "field": {
            "id": field.id,
            "name": field.name,
            "key": field.key,
            "field_type": field.field_type,
            "required": field.required,
            "options": field.options,
            "display_order": field.display_order
        }
    }

@app.delete("/api/fields/{field_id}")
def delete_field(
    field_id: int,
    db: Session = Depends(get_db)
):
    field = (
        db.query(FieldDefinition)
        .filter(FieldDefinition.id == field_id)
        .first()
    )

    if not field:
        raise HTTPException(
            status_code=404,
            detail="Field not found."
        )

    db.delete(field)
    db.commit()

    return {
        "message": (
            "Field deleted successfully. "
            "Existing machine JSON values are preserved."
        )
    }


@app.get("/api/machines")
def get_machines(db: Session = Depends(get_db)):
    machines = db.query(Machine).order_by(Machine.id).all()
    return [machine_to_dict(machine) for machine in machines]


@app.get("/api/machines/{machine_id}")
def get_machine(
    machine_id: int,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found.")

    return machine_to_dict(machine)


@app.post("/api/machines", status_code=201)
def create_machine(
    payload: MachinePayload,
    db: Session = Depends(get_db)
):
    fields = (
        db.query(FieldDefinition)
        .order_by(FieldDefinition.display_order)
        .all()
    )
    clean_data = validate_machine_data(payload.data, fields)

    machine = Machine(data=clean_data)
    db.add(machine)
    db.commit()
    db.refresh(machine)

    return {
        "message": "Machine created successfully.",
        "machine": machine_to_dict(machine),
    }


@app.put("/api/machines/{machine_id}")
def update_machine(
    machine_id: int,
    payload: MachinePayload,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found.")

    fields = (
        db.query(FieldDefinition)
        .order_by(FieldDefinition.display_order)
        .all()
    )
    clean_data = validate_machine_data(payload.data, fields)

    # Replace the JSON data with the values submitted by the edit form.
    # Missing optional fields are omitted and remain blank in the UI.
    machine.data = clean_data
    db.commit()
    db.refresh(machine)

    return {
        "message": "Machine updated successfully.",
        "machine": machine_to_dict(machine),
    }


@app.delete("/api/machines/{machine_id}")
def delete_machine(
    machine_id: int,
    db: Session = Depends(get_db)
):
    machine = db.query(Machine).filter(Machine.id == machine_id).first()

    if not machine:
        raise HTTPException(status_code=404, detail="Machine not found.")

    db.delete(machine)
    db.commit()

    return {"message": "Machine deleted successfully."}

@app.post("/api/machines/{machine_id}/predict")
def predict_machine(
    machine_id: int,
    db: Session = Depends(get_db),
):
    machine = db.query(Machine).filter(
        Machine.id == machine_id
    ).first()

    if not machine:
        raise HTTPException(
            status_code=404,
            detail="Machine not found.",
        )

    try:
        return predict_risk(machine.data or {})
    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc