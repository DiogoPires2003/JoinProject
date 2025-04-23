"""
URL configuration for betterHealth project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from healthApp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', login_view, name='login'),
    path('register/', register,name='register'),
    path('', home,name='home'),
    path('appointments/', appointment_list, name='appointment_list'),
    path('my-appointments/', my_appointments, name='my_appointments'),
    path('citas/modificar/<int:appointment_id>/', modify_appointment, name='modify_appointment'),
    path('cancel_appointment/<int:appointment_id>/', cancel_appointment, name='cancel_appointment'),
    path('appointment-history/', appointment_history, name='appointment_history'),
    path('administrator-area/', admin_area, name='admin_area'),
    path('manage-appointments/', manage_appointments_view, name='manage_appointments'),
    path('manage-patients/', manage_patients_view, name='manage_patients'),
    path('patients/edit/<int:pk>/', edit_patient_view, name='edit_patient'),
    path('patients/history/<int:pk>/', patient_appointment_history_view, name='patient_appointment_history'),
    path('nosotros/', nosotros, name='nosotros'),
    path('centros/', centros, name='centros'),
    path('servicios-salud/', servicios_salud, name='servicios_salud'),
    path('informacion-util/', informacion_util, name='informacion_util'),
    path('contacto/', contacto, name='contacto'),
    path('area-privada/', login_view , name='area_privada'),
    path('logout/', patient_logout, name='logout'),
    path('logout2/', logout_view, name='logout_view'),
    path('get-available-hours/', get_available_hours, name='get_available_hours'),
    path("check-attendance/", check_attendance, name="check_attendance"),

]
