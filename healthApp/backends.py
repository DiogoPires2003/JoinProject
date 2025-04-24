from django.contrib.auth.backends import BaseBackend
from .models import Patient

class PatientAuthBackend(BaseBackend):
    def authenticate(self, request, username=None, password=None):
        try:
            patient = Patient.objects.get(email=username)
            if patient.password == password:  # Note: This is not secure, we'll fix it later
                return patient
        except Patient.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return Patient.objects.get(pk=user_id)
        except Patient.DoesNotExist:
            return None