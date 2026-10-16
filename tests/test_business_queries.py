
import pytest

from app.db.database import SessionLocal
from app.models.business import Employee, Expense
from app.sql.business_queries import (
    count_employees,
    department_expense_total,
    list_employees,
    list_projects,
)


@pytest.fixture
def db():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


def test_count_active_employees(db):
    assert count_employees(db) == 5


def test_count_employees_by_department(db):
    assert count_employees(db, department="Engineering") == 3


def test_count_employees_unknown_department(db):
    assert count_employees(db, department="Legal") == 0


def test_list_employees_excludes_salary(db):
    employees = list_employees(db)

    assert len(employees) == 5
    assert all("salary" not in employee for employee in employees)


def test_list_employees_by_department(db):
    employees = list_employees(db, department="Finance")

    assert len(employees) == 1
    assert employees[0]["name"] == "Neha Singh"
    assert employees[0]["department"] == "Finance"


def test_list_employees_unknown_department(db):
    assert list_employees(db, department="Legal") == []


def test_list_projects(db):
    projects = list_projects(db)

    assert len(projects) == 3
    assert {project["name"] for project in projects} == {
        "Enterprise RAG Platform",
        "HR Automation System",
        "Financial Analytics Platform",
    }


def test_list_projects_by_department_and_status(db):
    projects = list_projects(
        db,
        department="Engineering",
        status="active",
    )

    assert len(projects) == 1
    assert projects[0]["name"] == "Enterprise RAG Platform"


def test_list_projects_unknown_status(db):
    assert list_projects(db, status="cancelled") == []


def test_department_expense_total(db):
    employee = db.query(Employee).filter_by(
        name="Aarav Sharma"
    ).one()

    db.add_all([
        Expense(
            employee_id=employee.id,
            category="Travel",
            amount=1200.0,
            expense_date="2026-10-01",
        ),
        Expense(
            employee_id=employee.id,
            category="Meals",
            amount=300.0,
            expense_date="2026-10-02",
        ),
    ])
    db.flush()

    assert department_expense_total(db, "Engineering") == pytest.approx(1500.0)


def test_department_expense_total_without_expenses(db):
    assert department_expense_total(db, "Finance") == 0.0
