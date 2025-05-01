# decorators.py
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from functools import wraps
from myapp.models import Cliente

def user_is_tienda(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Tienda').exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('unauthorized')
    return wrapper

def user_is_cliente(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Cliente').exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('unauthorized')
    return wrapper

def user_is_administrador(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if request.user.groups.filter(name='Administrador').exists():
            return view_func(request, *args, **kwargs)
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('unauthorized')
    return wrapper
