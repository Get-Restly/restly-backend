from json import dumps, loads
from typing import Optional

import openai
import requests
from flask import Blueprint, Flask, jsonify
from flask_pydantic import validate
from pydantic import BaseModel

from ..db import db
from ..models import Spec, get_current_user
from ..prompts import RELEVANT_APIS_PROMPT
from ..types import ApiEndpoint
from ..utils import SpecFormatter

spec_bp = Blueprint("spec", __name__)


class CreateSpecRequest(BaseModel):
    url: str


class CreateSpecResponse(BaseModel):
    id: int
    spec: dict  # TODO: define spec model https://swagger.io/specification/


@spec_bp.route("/api/v1/spec", methods=["POST"])
@validate()
def create_spec(body: CreateSpecRequest):
    content = requests.get(body.url).json()
    user = get_current_user()

    spec = Spec(
        url=body.url,
        content=dumps(content),
        user_id=user.id,
    )

    db.session.add(spec)
    db.session.commit()

    return CreateSpecResponse(
        id=spec.id,
        spec=content,
    )


class RelevantApisRequest(BaseModel):
    query: str
    count: int


class RelevantApisResponse(BaseModel):
    apis: list[ApiEndpoint]


@spec_bp.route("/api/v1/spec/<int:id>/relevant-apis", methods=["POST"])
@validate()
def relevant_apis(id, body: RelevantApisRequest):
    spec: Optional[Spec] = Spec.query.get(id)
    if not spec:
        jsonify({"error": "Spec not found"}), 404

    spec_content = loads(spec.content)
    trimmed_spec = SpecFormatter(spec_content).trim_paths_only()
    trimmed_spec_str = dumps(trimmed_spec)

    prompt = RELEVANT_APIS_PROMPT.format(query=body.query, spec=trimmed_spec_str)
    client = openai.OpenAI()
    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    resp = loads(completion.choices[0].message.content)
    return RelevantApisResponse(**resp)
