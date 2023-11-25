from flask import Blueprint
from flask_pydantic import validate
from pydantic import BaseModel
from typing import Optional

from ..db import db
from ..models import User

user_bp = Blueprint("user", __name__)

class CreateUserRequest(BaseModel):
    email: Optional[str]

class CreateUserResponse(BaseModel):
    token: str

@user_bp.route("/api/v1/users", methods=["POST"])
@validate()
def create_user(body: CreateUserRequest):
    user = User(email=body.email)
    db.session.add(user)
    db.session.commit()
    return CreateUserResponse(token=user.token)
