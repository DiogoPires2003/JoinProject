import os
from django.contrib.auth.hashers import make_password
from .models import Employee, Role
from dotenv import load_dotenv

load_dotenv()

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
    administrator_email = os.environ.get("ADMINISTRATOR_EMAIL")
    administrator_password = os.environ.get("ADMINISTRATOR_PASSWORD")

    # Asegúrate de que el rol "Administrator" existe
    administrator_role, _ = Role.objects.get_or_create(
        name="Administrator",
        defaults={"description": "Administrador del sistema"}
    )

    # Crea el empleado administrador si no existe
    Employee.objects.get_or_create(
        email=administrator_email,
        defaults={
            "first_name": "Super",
            "last_name": "Administrator",
            "role": administrator_role,
            "password": make_password(administrator_password)
        }
    )
