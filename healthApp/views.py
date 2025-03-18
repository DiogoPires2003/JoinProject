from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

def landing(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('home')  # Redirect to a home page or any other page
    else:
        form = AuthenticationForm()
    return render(request, 'landing.html', {'form': form})


def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('landing')  # Redirect to the login page after successful registration
    else:
        form = UserCreationForm()
    return render(request, 'register.html', {'form': form})

def home(request):
    return render(request, 'home.html')