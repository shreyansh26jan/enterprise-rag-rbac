from pydantic import BaseModel, Field, field_validator


class DocumentRoleAssignmentRequest(BaseModel):
    role_name: str = Field(..., min_length=1, max_length=100)

    @field_validator("role_name")
    @classmethod
    def validate_role_name(cls, value: str) -> str:
        value = value.strip()

        if not value:
            raise ValueError("Role name cannot be empty or whitespace.")

        return value


class DocumentRoleAssignmentResponse(BaseModel):
    document_id: int
    document_name: str
    role_name: str
    assigned: bool
