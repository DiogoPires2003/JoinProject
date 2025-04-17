import os
from .models import Role
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