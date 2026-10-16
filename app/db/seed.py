from app.db.database import SessionLocal
from app.models.rbac import (
    User,
    Role,
    Permission,
    Document,
)
from app.models.business import (
    Employee,
    Project,
    Expense,
)

def seed_database():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Create permissions
        # -------------------------------------------------

        # permission_names = [
        #     "document:read",
        #     "document:search",
        #     "document:upload",
        #     "document:delete",
        #     "document:manage_access",
        # ]
        permission_names = [
            # Document permissions
            "document:read",
            "document:search",
            "document:upload",
            "document:delete",
            "document:manage_access",

            # Business-data permissions
            "business:employee:read",
            "business:project:read",
            "business:project:budget",
            "business:expense:read",
        ]
        permissions = {}

        for name in permission_names:
            permission = (
                db.query(Permission)
                .filter(Permission.name == name)
                .first()
            )

            if not permission:
                permission = Permission(name=name)
                db.add(permission)

            permissions[name] = permission

        db.flush()

        # -------------------------------------------------
        # 2. Create roles
        # -------------------------------------------------

        role_names = [
            "admin",
            "hr_manager",
            "engineer",
            "employee",
        ]

        roles = {}

        for name in role_names:
            role = (
                db.query(Role)
                .filter(Role.name == name)
                .first()
            )

            if not role:
                role = Role(name=name)
                db.add(role)

            roles[name] = role

        db.flush()

        # -------------------------------------------------
        # 3. Assign permissions to roles
        # -------------------------------------------------

        roles["admin"].permissions = list(permissions.values())

        # roles["hr_manager"].permissions = [
        #     permissions["document:read"],
        #     permissions["document:search"],
        #     permissions["document:upload"],
        # ]
        roles["hr_manager"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
            permissions["document:upload"],
            permissions["business:employee:read"],
            permissions["business:project:read"],
        ]

        # roles["engineer"].permissions = [
        #     permissions["document:read"],
        #     permissions["document:search"],
        # ]
        roles["engineer"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
            permissions["business:employee:read"],
            permissions["business:project:read"],
        ]

        # roles["employee"].permissions = [
        #     permissions["document:read"],
        #     permissions["document:search"],
        # ]
        roles["employee"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
            permissions["business:project:read"],
        ]
        # -------------------------------------------------
        # 4. Create users
        # -------------------------------------------------

        users_data = [
            ("anjali", "anjali@company.com", "hr_manager"),
            ("shreyansh", "shreyansh@company.com", "engineer"),
            ("raj", "raj@company.com", "employee"),
            ("admin", "admin@company.com", "admin"),
        ]

        users = {}

        for username, email, role_name in users_data:

            user = (
                db.query(User)
                .filter(User.username == username)
                .first()
            )

            if not user:
                user = User(
                    username=username,
                    email=email,
                    is_active=True,
                )
                db.add(user)

            user.roles = [roles[role_name]]
            users[username] = user

        db.flush()

        # -------------------------------------------------
        # 5. Create documents
        # -------------------------------------------------

        documents_data = [
            (
                "HR Policy",
                "pdf",
                "confidential",
                ["hr_manager", "admin"],
            ),
            (
                "Engineering Architecture",
                "pdf",
                "internal",
                ["engineer", "admin"],
            ),
            (
                "Company Handbook",
                "pdf",
                "public",
                ["employee", "engineer", "hr_manager", "admin"],
            ),
        ]

        for name, source, classification, role_names in documents_data:

            document = (
                db.query(Document)
                .filter(Document.name == name)
                .first()
            )

            if not document:
                document = Document(
                    name=name,
                    source=source,
                    classification=classification,
                )
                db.add(document)

            document.roles = [
                roles[role_name]
                for role_name in role_names
            ]

                # -------------------------------------------------
        # 6. Create business data
        # -------------------------------------------------

        employees_data = [
            (
                "Aarav Sharma",
                "Engineering",
                "Software Engineer",
                "Bangalore",
                1200000.0,
                True,
            ),
            (
                "Priya Mehta",
                "Engineering",
                "Senior Software Engineer",
                "Bangalore",
                1800000.0,
                True,
            ),
            (
                "Rahul Verma",
                "Human Resources",
                "HR Manager",
                "Delhi",
                1500000.0,
                True,
            ),
            (
                "Neha Singh",
                "Finance",
                "Financial Analyst",
                "Mumbai",
                1100000.0,
                True,
            ),
            (
                "Vikram Rao",
                "Engineering",
                "Engineering Manager",
                "Hyderabad",
                2200000.0,
                True,
            ),
        ]

        for (
            name,
            department,
            role,
            location,
            salary,
            is_active,
        ) in employees_data:

            employee = (
                db.query(Employee)
                .filter(Employee.name == name)
                .first()
            )

            if not employee:
                employee = Employee(
                    name=name,
                    department=department,
                    role=role,
                    location=location,
                    salary=salary,
                    is_active=is_active,
                )
                db.add(employee)

        db.flush()

        # -------------------------------------------------
        # 7. Create projects
        # -------------------------------------------------

        projects_data = [
            (
                "Enterprise RAG Platform",
                "Engineering",
                "active",
                5000000.0,
            ),
            (
                "HR Automation System",
                "Human Resources",
                "active",
                2000000.0,
            ),
            (
                "Financial Analytics Platform",
                "Finance",
                "completed",
                3500000.0,
            ),
        ]

        for name, department, status, budget in projects_data:

            project = (
                db.query(Project)
                .filter(Project.name == name)
                .first()
            )

            if not project:
                project = Project(
                    name=name,
                    department=department,
                    status=status,
                    budget=budget,
                )
                db.add(project)

        db.flush()

        db.commit()

        print("Database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()