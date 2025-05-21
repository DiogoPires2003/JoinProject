from healthApp.models import Service
from django.shortcuts import render, get_object_or_404, redirect
from sprint2.forms import ServiceForm
from django.http import HttpResponse
import csv
from io import TextIOWrapper
from django.contrib import messages
from django.db import transaction


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
