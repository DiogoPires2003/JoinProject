from .forms import PatientForm, AppointmentForm
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from .forms import PatientForm, AppointmentForm, ModifyAppointmentsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
import requests
from django.http import JsonResponse, HttpResponseNotAllowed
from .models import Appointment, Patient, Service
from django.contrib import messages
import json
from datetime import datetime, time
from django.utils import timezone
from .models import Patient
from decouple import config
from django.views.decorators.http import require_POST





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
        return render(request, 'home.html')


def patient_logout(request):
    # Check if the patient is logged in by verifying the session
    if 'patient_id' in request.session:
        del request.session['patient_id']  # Remove the patient session data
    return redirect('home')

def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'register.html', {'form': form})


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
        except Exception as e:
            messages.error(request, f"Error al crear la cita: {str(e)}")
            print(f"Error creating appointment: {str(e)}")

    # GET request processing
    patient = Patient.objects.get(id=patient_id)
    services = Service.objects.all()

    # Get all appointments
    appointments = Appointment.objects.all()

    # Convert to JSON for JavaScript
    booked_appointments_json = []
    for appointment in appointments:
        booked_appointments_json.append({
            'date': appointment.date.strftime('%Y-%m-%d'),
            'service_id': appointment.service_id if appointment.service else None,
            'start': appointment.start_hour.strftime('%H:%M'),
            'end': appointment.end_hour.strftime('%H:%M')
        })

    return render(request, 'appointment_list.html', {
        'services': services,
        'patient': patient,  # Pasar el paciente al template puede ser útil
        'booked_appointments': json.dumps(booked_appointments_json)
    })



def booking_success(request):
    return render(request, 'booking_success.html')

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

def get_service_names():
    token_url = "https://example-mutua.onrender.com/token"
    payload = {
        "username": config("API_USERNAME"),
        "password": config("API_PASSWORD"),
    }

    response = requests.post(token_url, data=payload)
    if response.status_code != 200:
        return {}

    access_token = response.json().get("access_token")
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    services_response = requests.get("https://example-mutua.onrender.com/servicios-clinica/", headers=headers)
    if services_response.status_code != 200:
        return {}

    services = services_response.json()
    # Convertimos la lista en un diccionario: id -> nombre
    return {service["id"]: service["nombre"] for service in services}


from datetime import datetime
from django.utils import timezone

from datetime import datetime
from django.utils import timezone

def my_appointments(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)

        # Ordenar las citas de más recientes a más antiguas (por fecha y hora de inicio)
        appointments = Appointment.objects.filter(patient=patient).order_by('date', 'start_hour')

        # Obtener las citas futuras
        now = timezone.now()  # Obtener la hora actual "aware"
        future_appointments = [
            appointment for appointment in appointments
            if timezone.make_aware(datetime.combine(appointment.date, appointment.start_hour)) >= now
        ]

        # Obtener los nombres de los servicios
        service_names = get_service_names()

        # Enriquecer cada cita con el nombre del servicio
        for appointment in future_appointments:
            service_id = getattr(appointment.service, 'id', None) if appointment.service else None
            appointment.service_name = service_names.get(service_id, "No asignado")

        return render(request, 'my_appointments.html', {'appointments': future_appointments})

    except Patient.DoesNotExist:
        return redirect('login')




def modify_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')

    if not patient_id and request.user.is_authenticated:
        try:
            patient = Patient.objects.get(user=request.user)
            request.session['patient_id'] = patient.id
            patient_id = patient.id
        except Patient.DoesNotExist:
            pass

    if not patient_id:
        return redirect('login')

    # Obtener la cita de la base de datos
    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)

    # Obtener servicio y sus detalles
    service = appointment.service

    # Guardar datos originales de la cita para el log
    original_date = appointment.date
    original_start_hour = appointment.start_hour
    original_end_hour = appointment.end_hour
    patient_name = appointment.patient.nombre if hasattr(appointment.patient,
                                                         'nombre') else appointment.patient.user.username if hasattr(
        appointment.patient, 'user') else str(appointment.patient)
    service_name = service.name if hasattr(service, 'name') else str(service)

    # Cálculo mejorado de la duración del servicio (en minutos)
    start_time = appointment.start_hour
    end_time = appointment.end_hour

    # Convertir a minutos para calcular la diferencia
    start_minutes = start_time.hour * 60 + start_time.minute
    end_minutes = end_time.hour * 60 + end_time.minute

    # Si end_minutes es menor que start_minutes, significa que cruza la medianoche
    if end_minutes < start_minutes:
        end_minutes += 24 * 60  # Añadimos 24 horas en minutos

    service_duration = end_minutes - start_minutes

    # Si la duración es 0 o negativa, usamos un valor predeterminado de 30 minutos
    if service_duration <= 0:
        service_duration = 30

    service_names = get_service_names()

    # Si el servicio asociado a la cita está en el diccionario de servicios, lo asignamos
    if appointment.service_id in service_names:
        appointment_service_name = service_names[appointment.service_id]
    else:
        appointment_service_name = "Servicio no disponible"

    if request.method == 'POST':
        form = ModifyAppointmentsForm(request.POST, instance=appointment)
        if form.is_valid():
            # Obtener la hora de inicio seleccionada
            start_time = form.cleaned_data['start_hour']
            date = form.cleaned_data['date']

            # Calcular end_time basado en start_time y la duración del servicio
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = start_minutes + service_duration
            end_hour = end_minutes // 60
            end_minute = end_minutes % 60

            # Manejar el caso donde la hora excede las 24 horas
            if end_hour >= 24:
                end_hour = end_hour % 24

            from datetime import time as dt_time
            end_time = dt_time(hour=end_hour, minute=end_minute)

            # Asignar el end_time calculado
            form.instance.end_hour = end_time

            # IMPORTANTE: Asegurar que se conserva el servicio
            form.instance.service = service

            # Verificar solapamientos
            overlapping_appointments = Appointment.objects.filter(
                date=date,
                service=service,
            ).exclude(id=appointment_id)

            overlap_found = False
            for appt in overlapping_appointments:
                # Convertir tiempos a minutos para comparación
                appt_start = appt.start_hour.hour * 60 + appt.start_hour.minute
                appt_end = appt.end_hour.hour * 60 + appt.end_hour.minute
                new_start = start_time.hour * 60 + start_time.minute
                new_end = end_time.hour * 60 + end_time.minute

                # Verificar solapamiento
                if (new_start < appt_end and new_end > appt_start):
                    overlap_found = True
                    print(f"SOLAPAMIENTO DETECTADO con cita ID: {appt.id}")
                    print(f"Cita existente: {appt.date} de {appt.start_hour} a {appt.end_hour}")
                    break

            if overlap_found:
                messages.error(request, "La hora seleccionada se solapa con otra cita existente.")
                return redirect('modify_appointment', appointment_id=appointment_id)

            # Si llegamos aquí, no hay solapamientos y podemos guardar la cita
            modified_appointment = form.save()

            # Verificar que se haya guardado correctamente el servicio
            print(f"CITA MODIFICADA CORRECTAMENTE. Service ID: {modified_appointment.service_id}")


            return redirect('my_appointments')
    else:
        form = ModifyAppointmentsForm(instance=appointment)

    # Get all appointments for JavaScript
    appointments = Appointment.objects.all()

    # Convert to JSON for JavaScript
    booked_appointments_json = []
    for appt in appointments:
        booked_appointments_json.append({
            'id': appt.id,
            'date': appt.date.strftime('%Y-%m-%d'),
            'service_id': appt.service_id if appt.service else None,
            'start': appt.start_hour.strftime('%H:%M'),
            'end': appt.end_hour.strftime('%H:%M')
        })

    return render(request, 'modify_appointment.html', {
        'form': form,
        'appointment': appointment,
        'appointment_service_name': appointment_service_name,
        'booked_appointments': json.dumps(booked_appointments_json),
        'service_duration': service_duration,  # Pasamos la duración del servicio al template
        'service_id': service.id if service else None  # Añadimos el service_id para el frontend
    })

@require_POST
def cancel_appointment(request, appointment_id):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseNotAllowed(['POST'])

def appointment_history(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        now = timezone.now()

        # Obtener citas pasadas
        past_appointments = Appointment.objects.filter(
            patient=patient
        ).filter(
            date__lt=now.date()
        ).order_by('-date', '-start_hour')

        service_names = get_service_names()

        for appointment in past_appointments:
            service_id = getattr(appointment.service, 'id', None)
            appointment.service_name = service_names.get(service_id, "No asignado")

        return render(request, 'appointment_history.html', {
            'appointments': past_appointments
        })

    except Patient.DoesNotExist:
        return redirect('login')