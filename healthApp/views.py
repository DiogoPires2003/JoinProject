from .forms import PatientForm
from django.shortcuts import render, redirect
from .models import Patient
from django.contrib.auth.hashers import check_password


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
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = PatientForm()

    return render(request, 'register.html', {'form': form})

from django.shortcuts import render

def pedir_cita(request):
    return render(request, 'pedir_cita.html')
