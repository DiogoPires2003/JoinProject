def create_default_roles():
    from .models import Role
    from django.db.utils import OperationalError, ProgrammingError

    try:
        Role.objects.get_or_create(
            name="Administrator",
            defaults={"description": "Role with full access to all administrator functionalities."}
        )

    except (OperationalError, ProgrammingError):
        pass

def create_super_employee():
    from .models import Employee, Role
    from django.contrib.auth.hashers import make_password
    from django.db.utils import OperationalError, ProgrammingError

    try:
        administrator_role, _ = Role.objects.get_or_create(
            name="Administrator",
            defaults={"description": "Role with full access to all administrator functionalities."}
        )

        Employee.objects.get_or_create(
            email="administrator@betterhealth.com",
            defaults={
                "first_name": "Super",
                "last_name": "Administrator",
                "role": administrator_role,
                "password": make_password("admin1234")  # Hashea la contraseña
            }
        )
    except (OperationalError, ProgrammingError):
        pass

