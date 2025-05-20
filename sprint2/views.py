from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.shortcuts import render, redirect, get_object_or_404

from healthApp.forms import ProfileForm
from healthApp.models import Patient


# Create your views here.
def profile_view(request):
    if 'patient_id' not in request.session:
        return redirect('login')

    patient = get_object_or_404(Patient, id=request.session['patient_id'])

    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=patient)
        if form.is_valid():
            # Actualizar contraseña si se proporcionó
            new_password = form.cleaned_data.get('new_password')
            if new_password:
                patient.password = make_password(new_password)

            form.save()
            messages.success(request, 'Perfil actualizado correctamente')
            return redirect('profile')
    else:
        form = ProfileForm(instance=patient)

    return render(request, 'profile.html', {
        'form': form,
        'patient': patient
    })

