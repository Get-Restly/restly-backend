from datetime import datetime
from uuid import uuid4

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from restly.db import db


def generate_user_token() -> str:
    return uuid4().hex


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        db.DateTime, nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        db.DateTime,
        nullable=False,
        server_default=func.now(),
        server_onupdate=func.now(),
    )


class User(TimestampMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=True)
    token: Mapped[str] = mapped_column(
        db.String, nullable=False, default=lambda: generate_user_token(), unique=True
    )


class Spec(TimestampMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String, nullable=False)
    url: Mapped[str] = mapped_column(db.String, nullable=False)
    content: Mapped[str] = mapped_column(db.String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )


class Tutorial(TimestampMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(db.String, nullable=False)
    input: Mapped[str] = mapped_column(db.String, nullable=False, default="")
    relevant_apis: Mapped[str] = mapped_column(db.String, nullable=False, default="")
    content: Mapped[str] = mapped_column(db.String, nullable=False, default="")
    spec_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("spec.id"), nullable=True
    )
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )
    server: Mapped[str] = mapped_column(db.String, nullable=True, default=None)
