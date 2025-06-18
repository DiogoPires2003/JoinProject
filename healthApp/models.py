from datetime import time

from django.core.mail import send_mail
from django.core.validators import RegexValidator, MinLengthValidator
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.models import User
from django.db import models
from django.utils.timezone import now

from betterHealth import settings


class Role(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField()

    def __str__(self):
        return self.name



class Employee(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True)
    password = models.CharField(max_length=128)

    def save(self, *args, **kwargs):
        # Hash the password if it is not already hashed
        if not check_password(self.password, self.password):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"


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
                message='El número de seguro debe comenzar con una letra seguida de 5 dígitos.'
            )
        ],
        unique=True,
        error_messages={
            'unique': "Ya existe un paciente con este número de seguro.",
            'null': "El número de seguro no puede estar vacío.",
            'blank': "El número de seguro no puede estar en blanco.",
        }
    )
    password = models.CharField(
        max_length=128,
        validators=[
            MinLengthValidator(8, message="La contraseña debe tener al menos 8 caracteres.")
        ]

    )
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new patient
        self.full_clean()
        super().save(*args, **kwargs)
        if is_new:  # Send email only for new registrations
            self.send_confirmation_email()

    def send_confirmation_email(self):
        subject = "Confirmación de Registro"
        message = f"Estimado/a {self.first_name} {self.last_name},\n\nGracias por registrarse con nosotros. Su registro se ha completado con éxito."
        recipient_list = [self.email]
        try:
            send_mail(subject, message, settings.EMAIL_HOST_USER, recipient_list)
            print("Email sent successfully!")
        except Exception as e:
            print(f"Error sending email: {e}")

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'


class Service(models.Model):
    SERVICE_TYPES = [
        ('CON', 'Consulta'),
        ('PRU', 'Prueba'),
        ('TRA', 'Tratamiento'),
        ('CIR', 'Cirugía'),
    ]

    name = models.CharField(max_length=256)
    description = models.TextField(blank=True)
    service_type = models.CharField(
        max_length=3,
        choices=SERVICE_TYPES,
        default='CON'
    )
    price = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text='Precio en euros'
    )
    covered_by_insurance = models.BooleanField(
        default=False,
        verbose_name='Incluido en mutua'
    )
    duration = models.PositiveIntegerField(
        help_text='Duración en minutos',
        default=30
    )

    available = models.BooleanField(
        default=True,
        verbose_name='Disponible',
        help_text='Indica si el servicio está disponible actualmente'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Service'
        verbose_name_plural = 'Services'

class Appointment(models.Model):
    APPOINTMENT_STATES = [
        ('AUT', 'Autorizada por mutua'),
        ('DEN', 'Autorizacion denegada'),
        ('CON', 'Confirmada')
    ]

    patient = models.ForeignKey('Patient', on_delete=models.CASCADE)
    service = models.ForeignKey('Service', on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField(default=now)
    start_hour = models.TimeField(default=time(9, 0))  # 09:00 por defecto
    end_hour = models.TimeField(default=time(10, 0))
    state = models.CharField(
        max_length=3,
        choices=APPOINTMENT_STATES,
        default='PEN',
        verbose_name='Estado'
    )

    def __str__(self):
        return f"{self.patient} - {self.date.strftime('%Y-%m-%d')} {self.start_hour.strftime('%H:%M')} - {self.service or 'No service'}"

    class Meta:
        verbose_name = 'Appointment'
        verbose_name_plural = 'Appointments'
        unique_together = ('patient', 'date', 'start_hour', 'end_hour')

class Attendance(models.Model):
    appointment = models.OneToOneField('Appointment', on_delete=models.CASCADE)
    attended = models.BooleanField(default=False)
    marked_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Attendance for {self.appointment} - {'Attended' if self.attended else 'Not Attended'}"

    class Meta:
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendances'