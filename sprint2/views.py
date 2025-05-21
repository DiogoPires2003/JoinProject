from healthApp.models import Service, Attendance, Appointment
from django.shortcuts import render, get_object_or_404, redirect
from sprint2.forms import ServiceForm
from django.http import HttpResponse
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.db import transaction
from healthApp.decorators import admin_required, redirect_admin, financer_required
from sprint2.models import Factura, LineaFactura


def manage_services_view(request):
    if request.method == 'POST' and request.FILES.get('csv_file'):
        csv_file = TextIOWrapper(request.FILES['csv_file'].file, encoding='utf-8')
        csv_reader = csv.DictReader(csv_file)

        try:
            with transaction.atomic():
                # Get all current active services
                current_services = Service.objects.filter(available=True)
                active_service_names = set()

                for row in csv_reader:
                    service_name = row['name'].strip()
                    active_service_names.add(service_name)

                    # Update or create service
                    service, created = Service.objects.update_or_create(
                        name=service_name,
                        defaults={
                            'service_type': row['service_type'],
                            'price': float(row['price']),
                            'duration': int(row['duration']),
                            'available': True
                        }
                    )

                # Mark services not in CSV as unavailable
                current_services.exclude(name__in=active_service_names).update(available=False)

            messages.success(request, 'Servicios actualizados correctamente')
        except Exception as e:
            messages.error(request, f'Error al procesar el archivo: {str(e)}')

        return redirect('manage_services')

    # Handle GET request
    services = Service.objects.all()
    service_types = Service.SERVICE_TYPES
    filters = {
        'service_type': request.GET.get('service_type', ''),
        'available': request.GET.get('available', '')
    }

    # Apply filters
    if filters['service_type']:
        services = services.filter(service_type=filters['service_type'])
    if filters['available']:
        services = services.filter(available=filters['available'] == '1')

    context = {
        'services': services,
        'service_types': service_types,
        'filters': filters
    }

    return render(request, 'admin/manage_services.html', context)


def edit_service_view(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        form = ServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('manage_services')
    else:
        form = ServiceForm(instance=service)

    return render(request, 'admin/edit_service.html', {'form': form})


def download_services_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="services.csv"'

    writer = csv.writer(response)
    writer.writerow(['name', 'service_type', 'price', 'duration'])

    services = Service.objects.all()
    for service in services:
        writer.writerow([
            service.name,
            service.service_type,
            f'{service.price:.2f}',
            service.duration
        ])

    return response


def add_service_view(request):
    if request.method == 'POST':
        form = ServiceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Servicio añadido correctamente')
            return redirect('manage_services')
    else:
        form = ServiceForm(initial={'available': True})

    return render(request, 'admin/edit_service.html', {
        'form': form,
        'is_add': True
    })



@financer_required
def crear_factura_individual_view(request):

    asistencias_confirmadas = Attendance.objects.filter(attended=True)


    citas_pendientes_de_facturar_ids = []
    for asistencia in asistencias_confirmadas:
        # Comprobar si ya existe una factura para esta cita
        if not Factura.objects.filter(cita_origen=asistencia.appointment).exists():
            citas_pendientes_de_facturar_ids.append(asistencia.appointment.id)

    citas_a_facturar = Appointment.objects.filter(id__in=citas_pendientes_de_facturar_ids).select_related('patient',
                                                                                                          'service')


    if request.method == 'POST':
        appointment_id_to_bill = request.POST.get('appointment_id')
        if appointment_id_to_bill:
            try:
                cita_a_facturar = Appointment.objects.get(id=appointment_id_to_bill)

                # Verificar de nuevo que no se haya facturado mientras tanto (concurrencia)
                if Factura.objects.filter(cita_origen=cita_a_facturar).exists():
                    messages.warning(request, f"La cita para {cita_a_facturar.patient} ya ha sido facturada.")
                    return redirect('sprint2:crear_factura_individual')

                # Crear la Factura
                nueva_factura = Factura.objects.create(
                    paciente=cita_a_facturar.patient,
                    cita_origen=cita_a_facturar,  # Guardar la referencia a la cita

                )

                # Crear la LineaFactura
                if cita_a_facturar.service:
                    LineaFactura.objects.create(
                        factura=nueva_factura,
                        servicio=cita_a_facturar.service,
                        descripcion_manual=cita_a_facturar.service.name,  # O una descripción más detallada
                        cantidad=1,  # Asumiendo una cita es un servicio
                        precio_unitario=cita_a_facturar.service.price
                    )
                else:
                    # Manejar el caso de que la cita no tenga un servicio asociado (raro si se va a facturar)
                    messages.error(request, "La cita no tiene un servicio asociado para facturar.")
                    # Podrías borrar la factura en borrador o dejarla para edición manual
                    nueva_factura.delete()
                    return redirect('sprint2:crear_factura_individual')

                # Calcular totales de la factura
                nueva_factura.calcular_totales()
                nueva_factura.estado = 'EMITIDA'  # Opcional: cambiar estado al generar
                nueva_factura.save()

                messages.success(request,
                                 f"Factura {nueva_factura.numero_factura} generada para {cita_a_facturar.patient}.")



                return redirect('sprint2:crear_factura_individual')  # Recargar la página para ver la lista actualizada

            except Appointment.DoesNotExist:
                messages.error(request, "La cita seleccionada para facturar no existe.")
            except Exception as e:
                messages.error(request, f"Error al generar la factura: {e}")
            return redirect('sprint2:crear_factura_individual')

    context = {
        'titulo_pagina': 'Emitir Factura Individual desde Asistencias',
        'citas_a_facturar': citas_a_facturar,
    }
    return render(request, 'financer/crear_factura_individual.html', context)

