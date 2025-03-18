from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from .forms import PatientForm, EmailAuthenticationForm

def landing(request):
    if request.method == 'POST':
        form = EmailAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a home page or any other page
            else:
                form.add_error(None, 'Invalid email or password')
    else:
        form = EmailAuthenticationForm()
    return render(request, 'landing.html', {'form': form})
def register(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing')  # Redirect to the login page after successful registration
    else:
        form = PatientForm()
    return render(request, 'register.html', {'form': form})

def home(request):
    return render(request, 'home.html')