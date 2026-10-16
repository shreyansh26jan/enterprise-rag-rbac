
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.business_schemas import (
    EmployeeCountResponse,
    EmployeeResponse,
    ProjectResponse,
    ProjectBudgetResponse,
    ExpenseTotalResponse,
)
from app.db.database import get_db
from app.security.dependencies import get_current_username
from app.sql.business_service import (
    get_employee_count,
    get_employees,
    get_projects,
    get_project_budgets,
    get_department_expense_total,
)


router = APIRouter(
    prefix="/api/v1/business",
    tags=["Business Data"],
)


@router.get(
    "/employees/count",
    response_model=EmployeeCountResponse,
)
def employee_count(
    department: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    count = get_employee_count(
        db,
        username,
        department=department,
    )
    return {"count": count}


@router.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def employees(
    department: str | None = Query(default=None, min_length=1),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    return get_employees(
        db,
        username,
        department=department,
    )


@router.get(
    "/projects",
    response_model=list[ProjectResponse],
)
def projects(
    department: str | None = Query(default=None, min_length=1),
    project_status: str | None = Query(
        default=None,
        alias="status",
        min_length=1,
    ),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    return get_projects(
        db,
        username,
        department=department,
        project_status=project_status,
    )


@router.get(
    "/projects/budgets",
    response_model=list[ProjectBudgetResponse],
)
def project_budgets(
    department: str | None = Query(default=None, min_length=1),
    project_status: str | None = Query(
        default=None,
        alias="status",
        min_length=1,
    ),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    return get_project_budgets(
        db,
        username,
        department=department,
        project_status=project_status,
    )


@router.get(
    "/expenses/total",
    response_model=ExpenseTotalResponse,
)
def expense_total(
    department: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
    username: str = Depends(get_current_username),
):
    total = get_department_expense_total(
        db,
        username,
        department.strip(),
    )
    return {
        "department": department.strip(),
        "total": total,
    }
