from sqlalchemy.orm import Session

from app.auth.authorization import user_has_permission


BUSINESS_EMPLOYEE_READ = "business:employee:read"
BUSINESS_PROJECT_READ = "business:project:read"
BUSINESS_PROJECT_BUDGET = "business:project:budget"
BUSINESS_EXPENSE_READ = "business:expense:read"


def can_read_employees(
    db: Session,
    username: str,
) -> bool:
    return user_has_permission(
        db,
        username,
        BUSINESS_EMPLOYEE_READ,
    )


def can_read_projects(
    db: Session,
    username: str,
) -> bool:
    return user_has_permission(
        db,
        username,
        BUSINESS_PROJECT_READ,
    )


def can_read_project_budgets(
    db: Session,
    username: str,
) -> bool:
    return user_has_permission(
        db,
        username,
        BUSINESS_PROJECT_BUDGET,
    )


def can_read_expenses(
    db: Session,
    username: str,
) -> bool:
    return user_has_permission(
        db,
        username,
        BUSINESS_EXPENSE_READ,
    )