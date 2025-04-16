from django.http import HttpResponseForbidden
from django.shortcuts import redirect

class PatientAuthenticationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        public_paths = ['/', '/register/']  # Update paths to match urls.py
        if request.path not in public_paths and not request.session.get('patient_id'):
            return redirect('login')
        return self.get_response(request)

class BlockURLMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Lista de URLs a bloquear
        blocked_urls = ['/api/servicios/']  # Actualiza con las URLs que deseas bloquear

        if request.path in blocked_urls:
            return HttpResponseForbidden("Acceso denegado a esta URL.")

        return self.get_response(request)