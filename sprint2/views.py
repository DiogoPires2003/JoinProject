from django.shortcuts import render
from healthApp.models import Service
from django.shortcuts import render, get_object_or_404, redirect
from sprint2.forms import ServiceForm




# Create your views here.


def manage_services_view(request):
    # Get all services and order by name
    services = Service.objects.all().order_by('name')

    # Handle filters
    name_filter = request.GET.get('name', '')
    service_type = request.GET.get('service_type', '')
    availability = request.GET.get('available', '')

    if name_filter:
        services = services.filter(name__icontains=name_filter)
    if service_type:
        services = services.filter(service_type=service_type)
    if availability:
        is_available = availability == '1'
        services = services.filter(available=is_available)

    context = {
        'services': services,
        'service_types': Service.SERVICE_TYPES,
        'filters': {
            'name': name_filter,
            'service_type': service_type,
            'available': availability
        }
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