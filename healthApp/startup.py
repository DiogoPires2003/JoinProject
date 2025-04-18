import os
from django.db.utils import OperationalError, ProgrammingError
from dotenv import load_dotenv
from .models import Role

load_dotenv()

def create_default_roles():
    try:
        Role.objects.get_or_create(
            name="Administrator",
            defaults={"description": "Role with full access to all administrator functionalities."}
        )
    except (OperationalError, ProgrammingError):
        pass