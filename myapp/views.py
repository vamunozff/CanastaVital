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
    return render(request, 'inicio/home.html',  {'categorias': categorias})

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
@login_required
@user_is_cliente
def perfil_cliente(request):
    perfil_id = request.session.get('perfil_id')  # Asegurar que perfil_id está definido
    if not perfil_id:
        messages.error(request, "No tienes un perfil de cliente activo.")
        return redirect('verificar_registro')

    perfil = get_object_or_404(Perfil, id=perfil_id)
    cliente = get_object_or_404(Cliente, perfil=perfil)

    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if cliente_form.is_valid():
            cliente_form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil_cliente')
        else:
            messages.error(request, 'Error al actualizar el perfil. Verifica los campos.')

    else:
        cliente_form = ClienteForm(instance=cliente)

    return render(request, 'clientes/perfil.html', {
        'cliente_form': cliente_form,
        'cliente': cliente,
        'user': request.user
    })



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

@login_required
def actualizarProductosTiendas_list(request):
    pass
@login_required
def eliminarPrductosTiendas(request, id):
    productosTiendas = ProductosTiendas.objects.get(id=id)
    productosTiendas.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('productos')


@login_required
@user_is_tienda
def index_producto(request):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar productos.")
        return redirect("unauthorized")

    # Obtener los productos asociados a la tienda
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda).order_by("producto__nombre")

    # Obtener todos los productos disponibles
    productos = Producto.objects.all()

    # Obtener los proveedores asociados a la tienda
    proveedores = Proveedor.objects.filter(tienda=tienda)

    # Paginar los productos de la tienda
    paginator = Paginator(productos_tiendas, 10)  # Mostrar 10 productos por página
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    # Renderizar la plantilla con los productos y proveedores
    return render(request, "productos/index.html", {
        "productos_tiendas": page_obj,
        "productos": productos,
        "proveedores": proveedores,
    })


@login_required
def buscar_producto(request):
    query = request.GET.get('q', '')
    perfil = get_object_or_404(Perfil, user=request.user)
    tienda = get_object_or_404(Tienda, perfil=perfil)

    productos_tiendas = ProductosTiendas.objects.filter(
        tienda=tienda,
        producto__nombre__icontains=query
    )
    html = render_to_string('productos/_product_table.html', {
        'productos_tiendas': productos_tiendas
    })
    return JsonResponse({'html': html})

@login_required
@user_is_tienda
def actualizar_producto(request, id):
    # Obtener el producto asociado a la tienda
    producto_tienda = get_object_or_404(ProductosTiendas, id=id)

    # Verificar que el producto pertenece a la tienda del usuario
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar productos.")
        return redirect("index_producto")

    if producto_tienda.tienda != tienda:
        messages.error(request, "No tienes permiso para actualizar este producto.")
        return redirect("index_producto")

    if request.method == "POST":
        # Procesar el formulario enviado
        form = ProductosTiendasForm(request.POST, request.FILES, instance=producto_tienda)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Producto actualizado correctamente!")
            return redirect("index_producto")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        # Mostrar el formulario con los datos actuales del producto
        form = ProductosTiendasForm(instance=producto_tienda)

    # Obtener promociones activas para este producto
    promociones_activas = Promocion.objects.filter(
        productos_aplicables=producto_tienda,
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now(),
    )

    return render(request, "productos/actualizar.html", {
        "form": form,
        "producto_tienda": producto_tienda,
        "promociones_activas": promociones_activas,
    })


@login_required
def eliminar_producto(request, id):
    productosTiendas = get_object_or_404(ProductosTiendas, id=id)
    if request.method == "POST":
        productosTiendas.delete()
        messages.success(request, '¡Producto eliminado correctamente!')
        return redirect('index_producto')
    return redirect('index_producto')

@login_required
@user_is_tienda
def index_proveedor(request):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar proveedores.")
        return redirect("unauthorized")  # Asegúrate de tener esta vista o URL definida.

    # Filtrar proveedores asociados a la tienda del usuario
    proveedores = Proveedor.objects.filter(tienda=tienda)

    # Renderizar la plantilla con los proveedores
    return render(request, "proveedor/index.html", {"proveedores": proveedores})

@login_required
@user_is_tienda
def asignar_proveedor(request):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, 'No tienes una tienda asociada para gestionar proveedores.')
        return redirect('index_proveedor')

    if request.method == 'POST':
        # Obtener los datos del formulario
        razon_social = request.POST.get('txtRazonSocial')
        email = request.POST.get('txtEmail')
        telefono = request.POST.get('numTelefono')
        direccion = request.POST.get('txtDireccion')
        estado = request.POST.get('txtEstado')

        try:
            # Crear un nuevo proveedor asociado a la tienda
            nuevo_proveedor = Proveedor(
                tienda=tienda,
                razon_social=razon_social,
                email=email,
                telefono=telefono,
                direccion=direccion,
                estado=estado
            )
            nuevo_proveedor.full_clean()  # Validar los datos
            nuevo_proveedor.save()  # Guardar el proveedor en la base de datos

            messages.success(request, 'Proveedor registrado correctamente.')
            return redirect('index_proveedor')
        except ValidationError as ve:
            messages.error(request, f'Error de validación: {ve}')
        except Exception as e:
            messages.error(request, f'Error al registrar el proveedor: {str(e)}')

    # Obtener la lista de proveedores asociados a la tienda
    proveedores = Proveedor.objects.filter(tienda=tienda)

    return render(request, 'proveedor/index.html', {'proveedores': proveedores})

@login_required
@user_is_tienda
def actualizar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    # Verificar que el proveedor pertenece a la tienda del usuario
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar proveedores.")
        return redirect("index_proveedor")

    if proveedor.tienda != tienda:
        messages.error(request, "No tienes permiso para actualizar este proveedor.")
        return redirect("index_proveedor")

    if request.method == 'POST':
        try:
            # Obtener los datos del formulario
            razon_social = request.POST.get('txtRazonSocial')
            email = request.POST.get('txtEmail')
            telefono = request.POST.get('numTelefono')
            direccion = request.POST.get('txtDireccion')
            estado = request.POST.get('txtEstado')

            # Actualizar los datos del proveedor
            proveedor.razon_social = razon_social
            proveedor.email = email
            proveedor.telefono = telefono
            proveedor.direccion = direccion
            proveedor.estado = estado

            # Validar y guardar los cambios
            proveedor.full_clean()
            proveedor.save()

            messages.success(request, "¡Proveedor actualizado correctamente!")
            return redirect("index_proveedor")

        except ValueError:
            messages.error(request, "Por favor, ingrese valores válidos.")
        except Exception as e:
            messages.error(request, f"Error al actualizar el proveedor: {str(e)}")

    return render(request, "proveedor/actualizar.html", {"proveedor": proveedor})

@login_required
@user_is_tienda
def eliminar_proveedor(request, id):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar proveedores.")
        return redirect("index_proveedor")

    # Buscar el proveedor asociado a la tienda
    proveedor = get_object_or_404(Proveedor, id=id, tienda=tienda)

    if request.method == 'POST':
        proveedor.delete()
        messages.success(request, "Proveedor eliminado correctamente.")
        return redirect("index_proveedor")

    messages.error(request, "Acción no permitida.")
    return redirect("index_proveedor")

@login_required
def register_cliente(request):
    cliente_form = ClienteForm(request.POST or None, request.FILES or None)

    if request.method == 'POST':
        if cliente_form.is_valid():
            try:
                # Verifica si el usuario ya tiene un cliente registrado
                if Cliente.objects.filter(perfil__user=request.user).exists():
                    messages.warning(request, 'Ya tienes un cliente registrado.')
                    return redirect('index_cliente')

                # Obtiene el perfil asociado al usuario
                perfil = Perfil.objects.get(user=request.user)

                # Crea y guarda el cliente
                cliente = cliente_form.save(commit=False)
                cliente.perfil = perfil
                cliente.save()

                messages.success(request, 'El cliente se ha registrado exitosamente.')
                return redirect('index_cliente')
            except Perfil.DoesNotExist:
                messages.error(request, 'No se encontró el perfil asociado. Por favor, complete el registro primero.')
                return redirect('index_cliente')
        else:
            # Itera sobre los errores del formulario y los agrega a los mensajes
            for field, error_list in cliente_form.errors.items():
                field_name = cliente_form.fields[field].label
                for error in error_list:
                    messages.error(request, f'Error en "{field_name}": {error}')

    context = {'cliente_form': cliente_form}
    return render(request, 'registration/confirmar_completar.html', context)

@login_required
def register_tienda(request):
    if request.method == 'POST':
        tienda_form = TiendaForm(request.POST, request.FILES)

        if tienda_form.is_valid():
            try:
                perfil = Perfil.objects.get(user=request.user)
            except Perfil.DoesNotExist:
                messages.error(request, 'No se encontró el perfil asociado. Por favor, complete el registro primero.')
                return redirect('index_tienda')

            if perfil.rol.nombre != 'tienda':
                messages.error(request, 'No tiene permiso para registrar una tienda.')
                return redirect('index_tienda')

            tienda = tienda_form.save(commit=False)
            tienda.perfil = perfil
            tienda.save()

            messages.success(request, 'La tienda se ha registrado exitosamente.')
            return redirect('index_tienda')

        else:
            for field, error_list in tienda_form.errors.items():
                for error in error_list:
                    messages.error(request, f'Error en {field}: {error}')

    else:
        tienda_form = TiendaForm()

    context = {
        'tienda_form': tienda_form
    }
    return render(request, 'registration/confirmar_completar.html', context)


@login_required
def busqueda_tiendas(request):
    query = request.GET.get('search', '')
    if query:
        tiendas = Tienda.objects.filter(nombre__icontains=query)
    else:
        tiendas = Tienda.objects.all()

    return render(request, 'tiendas/busqueda.html', {'tiendas': tiendas})

@login_required
def busqueda_productos(request, tienda_id):
    tienda = get_object_or_404(Tienda, id=tienda_id)

    productosTiendas = ProductosTiendas.objects.filter(tienda=tienda, estado='activo').select_related('producto', 'proveedor').prefetch_related('promociones')

    context = {
        'tienda': tienda,
        'productosTiendas': productosTiendas
    }

    return render(request, 'productos/busqueda.html', context)


def promociones_activas(request, tienda_id):
    tienda = get_object_or_404(Tienda, id=tienda_id)
    promociones = Promocion.objects.activas().filter(tienda=tienda)

    context = {
        'tienda': tienda,
        'promociones': promociones,
    }
    return render(request, 'promociones/activas.html', context)


@login_required
def confirmar_pago(request):
    # Buscar el perfil del usuario con rol de cliente
    perfil_cliente = request.user.perfil_set.filter(rol__nombre="cliente").first()
    
    if not perfil_cliente:
        return JsonResponse({'error': 'No tienes un perfil de cliente asociado.'}, status=400)

    # Verificar que existe un cliente asociado a ese perfil
    cliente = Cliente.objects.filter(perfil=perfil_cliente).first()
    
    if not cliente:
        return JsonResponse({'error': 'No tienes un cliente asociado a tu perfil.'}, status=400)

    # Obtener direcciones del cliente
    direcciones = Direccion.objects.filter(cliente=cliente)
    direccion_principal = direcciones.filter(principal=True).first()
    departamentos = Departamento.objects.all()
    metodos_pago = MetodoPago.objects.all()

    # Filtrar ciudades según el departamento de la dirección principal
    ciudades = Ciudad.objects.filter(departamento=direccion_principal.departamento) if direccion_principal else Ciudad.objects.all()

    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Validar método de pago
            metodo_pago_id = data.get('metodo_pago_id')
            metodo_pago = MetodoPago.objects.filter(id=metodo_pago_id).first()
            if not metodo_pago:
                return JsonResponse({'error': 'El método de pago seleccionado no es válido.'}, status=400)

            # Obtener carrito de la sesión
            carrito = request.session.get('carrito', [])
            if not carrito:
                return JsonResponse({'error': 'El carrito está vacío, agrega productos antes de continuar.'}, status=400)

            # Validar productos del carrito
            productos_en_tienda = []
            errores = []
            for item in carrito:
                try:
                    producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'], estado='activo')
                    productos_en_tienda.append({
                        'producto': producto_tienda,
                        'nombre': producto_tienda.producto.nombre,
                        'cantidad': item['cantidad'],
                        'precio_unitario': producto_tienda.precio_unitario,
                        'subtotal': producto_tienda.precio_unitario * item['cantidad']
                    })
                except ProductosTiendas.DoesNotExist:
                    errores.append(f'El producto con ID {item["producto_tienda_id"]} no está disponible.')

            if errores:
                return JsonResponse({'error': errores}, status=400)

            # Validar dirección de envío
            direccion_envio_id = data.get('direccion_envio_id')
            direccion_envio = Direccion.objects.filter(id=direccion_envio_id, cliente=cliente).first()
            if not direccion_envio:
                return JsonResponse({'error': 'La dirección seleccionada no es válida.'}, status=400)

            # Calcular totales
            subtotal = sum(item['subtotal'] for item in productos_en_tienda)
            iva = subtotal * 0.12  # 12% de IVA
            total = subtotal + iva

            # Crear orden
            orden = Orden.objects.create(
                cliente=cliente,
                direccion_envio=direccion_envio,
                metodo_pago=metodo_pago,
                subtotal=subtotal,
                iva=iva,
                total=total,
            )

            # Agregar productos a la orden
            for producto in productos_en_tienda:
                ProductosOrden.objects.create(
                    orden=orden,
                    producto_tienda_id=producto['producto'].id,
                    cantidad=producto['cantidad'],
                    precio_unitario=producto['precio_unitario']
                )

            return JsonResponse({'success': True, 'orden_id': orden.id})

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Datos inválidos en la solicitud.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': f'Ocurrió un error al procesar la orden: {str(e)}'}, status=500)

    # Contexto para GET
    context = {
        'direcciones': direcciones,
        'direccion_principal': direccion_principal,
        'departamentos': departamentos,
        'ciudades': ciudades,
        'metodos_pago': metodos_pago,
    }
    return render(request, 'otros/confirmar_pago.html', context)


# @csrf_exempt
@login_required
def crear_direccion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            form = DireccionForm(data)

            if form.is_valid():
                nueva_direccion = form.save(commit=False)

                if request.user.is_cliente:
                    nueva_direccion.cliente = request.user.cliente
                elif request.user.is_tienda:
                    nueva_direccion.tienda = request.user.tienda
                nueva_direccion.save()

                return JsonResponse({'success': True, 'direccion_id': nueva_direccion.id})
            else:
                return JsonResponse({'success': False, 'errors': form.errors}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Datos JSON no válidos'}, status=400)
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

# @csrf_exempt
@login_required
def crear_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            perfil = get_object_or_404(Perfil, user=request.user)
            cliente = get_object_or_404(Cliente, perfil=perfil)

            direccion_envio_id = data.get('direccion_envio_id')
            subtotal = float(data.get('subtotal', 0))
            iva = float(data.get('iva', 0))
            total = float(data.get('total', 0))
            productos = data.get('productos', [])

            if not productos:
                return JsonResponse({'success': False, 'error': 'El carrito está vacío.'})

            direccion_envio = Direccion.objects.get(id=direccion_envio_id, cliente=cliente)

            tienda_ids = set()
            for item in productos:
                try:
                    producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'])
                    tienda_ids.add(producto_tienda.tienda.id)
                except ProductosTiendas.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado.'})

            if len(tienda_ids) != 1:
                return JsonResponse({'success': False, 'error': 'Todos los productos deben pertenecer a la misma tienda.'})

            tienda_id = tienda_ids.pop()
            tienda = Tienda.objects.get(id=tienda_id)

            with transaction.atomic():

                orden = Orden.objects.create(
                    cliente=cliente,
                    tienda=tienda,
                    direccion_envio=direccion_envio,
                    subtotal=0,
                    iva=iva,
                    total=total,
                    estado='pendiente'
                )

                subtotal_orden = 0

                for item in productos:
                    try:
                        producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'], estado='activo')
                        cantidad = int(item['cantidad'])
                        precio_unitario = float(item['precio_unitario'])
                        subtotal_producto = cantidad * precio_unitario
                        subtotal_orden += subtotal_producto

                        # Crear ProductoOrden
                        ProductoOrden.objects.create(
                            orden=orden,
                            producto_tienda=producto_tienda,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario
                        )

                        producto_tienda.cantidad -= cantidad
                        producto_tienda.save()

                    except ProductosTiendas.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado o inactivo.'})

                orden.subtotal = subtotal_orden
                orden.save()

            return JsonResponse({'success': True, 'orden_id': orden.id})

        except Direccion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dirección de envío no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
def direccion(request):
    # Inicializar variables para cliente y tienda
    cliente = None
    tienda = None
    direcciones = None

    # Verificar si el usuario es un cliente
    if hasattr(request.user, 'cliente'):
        cliente = request.user.cliente
        direcciones = Direccion.objects.filter(cliente=cliente)

    # Verificar si el usuario es una tienda
    elif hasattr(request.user, 'tienda'):
        tienda = request.user.tienda
        direcciones = Direccion.objects.filter(tienda=tienda)

    # Manejar el formulario de creación o actualización de direcciones
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            if cliente:
                direccion.cliente = cliente
            elif tienda:
                direccion.tienda = tienda
            direccion.save()
            messages.success(request, 'Dirección registrada exitosamente.')
            return redirect('direccion')
        else:
            messages.error(request, 'Por favor, corrija los errores en el formulario.')

    else:
        form = DireccionForm()

    # Renderizar la plantilla con las direcciones y el formulario
    return render(request, 'otros/direccion.html', {
        'form': form,
        'direcciones': direcciones,
    })

logger = logging.getLogger(__name__)

@login_required
def registrar_direccion(request):
    if request.method == 'POST':
        # Obtener el cliente o la tienda asociados al usuario actual
        cliente = getattr(request.user, 'cliente', None)
        tienda = getattr(request.user, 'tienda', None)

        # Pasar el cliente o la tienda al formulario
        form = DireccionForm(request.POST, cliente=cliente, tienda=tienda)
        if form.is_valid():
            direccion = form.save(commit=False)

            # Asociar la dirección al cliente o tienda
            if cliente:
                direccion.cliente = cliente
            elif tienda:
                direccion.tienda = tienda
            else:
                return JsonResponse({'success': False, 'message': 'No se encontró un perfil asociado (cliente o tienda).'}, status=400)

            direccion.save()
            return JsonResponse({'success': True, 'message': 'Dirección registrada exitosamente.'})
            
        else:
            # Devolver los errores específicos del formulario
            return JsonResponse({'success': False, 'message': 'El formulario no es válido.', 'errors': form.errors}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)

@login_required
def eliminar_direccion(request, direccion_id):
    # Verificar si el usuario es un cliente o tienda
    cliente = getattr(request.user, 'cliente', None)
    tienda = getattr(request.user, 'tienda', None)

    # Buscar la dirección asociada al cliente o tienda
    if cliente:
        direccion = get_object_or_404(Direccion, id=direccion_id, cliente=cliente)
    elif tienda:
        direccion = get_object_or_404(Direccion, id=direccion_id, tienda=tienda)
    else:
        messages.error(request, 'No se encontró un perfil asociado para eliminar la dirección.')
        return redirect('direccion')

    # Eliminar la dirección si el método es POST
    if request.method == 'POST':
        direccion.delete()
        messages.success(request, 'Dirección eliminada correctamente.')
        return redirect('direccion')

    # Redirigir si no es un método POST
    return redirect('direccion')

@login_required
def actualizar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__user=request.user)

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            direccion = form.save(commit=False)
            cliente = Cliente.objects.get(user=request.user)
            if direccion.principal:
                Direccion.objects.filter(cliente=cliente, principal=True).update(principal=False)
            direccion.save()
            messages.success(request, 'La dirección ha sido actualizada correctamente.')
            return redirect('direccion_cliente')
        else:
            messages.error(request, 'Ha ocurrido un error al actualizar la dirección.')
    else:
        form = DireccionForm(instance=direccion)

    departamentos = Departamento.objects.all()
    ciudades = Ciudad.objects.filter(departamento=direccion.departamento)
    return render(request, 'clientes/direccion.html',
                  {'form': form, 'direccion': direccion, 'departamentos': departamentos, 'ciudades': ciudades})


def get_datos(request):
    if 'departamento' in request.GET:
        departamento_id = request.GET.get('departamento')
        ciudades = Ciudad.objects.filter(departamento_id=departamento_id)
        ciudades_list = list(ciudades.values('id', 'nombre'))
        return JsonResponse({'ciudades': ciudades_list})
    else:
        departamentos = Departamento.objects.all()
        departamentos_list = list(departamentos.values('id', 'nombre'))
        return JsonResponse({'departamentos': departamentos_list})


@login_required
@user_is_tienda
def promocion(request):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar promociones.")
        return redirect("index_tienda")

    if request.method == "POST":
        form = PromocionForm(request.POST)
        if form.is_valid():
            nueva_promocion = form.save(commit=False)
            nueva_promocion.tienda = tienda  # Asociar la promoción a la tienda del usuario
            nueva_promocion.save()
            form.save_m2m()  # Guardar las relaciones ManyToMany
            messages.success(request, "¡Promoción registrada exitosamente!")
            return redirect("promocion")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = PromocionForm()

    # Obtener las promociones asociadas a la tienda
    promociones = Promocion.objects.filter(tienda=tienda)

    # Obtener los productos asociados a la tienda
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)

    # Obtener todas las categorías
    categorias = Categoria.objects.all()

    return render(request, "tiendas/promocion.html", {
        "promociones": promociones,
        "productos_tiendas": productos_tiendas,
        "categorias": categorias,
        "form": form,
        "tienda": tienda,
    })

@login_required
@user_is_tienda
def editar_promocion(request, id):
    # Verificar que el usuario tiene una tienda asociada
    try:
        tienda = Tienda.objects.get(usuario=request.user)
    except Tienda.DoesNotExist:
        messages.error(request, "No tienes una tienda asociada para gestionar promociones.")
        return redirect("promocion")

    # Buscar la promoción y validar que pertenece a la tienda del usuario
    promocion = get_object_or_404(Promocion, id=id, tienda=tienda)

    if request.method == "POST":
        form = PromocionForm(request.POST, instance=promocion)
        if form.is_valid():
            form.save()
            messages.success(request, "¡Promoción actualizada exitosamente!")
            return redirect("promocion")
        else:
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = PromocionForm(instance=promocion)

    # Obtener los productos asociados a la tienda
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)

    # Obtener los IDs de los productos aplicables a la promoción
    productos_aplicables_ids = list(promocion.productos_aplicables.values_list("id", flat=True))

    context = {
        "form": form,
        "promocion": promocion,
        "productos_tiendas": productos_tiendas,
        "productos_aplicables_ids": productos_aplicables_ids,
    }

    return render(request, "tiendas/editar_promocion.html", context)

def eliminar_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)

    # Confirmación y eliminación
    if request.method == "POST":
        promocion.delete()
        messages.success(request, "Promoción eliminada correctamente.")
        return redirect('promocion')

    messages.error(request, "Acción no permitida.")
    return redirect('promocion')

def historial_compra(request):
    cliente = get_object_or_404(Cliente, perfil__user=request.user)

    ordenes_pendientes = Orden.objects.filter(cliente=cliente, estado=Orden.Estado.PENDIENTE)
    carrito = ordenes_pendientes.first() if ordenes_pendientes.exists() else None

    compras = Orden.objects.filter(cliente=cliente, estado=Orden.Estado.COMPLETADA).order_by('-fecha_creacion')[:5]

    context = {
        'cliente': cliente,
        'user': request.user,
        'carrito': carrito,
        'compras': compras,
        'ordenes_pendientes': ordenes_pendientes,
    }

    return render(request, 'otros/historial_p.html', context)

def inventario(request):
    return render(request, 'otros/inventario.html')

@login_required
def ordenes(request):
    # Obtener los perfiles del usuario que sean de tipo "tienda"
    perfiles = Perfil.objects.filter(user=request.user, rol__nombre="tienda")

    # Obtener todas las tiendas asociadas a esos perfiles
    tiendas_usuario = Tienda.objects.filter(perfil__in=perfiles)

    if not tiendas_usuario.exists():
        messages.error(request, "No tienes ninguna tienda registrada para gestionar órdenes.")
        return redirect("index_tienda")

    # Filtrar órdenes de todas las tiendas asociadas al usuario
    ordenes_no_completadas = Orden.objects.filter(tienda__in=tiendas_usuario).exclude(estado=Orden.Estado.COMPLETADA)
    ordenes_completadas = Orden.objects.filter(tienda__in=tiendas_usuario, estado=Orden.Estado.COMPLETADA)

    return render(request, "productos/ordenes.html", {
        "ordenes_no_completadas": ordenes_no_completadas,
        "ordenes_completadas": ordenes_completadas,
    })

