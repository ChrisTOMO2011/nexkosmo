from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class CreateCharacterRequest(StrictModel):
    display_name: str = Field(min_length=1, max_length=160)
    role_label: str | None = Field(default=None, max_length=160)


class UpdateCharacterRequest(StrictModel):
    expected_version: int = Field(ge=1)
    display_name: str | None = Field(default=None, min_length=1, max_length=160)
    role_label: str | None = Field(default=None, max_length=160)

    @model_validator(mode="after")
    def require_metadata_change(self) -> "UpdateCharacterRequest":
        if not {"display_name", "role_label"}.intersection(self.model_fields_set):
            raise ValueError("At least one Character metadata field is required.")
        return self


class CharacterResponse(StrictModel):
    character_id: UUID
    workspace_id: UUID
    project_id: UUID
    identity_id: UUID
    created_by_principal_id: UUID
    display_name: str
    role_label: str | None
    version: int
    created_at: datetime
    updated_at: datetime
