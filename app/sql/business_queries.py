from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.business import Employee, Expense, Project

# Function	                                    Purpose
# count_employees()	                            Count active employees, optionally filtered by department
# list_employees()                          	List employee details without exposing salary
# list_projects()                           	List projects, optionally filtered by department or status
# department_expense_total()                	Calculate expenses for a department

def count_employees(
    db: Session,
    department: str | None = None,
) -> int:
    """
    Return the number of active employees.

    If department is provided, restrict the count
    to that department.
    """

    statement = select(
        func.count(Employee.id)
    ).where(
        Employee.is_active.is_(True)
    )

    if department:
        statement = statement.where(
            Employee.department == department
        )

    return db.scalar(statement) or 0


def list_employees(
    db: Session,
    department: str | None = None,
) -> list[dict]:
    """
    Return active employees, optionally filtered
    by department.
    """

    statement = (
        select(
            Employee.id,
            Employee.name,
            Employee.department,
            Employee.role,
            Employee.location,
        )
        .where(Employee.is_active.is_(True))
        .order_by(Employee.id)
    )

    if department:
        statement = statement.where(
            Employee.department == department
        )

    rows = db.execute(statement).mappings().all()

    return [dict(row) for row in rows]


def list_projects(
    db: Session,
    department: str | None = None,
    status: str | None = None,
    include_budget: bool = False,
) -> list[dict]:
    """
    Return projects with optional department and
    status filters.
    """

    # statement = (
    #     select(
    #         Project.id,
    #         Project.name,
    #         Project.department,
    #         Project.status,
    #         Project.budget,
    #     )
    #     .order_by(Project.id)
    # )
    columns = [
        Project.id,
        Project.name,
        Project.department,
        Project.status,
    ]

    if include_budget:
        columns.append(Project.budget)

    statement = select(*columns).order_by(Project.id)


    if include_budget:
        columns.append(Project.budget)

    if department:
        statement = statement.where(
            Project.department == department
        )

    if status:
        statement = statement.where(
            Project.status == status
        )

    rows = db.execute(statement).mappings().all()

    return [dict(row) for row in rows]


def department_expense_total(
    db: Session,
    department: str,
) -> float:
    """
    Return total expenses for employees belonging
    to the specified department.
    """

    statement = (
        select(
            func.coalesce(
                func.sum(Expense.amount),
                0,
            )
        )
        .select_from(Expense)
        .join(
            Employee,
            Expense.employee_id == Employee.id,
        )
        .where(
            Employee.department == department
        )
    )

    return float(db.scalar(statement) or 0)