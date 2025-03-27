from django.contrib import admin
from .models import Patient, Appointment

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'has_insurance')
    search_fields = ('first_name', 'last_name', 'email', 'dni')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'start_date', 'end_date', 'service')
