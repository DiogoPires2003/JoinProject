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
from sprint2.utils import render_to_pdf
from decimal import Decimal


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
    if request.method == 'POST':
        appointment_id_to_bill = request.POST.get('appointment_id')
        action = request.POST.get('action')

        try:
            cita_a_facturar = Appointment.objects.select_related('patient', 'service').get(id=appointment_id_to_bill)
            factura_existente = Factura.objects.filter(cita_origen=cita_a_facturar).first()
            factura_a_procesar = None

            # Lógica de creación/actualización de factura
            if not factura_existente:
                # Crear nueva factura
                factura_a_procesar = Factura.objects.create(
                    paciente=cita_a_facturar.patient,
                    cita_origen=cita_a_facturar,
                )

                # Crear línea de factura
                if cita_a_facturar.service:
                    LineaFactura.objects.create(
                        factura=factura_a_procesar,
                        servicio=cita_a_facturar.service,
                        descripcion_manual=cita_a_facturar.service.name,
                        cantidad=1,
                        precio_unitario=Decimal(str(cita_a_facturar.service.price))
                    )
                    factura_a_procesar.calcular_totales()
                    factura_a_procesar.estado = 'EMITIDA'
                    factura_a_procesar.save()
                    messages.success(request, f"Factura {factura_a_procesar.numero_factura} generada para {cita_a_facturar.patient}.")
                else:
                    messages.error(request, f"La cita para {cita_a_facturar.patient} no tiene un servicio asociado.")
                    factura_a_procesar.calcular_totales()
                    factura_a_procesar.estado = 'BORRADOR'
                    factura_a_procesar.save()
            else:
                factura_a_procesar = factura_existente
                factura_a_procesar.calcular_totales()
                factura_a_procesar.save()
                if action != "download_pdf":
                    messages.info(request, f"La factura {factura_a_procesar.numero_factura} ya existía.")

            # Lógica de generación de PDF
            if action in ["download_pdf", "generate_and_download_pdf"] and factura_a_procesar:
                if not factura_a_procesar.lineas_factura.exists() or factura_a_procesar.total_neto <= 0:
                    messages.warning(request, f"La factura {factura_a_procesar.numero_factura} no tiene líneas válidas.")
                    return redirect('crear_factura_individual')

                context_pdf = {
                    'factura': factura_a_procesar,
                    'lineas': factura_a_procesar.lineas_factura.all(),
                    'datos_clinica': {
                        'nombre': 'Better Health Clínica',
                        'cif': 'B12345678',
                        'direccion': 'Calle Ficticia 123, Ciudad',
                        'email': 'info@betterhealth.com'
                    }
                }
                pdf = render_to_pdf('financer/factura_pdf_template.html', context_pdf)
                if pdf:
                    response = HttpResponse(pdf, content_type='application/pdf')
                    filename = f"Factura_{factura_a_procesar.numero_factura}_{factura_a_procesar.paciente.last_name}.pdf"
                    response['Content-Disposition'] = f'attachment; filename="{filename}"'
                    return response
                else:
                    messages.error(request, f"Error al generar el PDF.")

            return redirect('crear_factura_individual')

        except Appointment.DoesNotExist:
            messages.error(request, "La cita especificada no existe.")
            return redirect('crear_factura_individual')
        except Exception as e:
            messages.error(request, f"Error al procesar la factura: {str(e)}")
            return redirect('crear_factura_individual')

    # GET request
    asistencias_confirmadas_ids = Attendance.objects.filter(attended=True).values_list('appointment_id', flat=True)
    citas_con_asistencia = Appointment.objects.filter(id__in=asistencias_confirmadas_ids).select_related('patient', 'service')
    citas_para_mostrar = []

    for cita_obj in citas_con_asistencia:
        factura_asociada = Factura.objects.filter(cita_origen=cita_obj).first()
        if factura_asociada:
            factura_asociada.calcular_totales()

        citas_para_mostrar.append({
            'cita': cita_obj,
            'factura_generada': factura_asociada
        })

    context = {
        'titulo_pagina': 'Emitir Factura Individual desde Asistencias',
        'citas_info': citas_para_mostrar,
    }
    return render(request, 'financer/crear_factura_individual.html', context)