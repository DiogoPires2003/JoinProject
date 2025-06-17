from django.shortcuts import redirect
from functools import wraps
from django.http import HttpResponseForbidden


def admin_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.session.get('is_admin'):
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def redirect_admin(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.session.get('is_admin'):
            return redirect('admin_area')
        return view_func(request, *args, **kwargs)
    return wrapper


def financer_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.user.groups.filter(name='Financer').exists():
            return HttpResponseForbidden("You do not have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return wrapper