from .decorators import admin_required, redirect_admin
from .forms import PatientForm, AppointmentForm, PatientEditForm
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password, make_password
from .forms import PatientForm, AppointmentForm, ModifyAppointmentsForm
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password
import requests
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden
from .models import Appointment, Patient, Service, Employee
from django.contrib import messages
import json
from datetime import datetime, time, timedelta
from django.utils import timezone
from .models import Patient
from decouple import config
from django.views.decorators.http import require_POST




@redirect_admin
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Intentar autenticar como Employee
        try:
            employee = Employee.objects.get(email=email)
            if check_password(password, employee.password):
                #print("Empleado autenticado correctamente")
                request.session['employee_id'] = employee.id
                request.session['role_name'] = employee.role.name

                # Si es administrador, marcarlo en la sesión
                if employee.role.name == "Administrator":
                    request.session['is_admin'] = True
                else:
                    request.session['is_admin'] = False

                return redirect('admin_area')  # o alguna otra vista específica para empleados
            else:
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})

        except Employee.DoesNotExist:
            pass  # Si no es empleado, intentar con paciente

        # Intentar autenticar como Patient
        try:
            patient = Patient.objects.get(email=email)
            if check_password(password, patient.password):
                #print("Paciente autenticado correctamente")
                request.session['patient_id'] = patient.id
                return redirect('home')  # o vista específica para pacientes
            else:
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})
        except Patient.DoesNotExist:
            return render(request, 'login.html', {'error': 'Correo no encontrado'})

    return render(request, 'login.html')


def home(request):
        return render(request, 'home.html')
@admin_required
def admin_area(request):
    if request.session.get('is_admin', False):  # Verifica si es un administrador
        return render(request, 'admin_area.html')  # Devuelve la plantilla para el área de admin
    else:
        return HttpResponseForbidden("Acceso denegado")

@admin_required
def manage_patients_view(request):
    # Keep your admin check
    if not request.session.get('is_admin'):
         # Or however you handle admin checks (e.g., decorator)
        return HttpResponseForbidden("Acceso denegado")

    # Fetch all patients from the database
    all_patients = Patient.objects.all().order_by('last_name', 'first_name') # Order for consistency

    context = {
        'patients': all_patients,
        # Add other context variables if needed
    }
    return render(request, 'manage_patients.html', context)

@admin_required # Ensure only admins can access
def edit_patient_view(request, pk):
    # Check admin status again if decorator doesn't handle sessions fully
    if not request.session.get('is_admin'):
        return HttpResponseForbidden("Acceso denegado")

    patient = get_object_or_404(Patient, pk=pk) # Get patient or 404

    if request.method == 'POST':
        # Populate form with submitted data AND link it to the existing patient instance
        form = PatientEditForm(request.POST, instance=patient)
        if form.is_valid():
            form.save() # Save the changes to the patient object
            messages.success(request, f"Datos de {patient.first_name} {patient.last_name} actualizados correctamente.")
            return redirect('manage_patients') # Redirect back to the list after successful edit
        else:
            # Form is invalid, errors will be attached to the form object
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else: # GET request
        # Populate form with the existing patient's data
        form = PatientEditForm(instance=patient)

    context = {
        'form': form,
        'patient': patient, # Pass patient object for use in template (e.g., title)
    }
    return render(request, 'edit_patient.html', context)

def logout_view(request):
    print("Before logout:", request.session.get('is_admin'))
    if request.session.get('is_admin'):
        del request.session['is_admin']
        request.session.modified = True
        print("After logout:", request.session.get('is_admin'))
        return redirect('home')
    else:
        request.session.flush()
        return redirect('home')
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

def get_available_hours(request):
    if request.method == 'GET':
        service_id = request.GET.get('service_id')
        date = request.GET.get('date')

        if not service_id or not date:
            return JsonResponse({'error': 'Service ID and date are required.'}, status=400)

        # Fetch the service duration from the API
        token_url = "https://example-mutua.onrender.com/token"
        payload = {
            "username": config("API_USERNAME"),
            "password": config("API_PASSWORD"),
        }

        token_response = requests.post(token_url, data=payload)
        if token_response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch API token.'}, status=500)

        access_token = token_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        services_url = "https://example-mutua.onrender.com/servicios-clinica/"
        services_response = requests.get(services_url, headers=headers)
        if services_response.status_code != 200:
            return JsonResponse({'error': 'Failed to fetch services from the API.'}, status=500)

        services = services_response.json()
        service = next((s for s in services if s["id"] == int(service_id)), None)
        if not service:
            return JsonResponse({'error': 'Service not found.'}, status=404)

        duration = service.get("duracion_minutos", 30)  # Default to 30 minutes if not provided

        # Define working hours (e.g., 9:00 AM to 5:00 PM)
        start_time = time(9, 0)
        end_time = time(17, 0)

        # Fetch existing appointments for the selected service and date
        existing_appointments = Appointment.objects.filter(
            service_id=service_id,
            date=date
        )

        # Generate all possible time slots
        available_hours = []
        current_time = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), start_time)
        end_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), end_time)

        while current_time + timedelta(minutes=duration) <= end_datetime:
            slot_start = current_time.time()
            slot_end = (current_time + timedelta(minutes=duration)).time()

            # Check for overlaps
            overlap = any(
                appt.start_hour <= slot_start < appt.end_hour or
                appt.start_hour < slot_end <= appt.end_hour
                for appt in existing_appointments
            )

            if not overlap:
                available_hours.append({
                    'start': slot_start.strftime('%H:%M'),
                    'end': slot_end.strftime('%H:%M')
                })

            current_time += timedelta(minutes=15)  # Increment by 15 minutes

        return JsonResponse({'available_hours': available_hours})
    return JsonResponse({'error': 'Invalid request method.'}, status=405)
from django.utils.timezone import now

from django.utils.timezone import now

@redirect_admin
def appointment_list(request):
    # Check if the patient is logged in
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    # Fetch the patient
    patient = Patient.objects.get(id=patient_id)

    # Fetch services from the API
    token_url = "https://example-mutua.onrender.com/token"
    payload = {
        "username": config("API_USERNAME"),
        "password": config("API_PASSWORD"),
    }

    token_response = requests.post(token_url, data=payload)
    if token_response.status_code == 200:
        access_token = token_response.json().get("access_token")
        headers = {"Authorization": f"Bearer {access_token}"}

        services_url = "https://example-mutua.onrender.com/servicios-clinica/"
        services_response = requests.get(services_url, headers=headers)
        if services_response.status_code == 200:
            services = [
                {
                    "id": service["id"],
                    "name": service["nombre"],
                    "description": service["descripcion"],
                    "type": service["tipo_servicio"],
                    "price": service["precio"],
                    "included_in_insurance": service["incluido_mutua"],
                    "duration": service["duracion_minutos"]
                }
                for service in services_response.json()
            ]
        else:
            services = []
            messages.error(request, "Error fetching services from the API.")
    else:
        services = []
        messages.error(request, "Error fetching token from the API.")

    # Handle POST request for creating an appointment
    reserva_exitosa = False
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        date = request.POST.get('fecha')
        start_time = request.POST.get('start_hour')
        end_time = request.POST.get('end_hour')

        try:
            # Validate and create the appointment
            start_datetime = f"{date} {start_time}"
            start_datetime_obj = timezone.make_aware(datetime.strptime(start_datetime, '%Y-%m-%d %H:%M'))

            if start_datetime_obj < now():
                messages.error(request, "No puedes pedir citas antes del día y hora de hoy.")
                return redirect('appointment_list')

            end_datetime = f"{date} {end_time}"
            end_datetime_obj = timezone.make_aware(datetime.strptime(end_datetime, '%Y-%m-%d %H:%M'))

            service = Service.objects.filter(id=service_id).first()
            if not service:
                messages.error(request, "El servicio seleccionado no es válido.")
                return redirect('appointment_list')

            Appointment.objects.create(
                patient=patient,
                service=service,
                start_hour=start_datetime_obj.time(),
                end_hour=end_datetime_obj.time(),
                date=start_datetime_obj.date()
            )
            reserva_exitosa = True
        except Exception as e:
            messages.error(request, f"Error creating appointment: {str(e)}")

    # Fetch all appointments for the patient
    appointments = Appointment.objects.all()

    # Convert appointments to JSON for JavaScript
    booked_appointments_json = [
        {
            'date': appointment.date.strftime('%Y-%m-%d'),
            'service_id': appointment.service_id if appointment.service else None,
            'start': appointment.start_hour.strftime('%H:%M'),
            'end': appointment.end_hour.strftime('%H:%M')
        }
        for appointment in appointments
    ]

    return render(request, 'appointment_list.html', {
        'services': services,
        'patient': patient,
        'booked_appointments': json.dumps(booked_appointments_json),
        'reserva_exitosa': reserva_exitosa
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

@redirect_admin
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
        ) | Appointment.objects.filter(
            patient=patient,
            date=now.date(),
            start_hour__lt=now.time()
        )

        # Obtener citas futuras
        future_appointments = Appointment.objects.filter(
            patient=patient
        ).filter(
            date__gt=now.date()
        ) | Appointment.objects.filter(
            patient=patient,
            date=now.date(),
            start_hour__gte=now.time()
        )

        # Añadir etiquetas a las citas
        for appointment in past_appointments:
            appointment.status_label = "Finalizada"
        for appointment in future_appointments:
            appointment.status_label = "Próxima"

        # Combinar ambas listas y ordenarlas
        all_appointments = list(past_appointments) + list(future_appointments)
        all_appointments.sort(key=lambda x: (x.date, x.start_hour), reverse=True)

        # Obtener nombres de servicios
        service_names = get_service_names()
        for appointment in all_appointments:
            service_id = getattr(appointment.service, 'id', None)
            appointment.service_name = service_names.get(service_id, "No asignado")

        return render(request, 'appointment_history.html', {
            'appointments': all_appointments
        })

    except Patient.DoesNotExist:
        return redirect('login')