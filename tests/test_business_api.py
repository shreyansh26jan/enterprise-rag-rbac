
from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient

from app.db.database import SessionLocal, get_db
from app.main import app
from app.security.authentication import create_access_token


BASE_URL = "/api/v1/business"


def auth_headers(username: str) -> dict[str, str]:
    token = create_access_token(username)
    return {"Authorization": f"Bearer {token}"}


def override_get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def client() -> Generator:
    previous_override = app.dependency_overrides.get(get_db)
    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        if previous_override is None:
            app.dependency_overrides.pop(get_db, None)
        else:
            app.dependency_overrides[get_db] = previous_override


# --------------------------------------------------
# Authentication
# --------------------------------------------------

def test_business_employees_requires_authentication(client):
    response = client.get(f"{BASE_URL}/employees")

    assert response.status_code == 401


def test_business_projects_rejects_invalid_token(client):
    response = client.get(
        f"{BASE_URL}/projects",
        headers={"Authorization": "Bearer invalid-token"},
    )

    assert response.status_code == 401


# --------------------------------------------------
# Employee endpoints
# --------------------------------------------------

def test_admin_can_get_employee_count(client):
    response = client.get(
        f"{BASE_URL}/employees/count",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert response.json()["count"] == 5


def test_engineer_can_filter_employee_count(client):
    response = client.get(
        f"{BASE_URL}/employees/count?department=Engineering",
        headers=auth_headers("shreyansh"),
    )

    assert response.status_code == 200
    assert response.json()["count"] == 3


def test_hr_manager_can_list_employees(client):
    response = client.get(
        f"{BASE_URL}/employees",
        headers=auth_headers("anjali"),
    )

    assert response.status_code == 200
    assert len(response.json()) == 5


def test_employee_response_never_exposes_salary(client):
    response = client.get(
        f"{BASE_URL}/employees",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert all("salary" not in employee for employee in response.json())


def test_employee_cannot_access_employee_directory(client):
    response = client.get(
        f"{BASE_URL}/employees",
        headers=auth_headers("raj"),
    )

    assert response.status_code == 403


def test_unknown_user_cannot_access_employee_directory(client):
    response = client.get(
        f"{BASE_URL}/employees",
        headers=auth_headers("unknown_user"),
    )

    assert response.status_code == 403


# --------------------------------------------------
# Project endpoints
# --------------------------------------------------

def test_employee_can_list_projects(client):
    response = client.get(
        f"{BASE_URL}/projects",
        headers=auth_headers("raj"),
    )

    assert response.status_code == 200
    assert len(response.json()) == 3


def test_project_response_never_exposes_budget(client):
    response = client.get(
        f"{BASE_URL}/projects",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert all("budget" not in project for project in response.json())


def test_engineer_can_filter_projects(client):
    response = client.get(
        f"{BASE_URL}/projects?department=Engineering&status=active",
        headers=auth_headers("shreyansh"),
    )

    assert response.status_code == 200
    projects = response.json()

    assert len(projects) == 1
    assert projects[0]["name"] == "Enterprise RAG Platform"
    assert "budget" not in projects[0]


def test_admin_can_read_project_budgets(client):
    response = client.get(
        f"{BASE_URL}/projects/budgets",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    projects = response.json()

    assert len(projects) == 3
    assert all("budget" in project for project in projects)


@pytest.mark.parametrize("username", ["anjali", "shreyansh", "raj"])
def test_non_admin_roles_cannot_read_project_budgets(client, username):
    response = client.get(
        f"{BASE_URL}/projects/budgets",
        headers=auth_headers(username),
    )

    assert response.status_code == 403


# --------------------------------------------------
# Expense endpoint
# --------------------------------------------------

def test_admin_can_read_expense_total(client):
    response = client.get(
        f"{BASE_URL}/expenses/total?department=Engineering",
        headers=auth_headers("admin"),
    )

    assert response.status_code == 200
    assert response.json() == {
        "department": "Engineering",
        "total": 0.0,
    }


@pytest.mark.parametrize(
    "username",
    ["anjali", "shreyansh", "raj", "unknown_user"],
)
def test_unauthorized_users_cannot_read_expenses(client, username):
    response = client.get(
        f"{BASE_URL}/expenses/total?department=Engineering",
        headers=auth_headers(username),
    )

    assert response.status_code == 403
