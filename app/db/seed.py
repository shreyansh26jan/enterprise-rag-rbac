from app.db.database import SessionLocal
from app.models.rbac import (
    User,
    Role,
    Permission,
    Document,
)


def seed_database():
    db = SessionLocal()

    try:
        # -------------------------------------------------
        # 1. Create permissions
        # -------------------------------------------------

        permission_names = [
            "document:read",
            "document:search",
            "document:upload",
            "document:delete",
            "document:manage_access",
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

        roles["hr_manager"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
            permissions["document:upload"],
        ]

        roles["engineer"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
        ]

        roles["employee"].permissions = [
            permissions["document:read"],
            permissions["document:search"],
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

        db.commit()

        print("Database seeded successfully.")

    except Exception:
        db.rollback()
        raise

    finally:
        db.close()


if __name__ == "__main__":
    seed_database()