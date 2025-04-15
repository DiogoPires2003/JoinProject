from django.contrib import admin
from .models import Patient, Appointment, Service

@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'phone', 'has_insurance')
    search_fields = ('first_name', 'last_name', 'email', 'dni')

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'start_hour', 'end_hour', 'service')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'description')  # muestra estas columnas en la lista
    search_fields = ('name',)  # permite buscar por nombre