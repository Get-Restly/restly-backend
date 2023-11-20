from datetime import datetime

from sqlalchemy import func
from sqlalchemy.orm import Mapped, mapped_column

from restly.db import db


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
    email: Mapped[str] = mapped_column(db.String, unique=True, nullable=False)


class Spec(TimestampMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    url: Mapped[str] = mapped_column(db.String, nullable=False)
    content: Mapped[str] = mapped_column(db.String, nullable=False)
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )


class Tutorial(TimestampMixin, db.Model):
    id: Mapped[int] = mapped_column(db.Integer, primary_key=True, autoincrement=True)
    query: Mapped[str] = mapped_column(db.String, nullable=False)
    relevant_apis: Mapped[str] = mapped_column(db.String, nullable=False)
    content: Mapped[str] = mapped_column(db.String, nullable=False, default="")
    spec_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("spec.id"), nullable=False
    )
    user_id: Mapped[int] = mapped_column(
        db.Integer, db.ForeignKey("user.id"), nullable=False
    )


def get_current_user() -> User:
    return User.query.first()
