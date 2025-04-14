from .forms import PatientForm
from django.shortcuts import render, redirect
from .models import Patient
from django.contrib.auth.hashers import check_password, make_password

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
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})
        except Patient.DoesNotExist:
            return render(request, 'login.html', {'error': 'Correo no registrado'})

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
