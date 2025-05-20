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

# Create your views here.
def hello(request):
    return HttpResponse("Bienvenido <a href='index.html'>Ingresar</a>")


@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()

        # Autenticar al usuario
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            roles = []
            if user.groups.filter(name='Cliente').exists():
                roles.append({'nombre': 'Cliente', 'url': '/index_cliente'})
            if user.groups.filter(name='Tienda').exists():
                roles.append({'nombre': 'Tienda', 'url': '/index_tienda'})
            if user.groups.filter(name='Administrador').exists():
                roles.append({'nombre': 'Administrador', 'url': '/index_administrador'})

            # Si el usuario tiene un solo rol, redirigir automáticamente
            if len(roles) == 1:
                return JsonResponse({'redirect': roles[0]['url']})

            # Si el usuario tiene múltiples roles, devolver los roles como JSON
            if len(roles) > 1:
                return JsonResponse({'roles': roles})

            # Si no tiene roles válidos
            return JsonResponse({'error': 'No tienes un rol asignado. Por favor, contacta al administrador.'}, status=403)

        # Si las credenciales son incorrectas
        return JsonResponse({'error': 'Credenciales incorrectas. Por favor, intenta nuevamente.'}, status=403)

    elif request.method == 'GET':
        return render(request, 'registration/login.html')

    return JsonResponse({'error': 'Método no permitido.'}, status=405)

@user_is_tienda
def vista_tienda(request):
    return render(request, 'tienda.html')

@user_is_cliente
def vista_cliente(request):
    return render(request, 'cliente.html')

@user_is_administrador
def vista_para_administrador(request):
    return render(request, 'administrador.html')

def unauthorized(request):
    return render(request, 'unauthorized.html', {'message': 'No tienes permiso para acceder a esta página.'})

def home(request):
    categorias = Categoria.objects.all()
    return render(request, 'inicio/index.html',  {'categorias': categorias})

@login_required
def completar_registro(request):
    perfil_id = request.session.get('perfil_id')
    print(f"Perfil ID en sesión: {perfil_id}")

    if not perfil_id:
        messages.error(request, "No tienes un perfil asociado. Por favor contacta a un administrador.")
        return redirect('verificar_registro')

    perfil = get_object_or_404(Perfil, id=perfil_id)
    print(f"Perfil encontrado: {perfil}")

    if not perfil.rol:
        messages.error(request, "Tu perfil no tiene un rol asignado. Por favor contacta a un administrador.")
        return redirect('verificar_registro')

    return render(request, 'registration/confirmar_completar.html', {'perfil': perfil})

@login_required
@user_is_tienda
def index_tienda(request):
    # Configurar el grupo en la sesión
    request.session['groups'] = 'Tienda'

    # Verificar que el usuario pertenece al grupo "Tienda"
    if not request.user.groups.filter(name='Tienda').exists():
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('unauthorized')

    # Obtener la tienda asociada al usuario
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada.")
        return redirect('unauthorized')

    # Calcular estadísticas de la tienda
    total_productos = tienda.productos_tiendas.count()
    productos_sin_stock = tienda.productos_tiendas.filter(cantidad=0).count()
    pedidos_pendientes = Orden.objects.filter(tienda=tienda, estado='pendiente').count()

    now = timezone.now()
    ventas_hoy = Orden.objects.filter(tienda=tienda, fecha_venta__date=now).aggregate(Sum('total'))['total__sum'] or 0
    ventas_semana = Orden.objects.filter(tienda=tienda, fecha_venta__gte=now - timedelta(days=7)).aggregate(Sum('total'))['total__sum'] or 0

    promociones_activas = Promocion.objects.filter(tienda=tienda, activo=True)
    proveedores_activos = Proveedor.objects.filter(tienda=tienda)

    # Contexto para la plantilla
    context = {
        'tienda': tienda,
        'total_productos': total_productos,
        'productos_sin_stock': productos_sin_stock,
        'pedidos_pendientes': pedidos_pendientes,
        'ventas_hoy': ventas_hoy,
        'ventas_semana': ventas_semana,
        'promociones_activas': promociones_activas,
        'proveedores_activos': proveedores_activos,
    }

    return render(request, 'tiendas/index.html', context)

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# @csrf_exempt
from django.shortcuts import redirect

from django.contrib.auth.models import Group

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            try:
                # Crear el usuario
                user = form.save(commit=False)
                user.first_name = request.POST.get('first_name', '').strip()
                user.last_name = request.POST.get('last_name', '').strip()
                user.email = form.cleaned_data['email']
                user.save()

                # Asignar el usuario al grupo "Cliente"
                cliente_group = Group.objects.get(name='Cliente')  # Asegúrate de que el grupo "Cliente" exista
                user.groups.add(cliente_group)

                # Crear el modelo Cliente asociado al usuario
                Cliente.objects.create(
                    usuario=user,
                    telefono=request.POST.get('telefono', '').strip(),
                    fecha_nacimiento=request.POST.get('fecha_nacimiento', None)
                )

                # Iniciar sesión automáticamente después del registro
                login(request, user)
                messages.success(request, 'Registro exitoso. Bienvenido.')
                return redirect('index_cliente')

            except Group.DoesNotExist:
                messages.error(request, 'El grupo "Cliente" no existe. Por favor, contacta al administrador.')
            except Exception as e:
                messages.error(request, f'Ocurrió un error: {str(e)}')

        messages.error(request, 'Por favor, corrija los errores en el formulario.')
        return render(request, 'registration/register.html', {'form': form})

    elif request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


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


@login_required
@user_is_tienda
def perfil_tienda(request):
    # Obtener la tienda asociada al usuario
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada.")
        return redirect('unauthorized')

    if request.method == 'POST':
        # Actualizar los datos de la tienda
        tienda.nombre = request.POST.get('nombre', tienda.nombre)
        tienda.horarios = request.POST.get('horarios', tienda.horarios)
        tienda.telefono = request.POST.get('telefono', tienda.telefono)
        tienda.descripcion = request.POST.get('descripcion', tienda.descripcion)

        # Actualizar el logo si se sube un archivo
        if 'logo_url' in request.FILES:
            tienda.logo_url = request.FILES['logo_url']

        tienda.save()
        messages.success(request, "Datos de la tienda actualizados exitosamente.")
        return redirect('perfil_tienda')

    # Obtener la dirección principal de la tienda (si existe)
    direccion = Direccion.objects.filter(tienda=tienda).first()

    return render(request, 'tiendas/perfil.html', {'tienda': tienda, 'direccion': direccion})


@login_required
@user_is_cliente
def index_cliente(request):
    # Configurar el grupo en la sesión
    request.session['groups'] = 'Cliente'

    # Verificar que el usuario pertenece al grupo "Cliente"
    if not request.user.groups.filter(name='Cliente').exists():
        messages.error(request, "No tienes permiso para acceder a esta sección.")
        return redirect('unauthorized')

    # Obtener promociones activas y categorías
    promociones_activas = Promocion.objects.filter(activo=True).order_by('fecha_fin')
    categorias = Categoria.objects.all()

    # Contexto para enviar al template
    contexto = {
        'promociones': promociones_activas,
        'categorias': categorias
    }

    return render(request, 'clientes/index.html', contexto)

@login_required
@user_is_administrador
def index_administrador(request):
    # Configurar el grupo en la sesión
    request.session['groups'] = 'Administrador'

    return render(request, 'administrador/index.html')

def categoria(request):
    return render(request, 'categorias/categorias.html')

@login_required
@user_is_tienda
def asignarProducto(request):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para asignar productos.")
        return redirect("index_producto")

    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            producto_id = int(request.POST.get('txtProducto_id'))
            proveedor_id = int(request.POST.get('txtProveedor_id'))
            precio_unitario = Decimal(request.POST.get('txtPrecioUnitario'))
            cantidad = int(request.POST.get('txtCantidad'))
            estado = request.POST.get('txtEstado')
            imagen = request.FILES.get('logo_url', None)

            # Si no se proporciona una imagen, usar una imagen predeterminada
            default_image_path = 'productos_tiendas/Default.jpg'
            if not imagen:
                imagen = default_image_path

            # Obtener el producto y el proveedor
            producto = get_object_or_404(Producto, id=producto_id)
            proveedor = get_object_or_404(Proveedor, id=proveedor_id, tienda=tienda)

            # Crear un nuevo producto asociado a la tienda
            nuevo_producto_tienda = ProductosTiendas(
                producto=producto,
                proveedor=proveedor,
                tienda=tienda,
                precio_unitario=precio_unitario,
                cantidad=cantidad,
                estado=estado,
                imagen=imagen
            )

            # Validar y guardar el nuevo producto
            nuevo_producto_tienda.full_clean()
            nuevo_producto_tienda.save()

            messages.success(request, "Producto asignado correctamente.")
            return redirect("index_producto")

        except ValueError:
            messages.error(request, "Por favor, ingrese valores válidos para los campos numéricos.")
        except ValidationError as ve:
            messages.error(request, f"Error de validación: {ve}")
        except Exception as e:
            messages.error(request, f"Error al asignar el producto: {str(e)}")

    # Obtener los proveedores y productos asociados a la tienda
    proveedores = Proveedor.objects.filter(tienda=tienda).distinct()
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)

    return render(request, 'productos/index.html', {
        'productos': Producto.objects.all(),
        'proveedores': proveedores,
        'productos_tiendas': productos_tiendas
    })