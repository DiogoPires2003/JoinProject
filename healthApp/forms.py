# forms.py
from django import forms
from .models import Patient
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from .models import Appointment, Patient, Service
import requests, time
from decouple import config


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

        if password != confirm_password:
            raise forms.ValidationError("Las contraseñas no coinciden")

        cleaned_data["password"] = make_password(password)
        return cleaned_data

    def clean_insurance_number(self):
        insurance_number = self.cleaned_data.get("insurance_number")
        if not insurance_number:
            return insurance_number

        if not insurance_number[0].isalpha() or not insurance_number[1:].isdigit() or len(insurance_number) != 6:
            raise forms.ValidationError("El número de seguro debe comenzar con una letra seguida de 5 dígitos.")

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
                raise forms.ValidationError(f"Error al validar el número de seguro: {response.text}")

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