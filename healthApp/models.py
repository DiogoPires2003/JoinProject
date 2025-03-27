from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.timezone import now

class Patient(models.Model):
    first_name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]+$',
                message='Name must contain only letters'
            )
        ]
    )
    last_name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]+$',
                message='Name must contain only letters'
            )
        ]
    )
    dni = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{8}[A-Z]$',
                message='DNI must be 8 digits followed by a letter'
            )
        ],
        unique=True
    )
    email = models.EmailField(
        max_length=254,
        unique=True
    )
    phone = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{9}$',
                message='Phone number must be 9 digits'
            )
        ]
    )
    has_insurance = models.BooleanField(default=False)
    insurance_number = models.CharField(
        max_length=12,
        blank=True,
        null=True,
        validators=[
            RegexValidator(
                regex=r'^\d+$',
                message='Insurance number must contain only digits'
            )
        ]
    )
    password = models.CharField(
        max_length=128,
        validators=[MinLengthValidator(8)]
    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

class Service(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'




class Appointment(models.Model):
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE, null=True, blank=True)
    start_date = models.DateTimeField(default=now)
    end_date = models.DateTimeField(default=now)

    def __str__(self):
        return f"{self.patient} - {self.start_date} - {self.service}"
