from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from .forms import CustomUserCreationForm, ClienteForm, TiendaForm, DireccionForm
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth import logout
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from .models import Rol, Perfil, Producto, ProductosTiendas, Proveedor, Cliente, Tienda, Promocion, Direccion, Orden, ProductoOrden, Ciudad, Departamento
from django.contrib import messages
from .forms import ProductosTiendasForm, PromocionForm
from django.db import transaction
import json
from decimal import Decimal
from .decorators import user_is_tienda, user_is_cliente, user_is_administrador
from django.utils import timezone
import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your views here.
def hello(request):
    return HttpResponse("Bienvenido <a href='index.html'>Ingresar</a>")

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            messages.success(request, 'Inicio de sesión exitoso.')

            if user.perfil.rol.nombre == 'administrador':
                return redirect('index_administrador')
            elif user.perfil.rol.nombre == 'tienda':
                return redirect('index_tienda')
            elif user.perfil.rol.nombre == 'cliente':
                return redirect('index_cliente')
        else:

            messages.error(request, 'Credenciales incorrectas. Por favor intenta nuevamente.')
            return redirect('login')

    return render(request, 'registration/login.html')

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
    return render(request, 'inicio/home.html')

def completar_registro(request):
    return render(request, 'registration/confirmar_completar.html')

@login_required
def index_tienda(request):
    return render(request, 'tiendas/index.html')

def logout_view(request):
    logout(request)
    messages.success(request, 'Has cerrado sesión exitosamente.')
    return redirect('login')

# @csrf_exempt
from django.shortcuts import redirect

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            user = form.save(commit=False)
            user.first_name = request.POST.get('first_name')
            user.last_name = request.POST.get('last_name')
            user.email = form.cleaned_data['email']
            user.save()

            rol_name = request.POST.get('rol')
            rol = Rol.objects.get(nombre=rol_name)
            Perfil.objects.create(user=user, rol=rol)

            login(request, user)
            return redirect('completar_registro')
        else:
            # No es necesario manejar los errores manualmente aquí, ya que se manejarán en el HTML
            return render(request, 'registration/register.html', {'form': form})

    elif request.method == 'GET':
        form = CustomUserCreationForm()
        return render(request, 'registration/register.html', {'form': form})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@user_is_cliente
@login_required
def perfil_cliente(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    cliente = get_object_or_404(Cliente, perfil=perfil)

    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST, request.FILES, instance=cliente)
        if cliente_form.is_valid():
            cliente_form.save()
            messages.success(request, 'Perfil actualizado exitosamente.')
            return redirect('perfil')
        else:
            messages.error(request, 'Error al actualizar el perfil.')
    else:
        cliente_form = ClienteForm(instance=cliente)

    return render(request, 'clientes/perfil.html', {
        'cliente_form': cliente_form,
        'cliente': cliente,
        'user': request.user
    })

@login_required
def perfil_tienda(request):

    try:
        tienda = request.user.perfil.tienda
    except Tienda.DoesNotExist:

        tienda = Tienda.objects.create(perfil=request.user.perfil)
        messages.success(request, "Tu tienda ha sido creada exitosamente.")

    if request.method == 'POST':
        tienda.nombre = request.POST.get('nombre', tienda.nombre)
        tienda.horarios = request.POST.get('horarios', tienda.horarios)
        tienda.telefono = request.POST.get('telefono', tienda.telefono)
        tienda.descripcion = request.POST.get('descripcion', tienda.descripcion)

        if 'logo_url' in request.FILES:
            tienda.logo_url = request.FILES['logo_url']

        tienda.save()
        messages.success(request, "Datos de la tienda actualizados exitosamente.")

    direccion = tienda.direcciones.first()

    return render(request, 'tiendas/perfil.html', {'tienda': tienda, 'direccion': direccion})

@login_required
def index_cliente(request):
    cliente = get_object_or_404(Cliente, perfil__user=request.user)
    return render(request, 'clientes/index.html', {'cliente': cliente, 'user': request.user})

@login_required
def index_administrador(request):

    return render(request, 'administrador/index.html')

def categoria(request):
    return render(request, 'categorias/categorias.html')

@login_required
def asignarProducto(request):
    if request.method == 'POST':
        try:
            producto_id = int(request.POST.get('txtProducto_id'))
            proveedor_id = int(request.POST.get('txtProveedor_id'))
            precio_unitario = request.POST.get('txtPrecioUnitario')
            cantidad = int(request.POST.get('txtCantidad'))
            estado = request.POST.get('txtEstado')
            imagen = request.FILES.get('logo_url')

            default_image_path = 'productos_tiendas/Default.jpg'
            tienda = get_object_or_404(Tienda, perfil__user=request.user)

            if not imagen:
                imagen = default_image_path

            producto = get_object_or_404(Producto, id=producto_id)
            proveedor = get_object_or_404(Proveedor, id=proveedor_id)

            nuevo_producto_tienda = ProductosTiendas(
                producto=producto,
                proveedor=proveedor,
                tienda=tienda,
                precio_unitario=precio_unitario,
                cantidad=cantidad,
                estado=estado,
                imagen=imagen
            )

            nuevo_producto_tienda.full_clean()
            nuevo_producto_tienda.save()

            messages.success(request, 'Producto asignado correctamente.')
            return redirect('index_producto')

        except ValueError:
            messages.error(request, 'Por favor, ingrese un valor numérico válido para cantidad o precio.')
        except Exception as e:
            messages.error(request, f'Error al asignar el producto: {str(e)}')

    tienda = get_object_or_404(Tienda, perfil__user=request.user)
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
def index_producto(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    tienda = get_object_or_404(Tienda, perfil=perfil)
    proveedores = Proveedor.objects.filter(tienda=tienda)
    productos = Producto.objects.all()
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)

    return render(request, 'productos/index.html', {
        'productos': productos,
        'productos_tiendas': productos_tiendas,
        'proveedores': proveedores
    })

@login_required
def actualizar_producto(request, id):
    producto_tienda = get_object_or_404(ProductosTiendas, id=id)

    # Verificar que el producto pertenezca a la tienda del usuario
    if producto_tienda.tienda != request.user.perfil.tienda:
        messages.error(request, 'No tienes permiso para actualizar este producto.')
        return redirect('index_producto')

    if request.method == 'POST':
        form = ProductosTiendasForm(request.POST, request.FILES, instance=producto_tienda)

        if form.is_valid():
            form.save()
            messages.success(request, '¡Producto actualizado!')
            return redirect('index_producto')
        else:
            # Print errors for debugging
            for field in form:
                print(f"Errores en el campo {field.label}: {field.errors}")
            print("Errores generales del formulario:", form.non_field_errors())
            messages.error(request, 'Por favor, corrija los errores en el formulario.')

    else:
        form = ProductosTiendasForm(instance=producto_tienda)

    # Obtener promociones activas para este producto
    promociones_activas = Promocion.objects.filter(
        productos_aplicables=producto_tienda,
        activo=True,
        fecha_inicio__lte=timezone.now(),
        fecha_fin__gte=timezone.now()
    )

    return render(request, 'productos/actualizar_producto.html', {
        'form': form,
        'producto_tienda': producto_tienda,
        'promociones_activas': promociones_activas,  # Pasar promociones activas al contexto
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
def index_proveedor(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    tienda = get_object_or_404(Tienda, perfil=perfil)
    proveedores = Proveedor.objects.filter(tienda=tienda)
    return render(request, 'proveedor/index.html',{'proveedores': proveedores})


@login_required
def asignar_proveedor(request):
    if request.method == 'POST':
        try:
            razon_social = request.POST.get('txtRazonSocial')
            email = request.POST.get('txtEmail')
            telefono = request.POST.get('numTelefono')
            direccion = request.POST.get('txtdireccion')
            estado = request.POST.get('txtEstado')

            perfil = Perfil.objects.get(user=request.user)
            tienda = Tienda.objects.get(perfil=perfil)

            nuevo_proveedor = Proveedor(
                tienda=tienda,
                razon_social=razon_social,
                email=email,
                telefono=telefono,
                direccion=direccion,
                estado=estado
            )

            nuevo_proveedor.full_clean()
            nuevo_proveedor.save()

            messages.success(request, 'Proveedor registrado correctamente.')
            return redirect('index_proveedor')

        except ValueError as ve:
            messages.error(request, f'Error de valor al asignar el proveedor: {str(ve)}')
        except Tienda.DoesNotExist:
            messages.error(request, 'No se encontró una tienda asociada al usuario.')
        except Exception as e:
            messages.error(request, f'Error al asignar el proveedor: {str(e)}')

    perfil = Perfil.objects.get(user=request.user)
    tienda = Tienda.objects.get(perfil=perfil)
    proveedores = Proveedor.objects.filter(tienda=tienda)

    return render(request, 'proveedor/index.html', {'proveedores': proveedores})

@login_required
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == "POST":
        proveedor.delete()
        messages.success(request, '¡Proveedor eliminado correctamente!')
        return redirect('index_proveedor')

    return redirect('index_proveedor')

@login_required
def actualizar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        try:
            razon_social = request.POST.get('txtRazonSocial')
            email = request.POST.get('txtEmail')
            telefono = request.POST.get('numTelefono')
            direccion = request.POST.get('txtdireccion')
            estado = request.POST.get('txtEstado')

            if proveedor.tienda.perfil.user != request.user:
                messages.error(request, 'No tienes permiso para actualizar este proveedor.')
                return redirect('index_proveedor')

            proveedor.razon_social = razon_social
            proveedor.email = email
            proveedor.telefono = telefono
            proveedor.direccion = direccion
            proveedor.estado = estado

            proveedor.full_clean()
            proveedor.save()

            messages.success(request, '¡Proveedor actualizado correctamente!')
            return redirect('index_proveedor')

        except ValueError:
            messages.error(request, 'Por favor, ingrese valores válidos.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el proveedor: {str(e)}')

    return render(request, 'proveedor/actualizar.html', {
        'proveedor': proveedor,
    })


@login_required
def register_cliente(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST, request.FILES)

        if cliente_form.is_valid():
            try:
                perfil = Perfil.objects.get(user=request.user)  # Verificar que el perfil existe
            except Perfil.DoesNotExist:
                messages.error(request, 'No se encontró el perfil asociado. Por favor, complete el registro primero.')
                return redirect('index_cliente')  # Redirigir si no hay perfil

            cliente = cliente_form.save(commit=False)  # Guardar cliente sin comprometer aún en la DB
            cliente.perfil = perfil  # Asignar el perfil al cliente
            cliente.save()  # Guardar el cliente en la base de datos
            messages.success(request, 'El cliente se ha registrado exitosamente.')
            return redirect('index_cliente')  # Redirigir al index_cliente

        else:
            for field, error_list in cliente_form.errors.items():
                for error in error_list:
                    messages.error(request, f'Error en {field}: {error}')

    else:
        cliente_form = ClienteForm()

    context = {
        'cliente_form': cliente_form
    }
    return render(request, 'registration/confirmar_completar.html', context)

@login_required
def register_tienda(request):
    if request.method == 'POST':
        tienda_form = TiendaForm(request.POST, request.FILES)

        if tienda_form.is_valid():
            try:
                perfil = Perfil.objects.get(user=request.user)  # Verifica si el perfil existe
            except Perfil.DoesNotExist:
                messages.error(request, 'No se encontró el perfil asociado. Por favor, complete el registro primero.')
                return redirect('index_tienda')

            # Validar que el usuario tenga el rol de "tienda"
            if perfil.rol.nombre != 'tienda':
                messages.error(request, 'No tiene permiso para registrar una tienda.')
                return redirect('index_tienda')

            tienda = tienda_form.save(commit=False)  # Guarda la tienda sin comprometerla aún
            tienda.perfil = perfil  # Asociar la tienda al perfil del usuario
            tienda.save()  # Guardar la tienda en la base de datos

            messages.success(request, 'La tienda se ha registrado exitosamente.')
            return redirect('index_tienda')  # Redirigir al index de tiendas

        else:
            for field, error_list in tienda_form.errors.items():
                for error in error_list:
                    messages.error(request, f'Error en {field}: {error}')

    else:
        tienda_form = TiendaForm()  # Inicializar el formulario si es GET

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
    productosTiendas = ProductosTiendas.objects.filter(tienda=tienda, estado='activo').select_related('producto', 'proveedor')
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

    perfil = request.user.perfil
    cliente = getattr(perfil, 'cliente', None)

    if not cliente:
        return JsonResponse({'error': 'No tienes un perfil de cliente asociado.'})

    direcciones = Direccion.objects.filter(cliente=cliente)
    form = DireccionForm()
    direccion_principal = Direccion.objects.filter(cliente=cliente, principal=True).first()

    departamentos = Departamento.objects.all()
    ciudad = Ciudad.objects.all()

    if request.method == 'POST':
        carrito = request.session.get('carrito', [])

        if not carrito:
            return JsonResponse({'error': 'El carrito está vacío.'})

        productos_en_tienda = []
        error = None

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
                error = f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado o inactivo.'
                break

        if error:
            return JsonResponse({'error': error})

        total = sum(item['subtotal'] for item in productos_en_tienda)

        context = {
            'direcciones': direcciones,
            'direccion_principal': direccion_principal,
            'productos_en_tienda': productos_en_tienda,
            'total': total,
            'form': form,
            'departamentos': departamentos,
            'ciudad': ciudad,
        }

        return render(request, 'otros/confirmar_pago.html', context)

    return render(request, 'otros/confirmar_pago.html', {
        'direcciones': direcciones,
        'direccion_principal': direccion_principal,
        'departamentos': departamentos,
        'ciudad': ciudad,
    })

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

            # Obtener el perfil del usuario y luego el cliente
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

                        # Actualizar el stock del producto
                        producto_tienda.cantidad -= cantidad
                        producto_tienda.save()

                    except ProductosTiendas.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado o inactivo.'})

                # Actualizar el subtotal y guardar la orden
                orden.subtotal = subtotal_orden
                orden.save()

            # Retornar una respuesta exitosa
            return JsonResponse({'success': True, 'orden_id': orden.id})

        except Direccion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dirección de envío no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)


@login_required
def direccion(request):
    try:
        # Intentamos obtener el perfil del cliente si existe
        cliente = Cliente.objects.get(perfil__user=request.user)
        direcciones = Direccion.objects.filter(cliente=cliente)
    except Cliente.DoesNotExist:
        cliente = None
        direcciones = None

    try:
        # Intentamos obtener el perfil de la tienda si existe
        tienda = Tienda.objects.get(perfil__user=request.user)
        direcciones_tienda = Direccion.objects.filter(tienda=tienda)
    except Tienda.DoesNotExist:
        tienda = None
        direcciones_tienda = None

    # Procesamos el formulario de nueva dirección
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            # Si el usuario es un cliente, asignamos la dirección al cliente
            if cliente:
                direccion.cliente = cliente
            # Si el usuario es una tienda, asignamos la dirección a la tienda
            elif tienda:
                direccion.tienda = tienda
            direccion.save()
            return redirect('direccion')
    else:
        form = DireccionForm()

    # Unimos ambas listas de direcciones, si existen
    todas_direcciones = list(direcciones or []) + list(direcciones_tienda or [])

    return render(request, 'otros/direccion.html', {
        'form': form,
        'direcciones': todas_direcciones,
    })

@login_required
def registrar_direccion(request):
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            try:
                direccion = form.save(commit=False)
                perfil = request.user.perfil
                cliente = getattr(perfil, 'cliente', None)
                tienda = getattr(perfil, 'tienda', None)

                if cliente:
                    direccion.cliente = cliente
                    # Verificar si es la dirección principal y actualizar las otras
                    if direccion.principal:
                        Direccion.objects.filter(cliente=cliente, principal=True).update(principal=False)
                    direccion.save()
                    return JsonResponse({'success': True}, status=200)

                elif tienda:
                    direccion.tienda = tienda
                    # Verificar si es la dirección principal y actualizar las otras
                    if direccion.principal:
                        Direccion.objects.filter(tienda=tienda, principal=True).update(principal=False)
                    direccion.save()
                    return JsonResponse({'success': True}, status=200)

                else:
                    return JsonResponse({'success': False, 'message': 'No se encontró un perfil asociado (cliente o tienda).'},
                                        status=400)
            except Exception as e:
                print(str(e))
                return JsonResponse({'success': False, 'message': 'Ocurrió un error al registrar la dirección.'},
                                    status=500)
        else:
            return JsonResponse({'success': False, 'message': 'El formulario no es válido.'}, status=400)
    return JsonResponse({'success': False, 'message': 'Método no permitido.'}, status=405)


@login_required
def eliminar_direccion(request, direccion_id):
    perfil = get_object_or_404(Perfil, user=request.user)

    # Verificar si el perfil es de un cliente o de una tienda
    cliente = getattr(perfil, 'cliente', None)
    tienda = getattr(perfil, 'tienda', None)

    if cliente:
        direccion = get_object_or_404(Direccion, id=direccion_id, cliente=cliente)
    elif tienda:
        direccion = get_object_or_404(Direccion, id=direccion_id, tienda=tienda)
    else:
        messages.error(request, 'No se encontró un perfil asociado para eliminar la dirección.')
        return redirect('direccion')

    if request.method == 'POST':
        direccion.delete()
        messages.success(request, 'Dirección eliminada correctamente.')
        return redirect('direccion')

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
def promocion(request):
    perfil = get_object_or_404(Perfil, user=request.user)
    tienda = get_object_or_404(Tienda, perfil=perfil)

    # Manejo del formulario para registrar una nueva promoción
    if request.method == 'POST':
        form = PromocionForm(request.POST)
        if form.is_valid():
            nueva_promocion = form.save(commit=False)
            nueva_promocion.tienda = tienda  # Asigna la tienda al objeto promoción
            nueva_promocion.save()
            form.save_m2m()  # Guarda la relación ManyToManyField para productos aplicables

            # Agrega un mensaje de éxito
            messages.success(request, '¡Promoción registrada exitosamente!')

            return redirect('promocion')  # Redirige a la página de éxito o a la misma vista
    else:
        form = PromocionForm()

    # Consulta las promociones y productos aplicables
    promociones = Promocion.objects.filter(tienda=tienda)
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)

    return render(request, 'tiendas/promocion.html', {
        'promociones': promociones,
        'productos_tiendas': productos_tiendas,
        'form': form,  # Asegúrate de pasar el formulario al contexto
    })

@login_required
def editar_promocion(request, id):
    perfil = get_object_or_404(Perfil, user=request.user)
    tienda = get_object_or_404(Tienda, perfil=perfil)
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)
    promocion = get_object_or_404(Promocion, id=id)

    if request.method == 'POST':
        form = PromocionForm(request.POST, instance=promocion)

        if form.is_valid():
            # Obtener el descuento del formulario
            descuento_input = request.POST.get('descuento', '')

            try:
                # Reemplaza la coma por un punto y convierte a Decimal
                if descuento_input:
                    # Quita los puntos y cambia la coma por un punto
                    descuento_decimal = Decimal(descuento_input.replace('.', '').replace(',', '.'))
                    form.cleaned_data['descuento'] = descuento_decimal

                # Si todo está bien, guarda la promoción
                form.save()
                return redirect('promocion')

            except (ValueError, ValidationError):
                form.add_error('descuento', 'Ingrese un número válido.')
                # Renderizar el formulario de nuevo en caso de error
                context = {
                    'form': form,
                    'promocion': promocion,
                    'productos_tiendas': productos_tiendas,
                    'productos_aplicables_ids': list(promocion.productos_aplicables.values_list('id', flat=True)),
                }
                return render(request, 'tiendas/editar_promocion.html', context)

    else:
        form = PromocionForm(instance=promocion)

    # Obtener los IDs de los productos aplicables
    productos_aplicables_ids = promocion.productos_aplicables.values_list('id', flat=True)

    context = {
        'form': form,
        'promocion': promocion,
        'productos_tiendas': productos_tiendas,
        'productos_aplicables_ids': list(productos_aplicables_ids),
    }
    return render(request, 'tiendas/editar_promocion.html', context)

def eliminar_promocion(request, id):
    promocion = get_object_or_404(Promocion, id=id)

    # Confirmación y eliminación
    if request.method == "POST":
        promocion.delete()
        messages.success(request, "Promoción eliminada correctamente.")
        return redirect('promocion')

    # Si la solicitud no es POST, redirige o muestra error
    messages.error(request, "Acción no permitida.")
    return redirect('promocion')