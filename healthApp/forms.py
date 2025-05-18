# forms.py
from django import forms
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from .models import Appointment, Patient, Service
import requests, time
from decouple import config
from django.utils import timezone


class PatientForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'dni', 'email', 'phone', 'has_insurance', 'insurance_number', 'password']

    api_token = None
    token_expiration = 0

    def get_api_token(self):
        if time.time() < self.token_expiration and self.api_token:
            return self.api_token

        auth_url = "https://example-mutua.onrender.com/token"
        auth_data = {
            "username": config("API_USERNAME"),
            "password": config("API_PASSWORD"),
        }

        try:
            response = requests.post(auth_url, data=auth_data)
            print("API Response:", response.status_code, response.text)
            if response.status_code == 200:
                token_data = response.json()
                self.api_token = token_data.get("access_token")
                self.token_expiration = time.time() + 600
                return self.api_token
            else:
                raise forms.ValidationError(f"Error al autenticar con la API: {response.text}")
        except requests.RequestException as e:
            raise forms.ValidationError(f"Error al conectar con la API: {str(e)}")

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

        # Check password length
        if password and len(password) < 8:
            raise forms.ValidationError("La contraseña debe tener al menos 8 caracteres.")

        # Hash the password
        cleaned_data["password"] = make_password(password)
        return cleaned_data

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if Patient.objects.filter(email=email).exists():
            raise forms.ValidationError("Ya existe un paciente con este correo electrónico.")
        return email

    def clean_insurance_number(self):
        insurance_number = self.cleaned_data.get("insurance_number")
        if not insurance_number:
            return insurance_number

        if not insurance_number[0].isalpha() or not insurance_number[1:].isdigit() or len(insurance_number) != 6:
            raise forms.ValidationError("El número de seguro debe comenzar con una letra seguida de 5 dígitos.")

        if Patient.objects.filter(insurance_number=insurance_number).exists():
            raise forms.ValidationError("Ya existe un paciente con este número de seguro.")

        try:
            token = self.get_api_token()
        except forms.ValidationError as e:
            raise forms.ValidationError(f"Error al obtener el token: {str(e)}")

        if not token:
            raise forms.ValidationError("No se pudo obtener el token de la API para validar el seguro.")

        api_url = f"https://example-mutua.onrender.com/pacientes/verificar/{insurance_number}"
        headers = {"Authorization": f"Bearer {token}"}
        try:
            response = requests.get(api_url, headers=headers)
            if response.status_code != 200:
                raise forms.ValidationError(f"El numero de seguro no es válido o no pertenece a la mutua.")

            response_data = response.json()
            if not response_data.get("pertenece_mutua", False):
                raise forms.ValidationError("El número de seguro es inválido o no pertenece a la mutua.")
        except requests.RequestException as e:
            raise forms.ValidationError(f"Error al conectar con la API: {str(e)}")

        return insurance_number


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'service', 'start_hour', 'end_hour', 'date']
        widgets = {
            'start_hour': forms.TimeInput(attrs={'type': 'time'}),
            'end_hour': forms.TimeInput(attrs={'type': 'time'}),
            'date': forms.DateInput(attrs={'type': 'date'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar las opciones de pacientes y servicios
        self.fields['patient'].queryset = Patient.objects.all()
        self.fields['service'].queryset = Service.objects.all()
    username = forms.EmailField(label='Correo electrónico', max_length=254)

class ModifyAppointmentsForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['service', 'start_hour', 'end_hour', 'date']  # Solo los campos que se deben modificar
        widgets = {
            'start_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'end_hour': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Hacer que el campo 'service' no sea editable, solo mostrar el título
        self.fields['service'].widget = forms.TextInput(attrs={'readonly': 'readonly'})
        if 'instance' in kwargs:
            appointment = kwargs['instance']
            self.fields['service'].initial = appointment.service.name


class PatientEditForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = [
            'first_name',
            'last_name',
            'dni',
            'email',
            'phone',
            'has_insurance',
            'insurance_number'
        ]

    def clean(self):
        cleaned_data = super().clean()

        dni = cleaned_data.get('dni')
        if dni and Patient.objects.filter(dni=dni).exclude(pk=self.instance.pk).exists():
             self.add_error('dni', 'Ya existe un paciente con este número de DNI.')

        return cleaned_data

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['insurance_number'].required = False


class AppointmentAdminCreateForm(forms.Form):
    patient = forms.ModelChoiceField(
        queryset=Patient.objects.order_by('last_name', 'first_name'),
        label="Seleccionar Paciente",
        widget=forms.Select(attrs={'class': 'form-select'}) # Basic select, consider Select2 later
    )
    service = forms.ModelChoiceField(
        queryset=Service.objects.order_by('name'), # Assumes Service model exists locally
        label="Seleccionar Servicio",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    date = forms.DateField(
        label="Fecha de la Cita",
        widget=forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'min': timezone.now().strftime('%Y-%m-%d') # Prevent selecting past dates
            }
        ),
        # Initial value can be set if desired, e.g., initial=timezone.now().date()
    )

    # Hidden fields to store the selected time slot from JS
    selected_start_hour = forms.CharField(widget=forms.HiddenInput(), required=False) # Start as not required
    selected_end_hour = forms.CharField(widget=forms.HiddenInput(), required=False) # Start as not required

    def clean(self):
        cleaned_data = super().clean()
        start_hour_str = cleaned_data.get("selected_start_hour")
        end_hour_str = cleaned_data.get("selected_end_hour")
        date = cleaned_data.get("date")
        service = cleaned_data.get("service")
        patient = cleaned_data.get("patient")

        # --- Basic Validations ---
        if not patient:
             self.add_error('patient', "Debe seleccionar un paciente.")
        if not service:
             self.add_error('service', "Debe seleccionar un servicio.")
        if not date:
             self.add_error('date', "Debe seleccionar una fecha.")

        # --- Date Validation ---
        if date and date < timezone.now().date():
            self.add_error('date', "No se puede seleccionar una fecha pasada.")

        # --- Time Slot Validation ---
        if not start_hour_str or not end_hour_str:
            # Raise a non-field error because it depends on JS interaction
            raise forms.ValidationError("Debe seleccionar una hora disponible para la cita.", code='no_hour_selected')
        else:
            try:
                start_time = timezone.datetime.strptime(start_hour_str, '%H:%M').time()
                end_time = timezone.datetime.strptime(end_hour_str, '%H:%M').time()
                # Combine date and time, make aware for comparison
                appointment_start_dt = timezone.make_aware(timezone.datetime.combine(date, start_time))
                now_dt = timezone.now()

                if appointment_start_dt <= now_dt:
                    raise forms.ValidationError("No se puede crear una cita para una hora que ya ha pasado.", code='past_time_selected')

                # --- Check for Conflicts ---
                conflicting_appointments = Appointment.objects.filter(
                    date=date,
                    # Check if the new slot overlaps with any existing slot for *any* patient/service
                    start_hour__lt=end_time,
                    end_hour__gt=start_time
                ).exists() # Use exists() for efficiency

                if conflicting_appointments:
                     raise forms.ValidationError(
                         f"El horario seleccionado ({start_hour_str} - {end_hour_str}) ya no está disponible. Por favor, seleccione otro.",
                         code='conflict'
                     )

            except (ValueError, TypeError):
                 raise forms.ValidationError("La hora seleccionada no es válida.", code='invalid_time_format')

        return cleaned_data


class ModifyAppointmentsForm_administrator(forms.ModelForm):
    class Meta:
        model = Appointment
        # Campos que el admin modificará principalmente
        fields = ['service', 'start_hour', 'end_hour', 'date']
        widgets = {
            # Usaremos 'text' para que el JS pueda poner el valor,
            # pero podríamos usar 'time' si el navegador lo soporta bien con JS
            'start_hour': forms.TimeInput(attrs={'type': 'hidden'}), # Lo haremos hidden, se rellena con JS
            'end_hour': forms.TimeInput(attrs={'type': 'hidden'}),   # Lo haremos hidden, se calcula en la vista
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'service': forms.TextInput(attrs={'readonly': 'readonly', 'class': 'form-control bg-light'}) # Hacemos servicio no editable aquí
        }
        labels = { # Etiquetas más claras para el admin
            'date': 'Nueva Fecha',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Rellenar el campo service_display si hay instancia
        if self.instance and self.instance.pk and self.instance.service:
            self.fields['service_display'].initial = self.instance.service.name
        elif self.instance and self.instance.pk:
            self.fields['service_display'].initial = "Servicio no asignado"

        # Pre-rellenar la fecha y hora inicial en los campos correspondientes
        if self.instance and self.instance.pk:
            self.fields['date'].initial = self.instance.date
            # El valor inicial del campo oculto se pondrá en la plantilla
            # self.fields['selected_start_hour'].initial = self.instance.start_hour.strftime('%H:%M') # No necesario aquí



