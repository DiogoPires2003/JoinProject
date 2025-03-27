# forms.py
from django import forms
from .models import Patient
from django.contrib.auth.hashers import make_password
from django.contrib.auth.forms import AuthenticationForm
from .models import Appointment, Patient, Service

class PatientForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'dni', 'email', 'phone', 'has_insurance', 'insurance_number', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")

        cleaned_data["password"] = make_password(password)
        return cleaned_data


class EmailAuthenticationForm(AuthenticationForm):
    username = forms.EmailField(label='Email', max_length=254)

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'service', 'start_date', 'end_date']
        widgets = {
            'fecha_cita': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar opciones en los campos del formulario
        self.fields['patient'].queryset = Patient.objects.all()  # Lista de pacientes
        self.fields['service'].queryset = Service.objects.all()