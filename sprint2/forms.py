from django import forms
from django.contrib.auth.hashers import check_password
from django.core.validators import MinLengthValidator

from healthApp.models import Service, Patient


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'service_type', 'price', 'covered_by_insurance', 'duration', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'duration': forms.NumberInput(attrs={'min': 1})
        }


import requests, time
from decouple import config
from django.utils import timezone

class ProfileForm(forms.ModelForm):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Contraseña actual",
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Nueva contraseña",
        required=False,
        validators=[MinLengthValidator(8)]
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirmar nueva contraseña",
        required=False
    )
    insurance_number = forms.CharField(
        required=False,
        label="Número de aseguradora",
        widget=forms.TextInput(attrs={'placeholder': 'Ingresa tu número de aseguradora'})
    )

    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'email', 'phone', 'insurance_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['readonly'] = True

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        current_password = cleaned_data.get('current_password')

        if not check_password(current_password, self.instance.password):
            raise forms.ValidationError("La contraseña actual es incorrecta")

        if new_password and new_password != confirm_password:
            raise forms.ValidationError("Las contraseñas nuevas no coinciden")

        return cleaned_data