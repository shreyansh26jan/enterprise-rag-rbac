from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.auth.business_authorization import (
    can_read_employees,
    can_read_projects,
    can_read_project_budgets,
    can_read_expenses,
)
from app.sql.business_queries import (
    count_employees,
    list_employees,
    list_projects,
    department_expense_total,
)


def get_employee_count(
    db: Session,
    username: str,
    department: str | None = None,
) -> int:
    if not can_read_employees(db, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access employee data.",
        )

    return count_employees(db, department)


def get_employees(
    db: Session,
    username: str,
    department: str | None = None,
) -> list[dict]:
    if not can_read_employees(db, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access employee data.",
        )

    return list_employees(db, department)


def get_projects(
    db: Session,
    username: str,
    department: str | None = None,
    project_status: str | None = None,
) -> list[dict]:
    if not can_read_projects(db, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access project data.",
        )

    return list_projects(
        db,
        department=department,
        status=project_status,
    )


def get_project_budgets(
    db: Session,
    username: str,
    department: str | None = None,
    project_status: str | None = None,
) -> list[dict]:
    if not can_read_project_budgets(db, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access project budgets.",
        )

    # return list_projects(
    #     db,
    #     department=department,
    #     status=project_status,
    # )
    return list_projects(
    db,
    department=department,
    status=project_status,
    include_budget=True,
)

def get_department_expense_total(
    db: Session,
    username: str,
    department: str,
) -> float:
    if not can_read_expenses(db, username):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access expense data.",
        )

    return department_expense_total(db, department)