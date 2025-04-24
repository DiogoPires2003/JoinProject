from background_task import background
from django.utils.timezone import timedelta
from django.core.mail import send_mail
from .models import Appointment


@background(schedule=60)
def send_appointment_reminder(appointment_id):
    """
    Sends an email reminder to the patient 48 hours before their appointment.
    """
    try:
        # Fetch the appointment by ID
        appointment = Appointment.objects.get(id=appointment_id)

        # Send the email
        send_mail(
            subject="Recordatorio de cita",
            message=f"Estimado/a {appointment.patient_name},\n\nEste es un recordatorio de su cita el {appointment.date}.",
            from_email="tu_correo@example.com",  # Reemplaza con tu correo
            recipient_list=[appointment.patient_email],
        )
    except Appointment.DoesNotExist:
        # Handle the case where the appointment does not exist
        pass


def schedule_appointment_reminder(appointment):
    """
    Schedules the send_appointment_reminder task 48 hours before the appointment.
    """
    from django.utils.timezone import now

    # Calculate the schedule time (48 hours before the appointment)
    reminder_time = appointment.date - timedelta(hours=48)

    # Ensure the reminder time is in the future
    if reminder_time > now():
        send_appointment_reminder(appointment.id, schedule=reminder_time)