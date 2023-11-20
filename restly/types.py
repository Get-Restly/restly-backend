from pydantic import BaseModel


class ApiEndpoint(BaseModel):
    path: str
    verb: str


class ApiEndpointList(BaseModel):
    apis: list[ApiEndpoint]
