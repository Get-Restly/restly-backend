from json import dumps, loads

import openai
from flask import Blueprint
from flask import jsonify
from flask_pydantic import validate
from pydantic import BaseModel

from ..db import db
from ..models import Spec, Tutorial, get_current_user
from ..prompts import GENERATE_TUTORIAL_PROMPT
from ..types import ApiEndpoint, ApiEndpointList
from ..utils import SpecFormatter

tutorial_bp = Blueprint("tutorial", __name__)


class CreateTutorialRequest(BaseModel):
    spec_id: int
    query: str
    apis: list[ApiEndpoint]


class CreateTutorialResponse(BaseModel):
    id: int
    tutorial: str


@tutorial_bp.route("/api/v1/tutorial", methods=["POST"])
@validate()
def create_tutorial(body: CreateTutorialRequest):
    user = get_current_user()
    spec = Spec.query.filter_by(id=body.spec_id, user_id=user.id).first()
    if not spec:
        return jsonify({"error": "Spec not found"}), 404

    content = generate_content(loads(spec.content), body.query, body.apis)
    relevant_apis = ApiEndpointList(apis=body.apis).model_dump_json()

    tutorial = Tutorial(
        spec_id=spec.id,
        query=body.query,
        content=content,
        relevant_apis=relevant_apis,
        user_id=user.id,
    )

    db.session.add(tutorial)
    db.session.commit()

    return CreateTutorialResponse(
        id=tutorial.id,
        tutorial=content,
    )


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
