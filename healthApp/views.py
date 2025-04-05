from .forms import PatientForm
from django.shortcuts import render, redirect
from .models import Patient
from django.contrib.auth.hashers import check_password


def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"Received POST request with email: {email} and password: {password}")

        try:
            patient = Patient.objects.get(email=email)
            print(f"Patient found: {patient}")
            if check_password(password, patient.password):
                print("Password is correct")
                request.session['patient_id'] = patient.id
                return redirect('home')
            else:
                print("Password is incorrect")
                return render(request, 'login.html', {'error': 'Contraseña incorrecta'})

        except Patient.DoesNotExist:
            print("Patient does not exist")
            return render(request, 'login.html', {'error': 'Correo no encontrado'})

    print("Rendering login page")
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
