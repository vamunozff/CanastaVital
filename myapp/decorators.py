# decorators.py
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect

def user_is_tienda(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'perfil') and request.user.perfil.rol.nombre == 'tienda':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('unauthorized')
    return _wrapped_view

def user_is_cliente(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'perfil') and request.user.perfil.rol.nombre == 'cliente':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('unauthorized')
    return _wrapped_view

def user_is_administrador(view_func):
    @login_required
    def _wrapped_view(request, *args, **kwargs):

        if hasattr(request.user, 'perfil') and request.user.perfil.rol.nombre == 'administrador':
            return view_func(request, *args, **kwargs)
        else:
            return redirect('unauthorized')
    return _wrapped_view
