from django.db import models

class Patient(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    dni = models.CharField(max_length=9, unique=True)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    has_insurance = models.BooleanField(default=False)
    insurance_number = models.CharField(max_length=50, blank=True, null=True)  # Only if the patient has insurance

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({'Insured' if self.has_insurance else 'Uninsured'})"

