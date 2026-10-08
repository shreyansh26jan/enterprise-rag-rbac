from app.auth.authorization import (
    user_can_access_document,
    user_has_permission,
)
from app.db.database import SessionLocal


def test_hr_manager_can_access_hr_policy():
    db = SessionLocal()

    try:
        assert user_can_access_document(
            db,
            "anjali",
            "HR Policy",
        ) is True

    finally:
        db.close()


def test_engineer_cannot_access_hr_policy():
    db = SessionLocal()

    try:
        assert user_can_access_document(
            db,
            "shreyansh",
            "HR Policy",
        ) is False

    finally:
        db.close()


def test_engineer_can_access_engineering_document():
    db = SessionLocal()

    try:
        assert user_can_access_document(
            db,
            "shreyansh",
            "Engineering Architecture",
        ) is True

    finally:
        db.close()


def test_employee_can_access_public_document():
    db = SessionLocal()

    try:
        assert user_can_access_document(
            db,
            "raj",
            "Company Handbook",
        ) is True

    finally:
        db.close()


def test_hr_manager_has_search_permission():
    db = SessionLocal()

    try:
        assert user_has_permission(
            db,
            "anjali",
            "document:search",
        ) is True

    finally:
        db.close()


def test_employee_cannot_delete_documents():
    db = SessionLocal()

    try:
        assert user_has_permission(
            db,
            "raj",
            "document:delete",
        ) is False

    finally:
        db.close()