from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.domain.projects import ProductionState


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateProjectRequest(StrictModel):
    name: str = Field(min_length=1, max_length=200)


class TransferOwnershipRequest(StrictModel):
    target_principal_id: UUID
    expected_version: int = Field(ge=1)


class ProjectVersionRequest(StrictModel):
    expected_version: int = Field(ge=1)


class ProjectResponse(StrictModel):
    project_id: UUID
    workspace_id: UUID
    identity_id: UUID
    context_id: UUID
    owner_principal_id: UUID
    name: str
    lifecycle: Literal["active", "archived"]
    version: int


class CreateProductionRequest(StrictModel):
    name: str = Field(min_length=1, max_length=200)


class TransitionProductionRequest(StrictModel):
    target_state: ProductionState
    expected_version: int = Field(ge=1)


class ProductionResponse(StrictModel):
    production_id: UUID
    workspace_id: UUID
    project_id: UUID
    name: str
    state: ProductionState
    version: int
