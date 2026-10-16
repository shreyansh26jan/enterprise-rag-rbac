import pytest
from fastapi import HTTPException

from app.sql.business_service import (
    get_employee_count,
    get_employees,
    get_projects,
    get_project_budgets,
    get_department_expense_total,
)
from app.db.database import SessionLocal
@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_admin_can_get_employee_count(db_session):
    assert get_employee_count(db_session, "admin") == 5


def test_employee_count_department_filter(db_session):
    assert get_employee_count(
        db_session,
        "admin",
        department="Engineering",
    ) == 3


def test_hr_manager_can_get_employees(db_session):
    employees = get_employees(db_session, "anjali")

    assert len(employees) == 5
    assert all("salary" not in employee for employee in employees)


def test_engineer_can_get_engineering_employees(db_session):
    employees = get_employees(
        db_session,
        "shreyansh",
        department="Engineering",
    )

    assert len(employees) == 3
    assert all(
        employee["department"] == "Engineering"
        for employee in employees
    )


def test_employee_cannot_get_employee_data(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_employees(db_session, "raj")

    assert exc_info.value.status_code == 403


def test_unknown_user_cannot_get_employee_count(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_employee_count(db_session, "unknown_user")

    assert exc_info.value.status_code == 403


def test_employee_can_get_projects(db_session):
    projects = get_projects(db_session, "raj")

    assert len(projects) == 3


def test_engineer_can_filter_projects(db_session):
    projects = get_projects(
        db_session,
        "shreyansh",
        department="Engineering",
        project_status="active",
    )

    assert len(projects) == 1
    assert projects[0]["name"] == "Enterprise RAG Platform"


def test_unknown_user_cannot_get_projects(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_projects(db_session, "unknown_user")

    assert exc_info.value.status_code == 403


def test_admin_can_get_project_budgets(db_session):
    projects = get_project_budgets(db_session, "admin")

    assert len(projects) == 3
    assert all("budget" in project for project in projects)


def test_hr_manager_cannot_get_project_budgets(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_project_budgets(db_session, "anjali")

    assert exc_info.value.status_code == 403


def test_engineer_cannot_get_project_budgets(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_project_budgets(db_session, "shreyansh")

    assert exc_info.value.status_code == 403


def test_employee_cannot_get_project_budgets(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_project_budgets(db_session, "raj")

    assert exc_info.value.status_code == 403


def test_admin_can_get_expense_total(db_session):
    total = get_department_expense_total(
        db_session,
        "admin",
        "Engineering",
    )

    assert total == 0.0


def test_hr_manager_cannot_get_expense_total(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_department_expense_total(
            db_session,
            "anjali",
            "Engineering",
        )

    assert exc_info.value.status_code == 403


def test_engineer_cannot_get_expense_total(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_department_expense_total(
            db_session,
            "shreyansh",
            "Engineering",
        )

    assert exc_info.value.status_code == 403


def test_employee_cannot_get_expense_total(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_department_expense_total(
            db_session,
            "raj",
            "Engineering",
        )

    assert exc_info.value.status_code == 403


def test_unknown_user_cannot_get_expense_total(db_session):
    with pytest.raises(HTTPException) as exc_info:
        get_department_expense_total(
            db_session,
            "unknown_user",
            "Engineering",
        )

    assert exc_info.value.status_code == 403

def test_regular_project_access_excludes_budgets(db_session):
    projects = get_projects(db_session, "raj")

    assert len(projects) == 3
    assert all("budget" not in project for project in projects)


def test_admin_budget_access_includes_budgets(db_session):
    projects = get_project_budgets(db_session, "admin")

    assert len(projects) == 3
    assert all("budget" in project for project in projects)