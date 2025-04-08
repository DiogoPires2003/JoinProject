from .forms import PatientForm, AppointmentForm
from django.shortcuts import render, redirect
from django.contrib.auth.hashers import check_password
import requests
from django.http import JsonResponse
from datetime import datetime
from .models import Appointment, Patient, Service
from django.contrib import messages


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        try:
            patient = Patient.objects.get(email=email)
            if check_password(password, patient.password):
                request.session['patient_id'] = patient.id
                return redirect('home')
            else:
                return render(request, 'login.html', {'error': 'Invalid password'})

        except Patient.DoesNotExist:
            return render(request, 'login.html', {'error': 'Invalid email'})

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
        form = AppointmentForm(request.POST)
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
    if request.method == 'POST':
        patient_id = request.POST.get('patient_id')  # Replace with actual patient identification logic
        service_id = request.POST.get('servicio')
        date = request.POST.get('fecha')
        start_time = request.POST.get('hora')

        # Debugging prints
        print(f"Patient ID: {patient_id}")
        print(f"Service ID: {service_id}")
        print(f"Date: {date}")
        print(f"Start Time: {start_time}")

        try:
            patient = Patient.objects.get(id=patient_id)
            service = Service.objects.get(id=service_id)
            start_datetime = f"{date} {start_time}"

            # Calculate end time (e.g., 30 minutes after start time)
            from datetime import datetime, timedelta
            start_datetime_obj = datetime.strptime(start_datetime, '%Y-%m-%d %H:%M')
            end_datetime_obj = start_datetime_obj + timedelta(minutes=30)

            # Save the appointment
            print("Guardando cita en la base de datos...")
            Appointment.objects.create(
                patient=patient,
                service=service,
                start_date=start_datetime_obj,
                end_date=end_datetime_obj
            )
            print("Cita guardada correctamente.")
            messages.success(request, "Appointment created successfully!")
            return redirect('home.html')  # Replace with your desired redirect URL
        except (Patient.DoesNotExist, Service.DoesNotExist):
            messages.error(request, "Invalid patient or service selected.")
    return render(request, 'appointment_list.html')