from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base


class FieldDefinition(Base):
    __tablename__ = "field_definitions"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    key: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True
    )

    field_type: Mapped[str] = mapped_column(
        String(20),
        nullable=False
    )

    required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False
    )

    options: Mapped[list | None] = mapped_column(
        JSON,
        nullable=True
    )

    display_order: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )


class Machine(Base):
    __tablename__ = "machines"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    data: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=dict
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False
    )