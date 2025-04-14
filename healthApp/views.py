from .forms import PatientForm, AppointmentForm
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
import requests
from django.http import JsonResponse
from .models import Appointment, Patient, Service
from django.contrib import messages
import json
from datetime import datetime
from django.utils import timezone
from .models import Patient




def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"Received POST request with email: {email} and password: {password}")

        try:
            patient = Patient.objects.get(email=email)
            print(f"Patient found: {patient}")
            if check_password(password, patient.password):
                print("Password is correct")
                request.session['patient_id'] = patient.id
                return redirect('home')
            else:
                print("Password is incorrect")
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})

        except Patient.DoesNotExist:
            print("Patient does not exist")
            return render(request, 'login.html', {'error': 'Correo no encontrado'})

    print("Rendering login page")
    return render(request, 'login.html')


def home(request):
    if request.method == 'POST' and 'patient_id' in request.session:
        del request.session['patient_id']
        return redirect('login')

    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        return render(request, 'home.html', {'patient': patient})
    except Patient.DoesNotExist:
        return redirect('login')


def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'register.html', {'form': form})
"""
def appointment_list(request):
    citas = Appointment.objects.all()
    return render(request, 'appointment_list.html', {'citas': citas})
"""

def get_services(request):
    # Paso 1: Solicitar el token
    token_url = "https://example-mutua.onrender.com/token"
    payload = {
        "username": "gei2025",
        "password": "gei2025",
    }

    # Realiza la solicitud POST para obtener el token
    response = requests.post(token_url, data=payload)

    # Verificar si la solicitud fue exitosa
    if response.status_code == 200:
        token_data = response.json()
        access_token = token_data.get("access_token")

        # Paso 2: Usar el token para obtener los servicios
        services_url = "https://example-mutua.onrender.com/servicios-clinica/"
        headers = {
            "Authorization": f"Bearer {access_token}"
        }

        services_response = requests.get(services_url, headers=headers)

        # Verificar si la solicitud para obtener los servicios fue exitosa
        if services_response.status_code == 200:
            services = services_response.json()
            return JsonResponse(services, safe=False)
        else:
            return JsonResponse({"error": "No se pudieron obtener los servicios"}, status=services_response.status_code)
    else:
        return JsonResponse({"error": "No se pudo obtener el token"}, status=response.status_code)


def appointment_list(request):
    # Primero comprobamos si hay una sesión de paciente activa
    patient_id = request.session.get('patient_id')

    # Si no hay ID de paciente en la sesión, pero hay usuario autenticado en Django
    # podemos intentar obtenerlo por ahí
    if not patient_id and request.user.is_authenticated:
        try:
            # Asumiendo que hay una relación entre User y Patient
            patient = Patient.objects.get(user=request.user)
            # Guardamos el ID en la sesión para futuros accesos
            request.session['patient_id'] = patient.id
            patient_id = patient.id
        except Patient.DoesNotExist:
            pass

    # Si aún no tenemos patient_id, redirigir a login
    if not patient_id:
        return redirect('login')

    if request.method == 'POST':
        # Ahora sabemos que tenemos un patient_id válido
        patient = Patient.objects.get(id=patient_id)
        print(f"Usuario logueado: {patient}")

        service_id = request.POST.get('service_id')
        date = request.POST.get('fecha')
        start_time = request.POST.get('start_hour')
        end_time = request.POST.get('end_hour')

        print(f"Service ID: {service_id}")
        print(f"Date: {date}")
        print(f"Start Time: {start_time}")
        print(f"End Time: {end_time}")

        try:
            # Skip service validation
            service = None
            if service_id:
                # Use get_or_create to avoid errors
                service, created = Service.objects.get_or_create(id=service_id,
                                                                 defaults={'name': f'Service {service_id}'})

            start_datetime = f"{date} {start_time}"
            end_datetime = f"{date} {end_time}"

            start_datetime_obj = timezone.make_aware(datetime.strptime(start_datetime, '%Y-%m-%d %H:%M'))
            end_datetime_obj = timezone.make_aware(datetime.strptime(end_datetime, '%Y-%m-%d %H:%M'))

            # Validate if the appointment is in the past
            if start_datetime_obj < timezone.now():
                messages.error(request, "No puedes pedir una cita en el pasado.")
                return redirect('appointment_list')

            # Save appointment
            Appointment.objects.create(
                patient=patient,
                service=service,  # This can be None
                start_hour=start_datetime_obj.time(),
                end_hour=end_datetime_obj.time(),
                date=start_datetime_obj.date()
            )

            messages.success(request, "Cita creada correctamente.")
            return render(request, 'appointment_list.html', {'reserva_exitosa': True})
  # Or any redirect you want
        except Exception as e:
            messages.error(request, f"Error al crear la cita: {str(e)}")
            print(f"Error creating appointment: {str(e)}")

    if request.method == 'GET':
        services = Service.objects.all()

        # Get all appointments
        appointments = Appointment.objects.all()

        # Convert to JSON for JavaScript
        booked_appointments_json = []
        for appointment in appointments:
            booked_appointments_json.append({
                'date': appointment.date.strftime('%Y-%m-%d'),
                'service_id': appointment.service_id,
                'start': appointment.start_hour.strftime('%H:%M'),
                'end': appointment.end_hour.strftime('%H:%M')
            })

        return render(request, 'appointment_list.html', {
            'services': services,
            'booked_appointments': json.dumps(booked_appointments_json)
        })

    return render(request, 'appointment_list.html')



def booking_success(request):
    return render(request, 'booking_success.html')

def home(request):
    if request.method == 'POST' and 'patient_id' in request.session:
        del request.session['patient_id']
        return redirect('login')

    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        return render(request, 'home.html', {'patient': patient})
    except Patient.DoesNotExist:
        return redirect('login')

def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.password = make_password(form.cleaned_data['password'])
            patient.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'register.html', {'form': form})

def pedir_cita(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'pedir_cita.html')

def nosotros(request):
    return render(request, 'nosotros.html')

def centros(request):
    return render(request, 'centros.html')

def servicios_salud(request):
    return render(request, 'servicios_salud.html')

def informacion_util(request):
    return render(request, 'informacion_util.html')

def contacto(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'contacto.html')
def my_appointments(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        appointments = Appointment.objects.filter(patient=patient)
        return render(request, 'my_appointments.html', {'appointments': appointments})
    except Patient.DoesNotExist:
        return redirect('login')

