from pydantic import BaseModel, ConfigDict


class ProblemDetails(BaseModel):
    model_config = ConfigDict(extra="forbid")

    type: str
    title: str
    status: int
    detail: str
    instance: str | None = None
    code: str
    trace_id: str | None = None
