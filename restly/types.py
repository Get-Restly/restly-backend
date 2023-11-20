from pydantic import BaseModel


class ApiEndpoint(BaseModel):
    path: str
    verb: str


class ApiEndpointList(BaseModel):
    apis: list[ApiEndpoint]


class SpecLiteModel(BaseModel):
    id: int
    name: str


class SpecModel(BaseModel):
    id: int
    name: str
    url: str
    content: str


class TutorialLiteModel(BaseModel):
    id: int
    name: str


class TutorialModel(BaseModel):
    id: int
    name: str
    query: str
    relevant_apis: ApiEndpointList
    content: str
    spec_id: int
