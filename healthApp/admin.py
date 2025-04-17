from django.contrib import admin
from .models import Patient, Appointment, Service, Role, Employee

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

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')  # Muestra los campos 'name' y 'description' en la lista
    search_fields = ('name',)  # Permite buscar por el campo 'name'

@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email', 'role')  # Muestra estos campos en la lista
    search_fields = ('first_name', 'last_name', 'email')  # Permite buscar por estos campos
    list_filter = ('role',)  # Permite filtrar por el campo 'role'