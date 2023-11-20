from json import dumps, loads
from typing import Optional

import openai
from flask import Blueprint, jsonify
from flask_pydantic import validate
from pydantic import BaseModel

from ..db import db
from ..models import Spec, Tutorial, get_current_user
from ..prompts import GENERATE_TUTORIAL_PROMPT
from ..types import ApiEndpoint, ApiEndpointList, TutorialModel, TutorialLiteModel
from ..utils import SpecFormatter

tutorial_bp = Blueprint("tutorial", __name__)


class ListTutorialsResponse(BaseModel):
    tutorials: list[TutorialLiteModel]


@tutorial_bp.route("/api/v1/tutorials", methods=["GET"])
@validate()
def list_tutorials():
    user = get_current_user()
    tutorials = Tutorial.query.filter_by(user_id=user.id).all()
    models = [
        TutorialLiteModel(id=tutorial.id, name=tutorial.name) for tutorial in tutorials
    ]
    return ListTutorialsResponse(tutorials=models)


class GetTutorialResponse(BaseModel):
    tutorial: TutorialModel


@tutorial_bp.route("/api/v1/tutorials/<int:id>", methods=["GET"])
@validate()
def get_tutorial(id: int):
    user = get_current_user()
    tutorial = Tutorial.query.filter_by(id=id, user_id=user.id).first()
    if not tutorial:
        return jsonify({"error": "Tutorial not found"}), 404
    model = TutorialModel(
        id=tutorial.id,
        name=tutorial.name,
        content=tutorial.content,
        query=tutorial.input,
        relevant_apis=loads(tutorial.relevant_apis),
        spec_id=tutorial.spec_id,
    )

    return GetTutorialResponse(tutorial=model)


class CreateTutorialRequest(BaseModel):
    name: str


class CreateTutorialResponse(BaseModel):
    id: int


@tutorial_bp.route("/api/v1/tutorials", methods=["POST"])
@validate()
def create_tutorial(body: CreateTutorialRequest):
    user = get_current_user()
    tutorial = Tutorial(name=body.name, user_id=user.id)
    db.session.add(tutorial)
    db.session.commit()
    return CreateTutorialResponse(id=tutorial.id)


class GenerateTutorialRequest(BaseModel):
    spec_id: int
    query: str
    apis: list[ApiEndpoint]


class GenerateTutorialResponse(BaseModel):
    id: int
    content: str


@tutorial_bp.route("/api/v1/tutorials/<int:id>/generate-content", methods=["POST"])
@validate()
def generate_tutorial_content(id: int, body: GenerateTutorialRequest):
    user = get_current_user()
    spec: Optional[Spec] = Spec.query.filter_by(
        id=body.spec_id, user_id=user.id
    ).first()
    if not spec:
        return jsonify({"error": "Spec not found"}), 404

    tutorial = Tutorial.query.filter_by(id=id, user_id=user.id).first()
    if not tutorial:
        return jsonify({"error": "Tutorial not found"}), 404

    content = generate_content(loads(spec.content), body.query, body.apis)
    relevant_apis = ApiEndpointList(apis=body.apis).model_dump_json()

    tutorial.content = content
    tutorial.input = body.query
    tutorial.relevant_apis = relevant_apis
    tutorial.spec_id = spec.id

    db.session.add(tutorial)
    db.session.commit()

    return GenerateTutorialResponse(
        id=tutorial.id,
        content=content,
    )


class UpdateTutorialContentRequest(BaseModel):
    content: str


class UpdateTutorialContentResponse(BaseModel):
    id: int


@tutorial_bp.route("/api/v1/tutorials/<int:id>/content", methods=["PUT"])
@validate()
def update_tutorial_content(id: int, body: UpdateTutorialContentRequest):
    user = get_current_user()
    tutorial = Tutorial.query.filter_by(id=id, user_id=user.id).first()
    if not tutorial:
        return jsonify({"error": "Tutorial not found"}), 404

    tutorial.content = body.content

    db.session.add(tutorial)
    db.session.commit()

    return UpdateTutorialContentResponse(id=tutorial.id)


def generate_content(spec: dict, query: str, apis: list[ApiEndpoint]) -> str:
    trimmed_spec = SpecFormatter(spec).narrow_api_list(apis)
    trimmed_spec_str = dumps(trimmed_spec, indent=2)
    prompt = GENERATE_TUTORIAL_PROMPT.format(query=query, spec=trimmed_spec_str)
    client = openai.OpenAI()

    completion = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=[{"role": "user", "content": prompt}],
        temperature=0,
    )
    result = completion.choices[0].message.content
    return result
