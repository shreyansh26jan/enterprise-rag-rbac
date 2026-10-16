from app.auth.business_authorization import (
    can_read_employees,
    can_read_projects,
    can_read_project_budgets,
    can_read_expenses,
)
from app.db.database import SessionLocal

def test_admin_can_read_all_business_data():
    db_session = SessionLocal()
    try:
        assert can_read_employees(db_session, "admin")
        assert can_read_projects(db_session, "admin")
        assert can_read_project_budgets(db_session, "admin")
        assert can_read_expenses(db_session, "admin")
        
    finally:
        db_session.close()
    

def test_hr_manager_business_permissions():
    db_session = SessionLocal()
    try:
        assert can_read_employees(db_session, "anjali")
        assert can_read_projects(db_session, "anjali")
        assert not can_read_project_budgets(db_session, "anjali")
        assert not can_read_expenses(db_session, "anjali")
    finally:
            db_session.close()
        

def test_engineer_business_permissions():
    db_session = SessionLocal()
    try:
        assert can_read_employees(db_session, "shreyansh")
        assert can_read_projects(db_session, "shreyansh")
        assert not can_read_project_budgets(db_session, "shreyansh")
        assert not can_read_expenses(db_session, "shreyansh")
    finally:
            db_session.close()
        

def test_employee_business_permissions():
    db_session = SessionLocal()
    try:
        assert not can_read_employees(db_session, "raj")
        assert can_read_projects(db_session, "raj")
        assert not can_read_project_budgets(db_session, "raj")
        assert not can_read_expenses(db_session, "raj")
    finally:
            db_session.close()
        

def test_unknown_user_has_no_business_permissions():
    db_session = SessionLocal()
    try:
        assert not can_read_employees(db_session, "unknown_user")
        assert not can_read_projects(db_session, "unknown_user")
        assert not can_read_project_budgets(db_session, "unknown_user")
        assert not can_read_expenses(db_session, "unknown_user")
    finally:
            db_session.close()
            