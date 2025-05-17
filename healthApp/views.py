from .decorators import admin_required, redirect_admin
from .forms import PatientForm, AppointmentForm, PatientEditForm, ModifyAppointmentsForm, AppointmentAdminCreateForm
from .models import Appointment, Patient, Service, Employee, Attendance
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.hashers import check_password, make_password
from django.http import JsonResponse, HttpResponseNotAllowed, HttpResponseForbidden, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.utils.timezone import now, timezone
from decouple import config
from datetime import datetime, time, timedelta
import requests
import json
import logging
from django.db.models import Q  # Import Q object for complex lookups
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db import IntegrityError
from datetime import time as dt_time
from datetime import datetime
from django.utils import timezone


@admin_required
def check_attendance(request):
    today = now().date()

    # Handle form submission
    if request.method == 'POST':
        appointment_id = request.POST.get('appointment_id')
        attended = request.POST.get('attended') == 'on'

        appointment = Appointment.objects.get(id=appointment_id)
        attendance, created = Attendance.objects.get_or_create(appointment=appointment)
        attendance.attended = attended
        attendance.save()

        return redirect('check_attendance')

    # Query today's appointments
    appointments = Appointment.objects.filter(date=today)

    # Apply filters
    patient_filter = request.GET.get("patient")
    service_filter = request.GET.get("service")
    attended_filter = request.GET.get("attended")

    if patient_filter:
        appointments = appointments.filter(
            Q(patient__first_name__icontains=patient_filter) |
            Q(patient__last_name__icontains=patient_filter)
        )

    if service_filter:
        appointments = appointments.filter(service_id=int(service_filter))

    if attended_filter in ["0", "1"]:
        attended = attended_filter == "1"
        appointments = appointments.filter(attendance__attended=attended)

    # Enrich appointments with service names and attendance status
    enriched_appointments = []
    for appointment in appointments:
        attendance = Attendance.objects.filter(appointment=appointment).first()
        service_name = appointment.service.name if appointment.service else 'No asignado'

        enriched_appointments.append({
            'id': appointment.id,
            'patient': f"{appointment.patient.first_name} {appointment.patient.last_name}",
            'service_name': service_name,
            'start_hour': appointment.start_hour,
            'attended': attendance.attended if attendance else False,
        })

    return render(request, 'admin/check_attendance.html', {
        'appointments': enriched_appointments,
        'services': Service.objects.all(),
    })


@redirect_admin
def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Try to authenticate as Employee
        try:
            employee = Employee.objects.get(email=email)
            if check_password(password, employee.password):
                request.session['employee_id'] = employee.id
                request.session['role_name'] = employee.role.name
                request.session['is_admin'] = employee.role.name == "Administrator"
                return redirect('admin_area')
            else:
                return render(request, 'auth/login.html', {'error_message': 'Incorrect password.'})
        except Employee.DoesNotExist:
            pass

        # Try to authenticate as Patient
        try:
            patient = Patient.objects.get(email=email)
            if check_password(password, patient.password):
                request.session['patient_id'] = patient.id
                return redirect('home')
            else:
                return render(request, 'auth/login.html',
                              {'error_message': 'El usuario o la contraseña son incorrectos.'})
        except Patient.DoesNotExist:
            return render(request, 'auth/login.html', {'error_message': 'El usuario o la contraseña son incorrectos.'})

    return render(request, 'auth/login.html')


def home(request):
    return render(request, 'home/home.html')


@admin_required
def admin_area(request):
    if request.session.get('is_admin', False):  # Verifica si es un administrador
        return render(request, 'admin/admin_area.html')  # Devuelve la plantilla para el área de admin
    else:
        return HttpResponseForbidden("Acceso denegado")


@admin_required
def manage_patients_view(request):
    # Keep your admin check
    if not request.session.get('is_admin'):
        # Or however you handle admin checks (e.g., decorator)
        return HttpResponseForbidden("Acceso denegado")

    # Fetch all patients from the database
    all_patients = Patient.objects.all().order_by('last_name', 'first_name')  # Order for consistency

    context = {
        'patients': all_patients,
        # Add other context variables if needed
    }
    return render(request, 'admin/manage_patients.html', context)


@admin_required  # Ensure only admins can access
def edit_patient_view(request, pk):
    # Check admin status again if decorator doesn't handle sessions fully
    if not request.session.get('is_admin'):
        return HttpResponseForbidden("Acceso denegado")

    patient = get_object_or_404(Patient, pk=pk)  # Get patient or 404

    if request.method == 'POST':
        # Populate form with submitted data AND link it to the existing patient instance
        form = PatientEditForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()  # Save the changes to the patient object
            messages.success(request, f"Datos de {patient.first_name} {patient.last_name} actualizados correctamente.")
            return redirect('manage_patients')  # Redirect back to the list after successful edit
        else:
            # Form is invalid, errors will be attached to the form object
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:  # GET request
        # Populate form with the existing patient's data
        form = PatientEditForm(instance=patient)

    context = {
        'form': form,
        'patient': patient,  # Pass patient object for use in template (e.g., title)
    }
    return render(request, 'admin/edit_patient.html', context)


@admin_required
def patient_appointment_history_view(request, pk):
    # Admin check
    if not request.session.get('is_admin'):
        return HttpResponseForbidden("Acceso denegado")

    patient = get_object_or_404(Patient, pk=pk)
    now = timezone.now()

    # Get all appointments with service information
    all_patient_appointments = Appointment.objects.filter(
        patient=patient
    ).select_related('service').order_by('-date', '-start_hour')

    appointments_with_status = []
    for appointment in all_patient_appointments:
        is_past = False
        if appointment.date < now.date():
            is_past = True
        elif appointment.date == now.date() and appointment.start_hour < now.time():
            is_past = True

        appointment.status_label = "Finalizada" if is_past else "Próxima"
        appointment.service_name = appointment.service.name if appointment.service else "Servicio Desconocido"
        appointments_with_status.append(appointment)

    context = {
        'patient': patient,
        'appointments': appointments_with_status,
    }
    return render(request, 'admin/patient_appointment_history.html', context)


@admin_required
def manage_appointments_view(request):
    now_dt = timezone.now()
    today = now_dt.date()
    now_time = now_dt.time()

    future_appointments_filter = Q(date__gt=today) | Q(date=today, start_hour__gte=now_time)

    appointments_list = Appointment.objects.filter(future_appointments_filter) \
        .select_related('patient', 'service') \
        .order_by('date', 'start_hour')

    services = Service.objects.all()  # For the filter dropdown

    patient_name = request.GET.get('patient_name', '').strip()
    date_from = request.GET.get('date_from')
    date_to = request.GET.get('date_to')
    service_id = request.GET.get('service')

    if patient_name:
        appointments_list = appointments_list.filter(
            Q(patient__first_name__icontains=patient_name) |
            Q(patient__last_name__icontains=patient_name)
        )

    if date_from:
        try:

            date_from_obj = timezone.datetime.strptime(date_from, '%Y-%m-%d').date()
            if date_from_obj >= today:
                appointments_list = appointments_list.filter(date__gte=date_from)

        except (ValueError, TypeError):
            messages.warning(request, f"Formato de fecha 'Desde' inválido ignorado: {date_from}")
    if date_to:
        try:
            appointments_list = appointments_list.filter(date__lte=date_to)
        except (ValueError, TypeError):
            messages.warning(request, f"Formato de fecha 'Hasta' inválido ignorado: {date_to}")
    if service_id:
        appointments_list = appointments_list.filter(service_id=service_id)

    paginator = Paginator(appointments_list, 10)
    page_number = request.GET.get('page')
    try:
        page_obj = paginator.get_page(page_number)
    except PageNotAnInteger:
        page_obj = paginator.page(1)
    except EmptyPage:
        page_obj = paginator.page(paginator.num_pages)

    context = {
        'page_obj': page_obj,
        'services': services,

    }
    return render(request, 'admin/manage_appointments.html', context)


@admin_required
def create_appointment_admin_view(request):
    """
    Vista para que un administrador cree una nueva cita médica
    usando un formulario personalizado con selección de hora dinámica.
    """
    if request.method == 'POST':
        form = AppointmentAdminCreateForm(request.POST)
        if form.is_valid():

            patient = form.cleaned_data['patient']
            service = form.cleaned_data['service']
            date = form.cleaned_data['date']
            start_hour_str = form.cleaned_data['selected_start_hour']
            end_hour_str = form.cleaned_data['selected_end_hour']

            try:
                start_time = timezone.datetime.strptime(start_hour_str, '%H:%M').time()
                end_time = timezone.datetime.strptime(end_hour_str, '%H:%M').time()

                new_appointment = Appointment.objects.create(
                    patient=patient,
                    service=service,
                    date=date,
                    start_hour=start_time,
                    end_hour=end_time
                )

                storage = messages.get_messages(request)
                for _ in storage:
                    pass

                messages.success(
                    request,
                    f"Cita para {patient.first_name} {patient.last_name} el {date.strftime('%d/%m/%Y')} a las {start_hour_str} creada exitosamente."
                )

                return redirect('manage_appointments')

            except IntegrityError:

                messages.error(request, "Ya existe una cita con estos datos. Por favor, verifica la información.")
            except (ValueError, TypeError) as e:

                messages.error(request, f"Error interno al procesar la hora seleccionada: {e}")
            except Exception as e:

                messages.error(request, f"Ocurrió un error inesperado al crear la cita: {str(e)}")
        else:

            messages.error(request, "El formulario contiene errores. Por favor, revíselos.")

    else:
        form = AppointmentAdminCreateForm()

    context = {
        'form': form,
    }
    return render(request, 'admin/create_appointment.html', context)


@admin_required
def edit_appointment_admin_view(request, pk):
    """
    Vista para que un administrador modifique una cita existente.
    """
    appointment = get_object_or_404(Appointment.objects.select_related('patient', 'service'), pk=pk)
    service = appointment.service
    patient = appointment.patient

    service_duration = 30  # Valor por defecto si no se puede calcular
    if service and appointment.start_hour and appointment.end_hour:
        start_time = appointment.start_hour
        end_time = appointment.end_hour
        start_minutes = start_time.hour * 60 + start_time.minute
        end_minutes = end_time.hour * 60 + end_time.minute
        if end_minutes < start_minutes:
            end_minutes += 24 * 60
        calculated_duration = end_minutes - start_minutes
        if calculated_duration > 0:
            service_duration = calculated_duration

    service_name = service.name if service else "Servicio no asignado"

    if request.method == 'POST':
        form = ModifyAppointmentsForm(request.POST, instance=appointment)

        start_hour_str = request.POST.get('start_hour')
        date_str = request.POST.get('date')

        valid_post = True
        form_errors = []
        start_time = None
        date = None

        if not date_str:
            form_errors.append("Debe seleccionar una fecha.")
            valid_post = False
        else:
            try:
                date = timezone.datetime.strptime(date_str, '%Y-%m-%d').date()
                if date < timezone.now().date():
                    form_errors.append("No se puede seleccionar una fecha pasada.")
                    valid_post = False
            except ValueError:
                form_errors.append("Formato de fecha inválido.")
                valid_post = False

        if not start_hour_str:
            form_errors.append("Debe seleccionar una hora.")
            valid_post = False
        else:
            try:
                start_time = timezone.datetime.strptime(start_hour_str, '%H:%M').time()
            except ValueError:
                form_errors.append("Formato de hora inválido.")
                valid_post = False

        if valid_post and start_time and date:
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = start_minutes + service_duration
            end_hour = (end_minutes // 60) % 24
            end_minute = end_minutes % 60
            end_time = dt_time(hour=end_hour, minute=end_minute)

            overlapping_appointments = Appointment.objects.filter(
                date=date,

                start_hour__lt=end_time,
                end_hour__gt=start_time
            ).exclude(pk=pk)

            if overlapping_appointments.exists():
                messages.error(request,
                               f"El horario seleccionado ({start_hour_str} - {end_time.strftime('%H:%M')}) se solapa con otra cita existente.")

                valid_post = False
            else:

                try:

                    appointment.date = date
                    appointment.start_hour = start_time
                    appointment.end_hour = end_time

                    appointment.save()

                    messages.success(request,
                                     f"Cita de {patient} modificada exitosamente para el {date.strftime('%d/%m/%Y')} a las {start_hour_str}.")
                    return redirect('manage_appointments')
                except Exception as e:
                    messages.error(request, f"Error al guardar los cambios: {e}")
                    valid_post = False

        if not valid_post:
            for error in form_errors:
                messages.error(request, error)


    else:

        form = ModifyAppointmentsForm(instance=appointment)

    all_appointments = Appointment.objects.filter(date__gte=timezone.now().date() - timedelta(days=1)).values(
        'id', 'date', 'service_id', 'start_hour', 'end_hour'
    )
    booked_appointments_list = []
    for appt in all_appointments:
        booked_appointments_list.append({
            'id': appt['id'],
            'date': appt['date'].strftime('%Y-%m-%d'),
            'service_id': appt['service_id'],
            'start': appt['start_hour'].strftime('%H:%M'),
            'end': appt['end_hour'].strftime('%H:%M')
        })
    booked_appointments_json = json.dumps(booked_appointments_list)

    context = {
        'form': form,
        'appointment': appointment,
        'patient': patient,
        'service_name': service_name,
        'service_duration': service_duration,
        'service_id': service.id if service else None,
        'booked_appointments': booked_appointments_json,
        'current_appointment_id': pk,
    }

    return render(request, 'admin/edit_appointment.html', context)


@admin_required
def cancel_appointment_admin_view(request, pk):
    """
    Handles the cancellation of an appointment by an admin.
    Only allows cancellation of future appointments via POST request.
    """
    now_dt = timezone.now()
    today = now_dt.date()
    now_time = now_dt.time()

    appointment = get_object_or_404(Appointment, pk=pk)

    try:
        appointment_start_dt = timezone.make_aware(
            timezone.datetime.combine(appointment.date, appointment.start_hour)
        )
    except ValueError:
        messages.error(request, "Error al procesar la hora de la cita.")
        return redirect('manage_appointments')

    if appointment_start_dt <= now_dt:
        messages.error(request, "No se puede cancelar una cita que ya ha comenzado o ha pasado.")
        return redirect('manage_appointments')

    if request.method == 'POST':
        try:
            patient_name = f"{appointment.patient.first_name} {appointment.patient.last_name}"
            appointment_date_str = appointment.date.strftime('%d/%m/%Y')
            appointment_time_str = appointment.start_hour.strftime('%H:%M')

            appointment.delete()

            messages.success(
                request,
                f"La cita de {patient_name} para el {appointment_date_str} a las {appointment_time_str} ha sido cancelada exitosamente."
            )

        except Exception as e:

            messages.error(request, f"Ocurrió un error al intentar cancelar la cita: {e}")

        return redirect('manage_appointments')

    else:

        messages.warning(request, "Método no válido para cancelar. Use el botón de cancelación.")
        return redirect('manage_appointments')


def logout_view(request):
    if request.session.get('is_admin'):
        request.session.flush()
        return redirect('home')
    else:
        request.session.flush()
        return redirect('home')


def patient_logout(request):
    # Check if the patient is logged in by verifying the session
    if 'patient_id' in request.session:
        del request.session['patient_id']  # Remove the patient session data
    return redirect('home')


def get_available_hours(request):
    if request.method == 'GET':
        service_id = request.GET.get('service_id')
        date = request.GET.get('date')

        if not service_id or not date:
            return JsonResponse({'error': 'Service ID and date are required.'}, status=400)

        try:
            # Get service and its duration
            service = Service.objects.get(id=service_id)
            duration = service.duration

            # Define working hours
            start_time = time(8, 0)  # 8:00 AM
            end_time = time(20, 0)   # 8:00 PM

            # Get all existing appointments for the date
            existing_appointments = Appointment.objects.filter(
                date=date
            ).order_by('start_hour')

            # Generate available slots
            available_hours = []
            current_time = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), start_time)
            end_datetime = datetime.combine(datetime.strptime(date, '%Y-%m-%d'), end_time)

            # Convert existing appointments to time ranges
            booked_slots = []
            for appt in existing_appointments:
                booked_slots.append({
                    'start': datetime.combine(datetime.strptime(date, '%Y-%m-%d'), appt.start_hour),
                    'end': datetime.combine(datetime.strptime(date, '%Y-%m-%d'), appt.end_hour)
                })

            while current_time + timedelta(minutes=duration) <= end_datetime:
                slot_end = current_time + timedelta(minutes=duration)
                is_available = True

                # Check if slot overlaps with any existing appointment
                for booked in booked_slots:
                    if (current_time < booked['end'] and
                        slot_end > booked['start']):
                        is_available = False
                        # Move current_time to the end of this booked slot
                        current_time = booked['end']
                        break

                if is_available:
                    available_hours.append({
                        'start': current_time.time().strftime('%H:%M'),
                        'end': slot_end.time().strftime('%H:%M')
                    })
                    current_time = slot_end
                else:
                    continue

            return JsonResponse({'available_hours': available_hours})

        except Service.DoesNotExist:
            return JsonResponse({'error': 'Service not found.'}, status=404)
        except Exception as e:
            logging.error(f"Error in get_available_hours: {e}")
            return JsonResponse({'error': 'Internal server error.'}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


@redirect_admin
def appointment_list(request):
    MAX_APPOINTMENTS_PER_DAY = 5

    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    patient = Patient.objects.get(id=patient_id)
    services = Service.objects.all()

    # Handle POST request for creating an appointment
    reserva_exitosa = False
    if request.method == 'POST':
        service_id = request.POST.get('service_id')
        date = request.POST.get('fecha')
        start_time = request.POST.get('start_hour')
        end_time = request.POST.get('end_hour')

        appointments_on_date = Appointment.objects.filter(patient=patient, date=date).count()
        if appointments_on_date >= MAX_APPOINTMENTS_PER_DAY:
            messages.error(request, f"Solo puedes reservar un máximo de {MAX_APPOINTMENTS_PER_DAY} citas por día.")
            return redirect('appointment_list')

        try:
            start_datetime = f"{date} {start_time}"
            start_datetime_obj = timezone.make_aware(datetime.strptime(start_datetime, '%Y-%m-%d %H:%M'))

            if start_datetime_obj < now():
                messages.error(request, "No puedes pedir citas antes del día y hora de hoy.")
                return redirect('appointment_list')

            end_datetime = f"{date} {end_time}"
            end_datetime_obj = timezone.make_aware(datetime.strptime(end_datetime, '%Y-%m-%d %H:%M'))

            service = Service.objects.get(id=service_id)
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

    # Fetch all appointments for JavaScript
    appointments = Appointment.objects.all()
    booked_appointments_json = [
        {
            'date': appointment.date.strftime('%Y-%m-%d'),
            'service_id': appointment.service_id if appointment.service else None,
            'start': appointment.start_hour.strftime('%H:%M'),
            'end': appointment.end_hour.strftime('%H:%M')
        }
        for appointment in appointments
    ]

    return render(request, 'appointments/appointment_list.html', {
        'services': services,
        'patient': patient,
        'booked_appointments': json.dumps(booked_appointments_json),
        'reserva_exitosa': reserva_exitosa
    })


def booking_success(request):
    return render(request, 'appointments/booking_success.html')


def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'auth/register.html', {'form': form})


def nosotros(request):
    return render(request, 'home/nosotros.html')


def centros(request):
    return render(request, 'home/centros.html')


def servicios_salud(request):
    return render(request, 'home/servicios_salud.html')


def informacion_util(request):
    return render(request, 'home/informacion_util.html')


def contacto(request):
    if request.method == 'POST':
        return redirect('home')
    return render(request, 'home/contacto.html')


@redirect_admin
def modify_appointment(request, appointment_id):
    patient_id = request.session.get('patient_id')

    if not patient_id:
        return redirect('login')

    # Get appointment and service from database
    appointment = get_object_or_404(Appointment, id=appointment_id, patient_id=patient_id)
    service = appointment.service

    # Get service duration from the Service model
    service_duration = service.duration if service else 30  # Use default only if no service

    if request.method == 'POST':
        form = ModifyAppointmentsForm(request.POST, instance=appointment)
        if form.is_valid():
            start_time = form.cleaned_data['start_hour']
            date = form.cleaned_data['date']

            # Calculate end time based on service duration from database
            start_minutes = start_time.hour * 60 + start_time.minute
            end_minutes = start_minutes + service_duration
            end_hour = end_minutes // 60
            end_minute = end_minutes % 60

            if end_hour >= 24:
                end_hour = end_hour % 24

            end_time = dt_time(hour=end_hour, minute=end_minute)
            form.instance.end_hour = end_time
            form.instance.service = service

            # Check for overlapping appointments
            overlapping_appointments = Appointment.objects.filter(
                date=date,
                service=service
            ).exclude(id=appointment_id)

            overlap_found = False
            for appt in overlapping_appointments:
                appt_start = appt.start_hour.hour * 60 + appt.start_hour.minute
                appt_end = appt.end_hour.hour * 60 + appt.end_hour.minute
                new_start = start_time.hour * 60 + start_time.minute
                new_end = end_time.hour * 60 + end_time.minute

                if new_start < appt_end and new_end > appt_start:
                    overlap_found = True
                    break

            if overlap_found:
                messages.error(request, "La hora seleccionada se solapa con otra cita existente.")
                return redirect('modify_appointment', appointment_id=appointment_id)

            modified_appointment = form.save()
            return redirect('my_appointments')
    else:
        form = ModifyAppointmentsForm(instance=appointment)

    # Get all appointments for JavaScript
    appointments = Appointment.objects.all().values(
        'id', 'date', 'service_id', 'start_hour', 'end_hour'
    )
    booked_appointments_json = [
        {
            'id': appt['id'],
            'date': appt['date'].strftime('%Y-%m-%d'),
            'service_id': appt['service_id'],
            'start': appt['start_hour'].strftime('%H:%M'),
            'end': appt['end_hour'].strftime('%H:%M')
        }
        for appt in appointments
    ]

    return render(request, 'appointments/modify_appointment.html', {
        'form': form,
        'appointment': appointment,
        'appointment_service_name': appointment.service.name if appointment.service else "No asignado",
        'booked_appointments': json.dumps(booked_appointments_json),
        'service_duration': service_duration,
        'service_id': service.id if service else None
    })


@require_POST
def cancel_appointment(request, appointment_id):
    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        appointment = get_object_or_404(Appointment, id=appointment_id)
        appointment.delete()
        return JsonResponse({'status': 'success'})
    return HttpResponseNotAllowed(['POST'])


@redirect_admin
def appointment_history(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        now = timezone.now()

        # Get past appointments
        past_appointments = (
                Appointment.objects.filter(
                    patient=patient,
                    date__lt=now.date()
                ) |
                Appointment.objects.filter(
                    patient=patient,
                    date=now.date(),
                    start_hour__lt=now.time()
                )
        ).select_related('service')

        # Get future appointments
        future_appointments = (
                Appointment.objects.filter(
                    patient=patient,
                    date__gt=now.date()
                ) |
                Appointment.objects.filter(
                    patient=patient,
                    date=now.date(),
                    start_hour__gte=now.time()
                )
        ).select_related('service')

        # Add labels to appointments
        for appointment in past_appointments:
            appointment.status_label = "Finalizada"
            appointment.service_name = appointment.service.name if appointment.service else "No asignado"

        for appointment in future_appointments:
            appointment.status_label = "Próxima"
            appointment.service_name = appointment.service.name if appointment.service else "No asignado"

        # Combine and sort appointments
        all_appointments = list(past_appointments) + list(future_appointments)
        all_appointments.sort(key=lambda x: (x.date, x.start_hour), reverse=True)

        return render(request, 'appointments/appointment_history.html', {
            'appointments': all_appointments
        })

    except Patient.DoesNotExist:
        return redirect('login')


@redirect_admin
def my_appointments(request):
    patient_id = request.session.get('patient_id')
    if not patient_id:
        return redirect('login')

    try:
        patient = Patient.objects.get(id=patient_id)
        now_dt = timezone.now()

        # Get future appointments with service information
        appointments = Appointment.objects.filter(
            patient=patient
        ).select_related('service').order_by('date', 'start_hour')

        future_appointments = [
            appointment for appointment in appointments
            if timezone.make_aware(datetime.combine(appointment.date, appointment.start_hour)) >= now_dt
        ]

        # Add service names directly from the Service model
        for appointment in future_appointments:
            appointment.service_name = appointment.service.name if appointment.service else "No asignado"

        return render(request, 'appointments/my_appointments.html', {'appointments': future_appointments})

    except Patient.DoesNotExist:
        return redirect('login')
