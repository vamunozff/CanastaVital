from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import CustomUserCreationForm, ClienteForm, TiendaForm, DireccionForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User, Group
from .models import Producto, ProductosTiendas, Proveedor, Cliente, Tienda, Promocion, Direccion, Orden, ProductoOrden, Ciudad, Departamento, Categoria, MetodoPago
from django.contrib import messages
from .forms import ProductosTiendasForm, PromocionForm
from django.db import transaction
import json
from django.db.models import Sum
from decimal import Decimal
from .decorators import user_is_tienda, user_is_cliente, user_is_administrador
from django.utils import timezone
from datetime import timedelta
from django.core.paginator import Paginator
from django.template.loader import render_to_string
import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate, login as auth_login

# Función perfil_cliente corregida
@login_required
@user_is_cliente
def perfil_cliente(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "No tienes un perfil de cliente asociado.")
        return redirect('home')

    if request.method == 'POST':
        # Crear un diccionario con los datos del formulario para el modelo Cliente
        cliente_data = {
            'telefono': request.POST.get('telefono', ''),
            'fecha_nacimiento': request.POST.get('fecha_nacimiento', None),
            'numero_documento': request.POST.get('numero_documento', ''),
            'tipo_documento': cliente.tipo_documento  # Mantener el tipo de documento actual
        }
        
        # Manejar la imagen de perfil si se proporciona
        if 'imagen_perfil' in request.FILES:
            cliente_data['imagen_perfil'] = request.FILES['imagen_perfil']
        
        # Actualizar datos del modelo Cliente
        cliente_form = ClienteForm(cliente_data, request.FILES, instance=cliente)
        
        if cliente_form.is_valid():
            with transaction.atomic():  # Usar transacción para garantizar que ambos modelos se actualicen o ninguno
                cliente_form.save()
                
                # Actualizar datos del modelo User
                request.user.first_name = request.POST.get('first_name', request.user.first_name)
                request.user.last_name = request.POST.get('last_name', request.user.last_name)
                request.user.save()
                
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('perfil_cliente')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in cliente_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        cliente_form = ClienteForm(instance=cliente)

    context = {
        'cliente': cliente,
        'user': request.user,
        'cliente_form': cliente_form,
    }
    return render(request, 'clientes/perfil.html', context)