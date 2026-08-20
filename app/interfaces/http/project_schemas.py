from datetime import datetime
from typing import Any, Self
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.domain.projects import Production, Project


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class ProjectResponse(StrictModel):
    project_id: UUID
    workspace_id: UUID
    name: str
    description: str
    status: str
    owner_id: UUID
    member_ids: tuple[UUID, ...]
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_domain(cls, project: Project) -> Self:
        return cls(**{field: getattr(project, field) for field in cls.model_fields})


class ProjectListResponse(StrictModel):
    items: tuple[ProjectResponse, ...]
    limit: int
    offset: int


class ProjectMutationResponse(StrictModel):
    project: ProjectResponse
    change_summary: dict[str, Any] = Field(default_factory=dict)


class CreateProjectRequest(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    description: str = Field(default="", max_length=4000)


class UpdateProjectRequest(StrictModel):
    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    description: str | None = Field(default=None, max_length=4000)
    status: str | None = Field(default=None, pattern="^(active|archived)$")

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if self.name is None and self.description is None and self.status is None:
            raise ValueError("At least one project field is required.")
        return self


class SetProjectMemberRequest(StrictModel):
    role: str = Field(pattern="^(Admin|Editor|Viewer)$")
    expected_version: int = Field(ge=1)


class RemoveProjectMemberRequest(StrictModel):
    expected_version: int = Field(ge=1)


class ProductionResponse(StrictModel):
    production_id: UUID
    project_id: UUID
    workspace_id: UUID
    name: str
    production_type: str
    status: str
    owner_id: UUID
    created_at: datetime
    updated_at: datetime
    version: int

    @classmethod
    def from_domain(cls, production: Production) -> Self:
        return cls(**{field: getattr(production, field) for field in cls.model_fields})


class ProductionListResponse(StrictModel):
    items: tuple[ProductionResponse, ...]
    limit: int
    offset: int


class ProductionMutationResponse(StrictModel):
    production: ProductionResponse
    change_summary: dict[str, Any] = Field(default_factory=dict)


class CreateProductionRequest(StrictModel):
    name: str = Field(min_length=1, max_length=160)
    production_type: str = Field(
        pattern=(
            "^(Feature Film|Short Film|TV|Commercial|Music Video|Social|"
            "Animation|Documentary|Custom)$"
        )
    )


class UpdateProductionRequest(StrictModel):
    expected_version: int = Field(ge=1)
    name: str | None = Field(default=None, min_length=1, max_length=160)
    status: str | None = Field(
        default=None,
        pattern=("^(draft|pre-production|production|post-production|completed|archived)$"),
    )

    @model_validator(mode="after")
    def require_update(self) -> Self:
        if self.name is None and self.status is None:
            raise ValueError("At least one production field is required.")
        return self
