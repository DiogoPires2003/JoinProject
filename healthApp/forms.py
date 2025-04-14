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

        cleaned_data["password"] = make_password(password)
        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)