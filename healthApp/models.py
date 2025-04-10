from django.contrib.auth.models import User
from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.timezone import now
from datetime import time
from django.dispatch import receiver
from django.db.models.signals import post_save


def get_default_user():
    return User.objects.first()

@receiver(post_save, sender=User)
def create_patient_for_user(sender, instance, created, **kwargs):
    if created:
        Patient.objects.create(user=instance)


class Patient(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient', null=True, blank=True)

    def get_default_user(self):
        return User.objects.first()
    first_name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]+$',
                message='El nombre debe contener solo letras'
            )
        ]
    )
    last_name = models.CharField(
        max_length=50,
        validators=[
            RegexValidator(
                regex=r'^[A-Za-z\s]+$',
                message='El apellido debe contener solo letras'
            )
        ]
    )
    dni = models.CharField(
        max_length=9,
        validators=[
            RegexValidator(
                regex=r'^\d{8}[A-Z]$',
                message='El DNI debe tener 8 dígitos seguidos de una letra'
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
                message='El número de teléfono debe tener 9 dígitos'
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
                regex=r'^[A-Za-z]\d{5}$',
                message='El número de seguro debe comenzar con una letra seguida de 5 dígitos'
            )
        ],
        unique=True,
        error_messages={
            'unique': "Ya existe un paciente con este número de seguro."
        }
    )
    password = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(8, message="La contraseña debe tener al menos 8 caracteres.")
        ]

    )

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Service(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'


class Appointment(models.Model):
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=now)
    start_hour = models.TimeField(default=time(9, 0))  # 09:00 por defecto
    end_hour = models.TimeField(default=time(10, 0))

    def __str__(self):
        return f"{self.patient} - {self.date.strftime('%Y-%m-%d')} {self.start_hour.strftime('%H:%M')} - {self.service or 'No service'}"



        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'