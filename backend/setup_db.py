from backend.database import Base, SessionLocal, engine
from backend.models import FieldDefinition


DEFAULT_FIELDS = [
    {
        "name": "Machine Name",
        "key": "machine_name",
        "field_type": "text",
        "required": True,
        "options": None,
        "display_order": 1,
    },
    {
        "name": "Temperature",
        "key": "temperature",
        "field_type": "number",
        "required": True,
        "options": None,
        "display_order": 2,
    },
    {
        "name": "Pressure",
        "key": "pressure",
        "field_type": "number",
        "required": True,
        "options": None,
        "display_order": 3,
    },
    {
        "name": "Vibration",
        "key": "vibration",
        "field_type": "dropdown",
        "required": True,
        "options": ["Low", "Medium", "High"],
        "display_order": 4,
    },
]


def setup_database():
    print("Creating database tables...")

    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        existing_fields = db.query(FieldDefinition).count()

        if existing_fields == 0:
            print("Adding default field definitions...")

            for field_data in DEFAULT_FIELDS:
                field = FieldDefinition(**field_data)
                db.add(field)

            db.commit()

            print("Default fields added successfully.")

        else:
            print(
                f"Database already contains "
                f"{existing_fields} field definitions."
            )

    finally:
        db.close()

    print("Database setup complete.")


if __name__ == "__main__":
    setup_database()