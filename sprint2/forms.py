from django import forms
from healthApp.models import Service

class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['name', 'description', 'service_type', 'price', 'covered_by_insurance', 'duration', 'available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'min': 0, 'step': 0.01}),
            'duration': forms.NumberInput(attrs={'min': 1})
        }