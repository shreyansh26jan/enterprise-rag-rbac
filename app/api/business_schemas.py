
from pydantic import BaseModel, ConfigDict, Field


class EmployeeResponse(BaseModel):
    id: int
    name: str
    department: str
    role: str
    location: str

    model_config = ConfigDict(from_attributes=True)


class EmployeeCountResponse(BaseModel):
    count: int


class ProjectResponse(BaseModel):
    id: int
    name: str
    department: str
    status: str


class ProjectBudgetResponse(ProjectResponse):
    budget: float


class ExpenseTotalResponse(BaseModel):
    department: str
    total: float


class ErrorResponse(BaseModel):
    detail: str
