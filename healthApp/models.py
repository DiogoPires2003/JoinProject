from django.db import models
from django.core.validators import RegexValidator, MinLengthValidator

class Patient(models.Model):
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
        verbose_name = 'Paciente'
        verbose_name_plural = 'Pacientes'