from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt, csrf_protect
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, ClienteForm, TiendaForm, DireccionForm
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Producto, ProductosTiendas, Proveedor, Cliente, Tienda, Promocion, Direccion, Orden, ProductoOrden
from django.contrib import messages
from .forms import ProductosTiendasForm
from django.db import transaction
import json
from django.http import JsonResponse
from django.utils import timezone
import logging
from django.core.exceptions import ValidationError
from django.db import IntegrityError

# Create your views here.
def hello(request):
    return HttpResponse("Bienvenido <a href='index.html'>Ingresar</a>")

def login(request):
    return render(request, 'registration/login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)

            es_cliente = Cliente.objects.filter(user=user).exists()
            es_tienda = Tienda.objects.filter(user=user).exists()

            if es_cliente and es_tienda:
                return JsonResponse({'success': True, 'role': 'both'})
            elif es_cliente:
                return JsonResponse({'success': True, 'role': 'cliente'})
            elif es_tienda:
                return JsonResponse({'success': True, 'role': 'tienda'})
            else:
                logout(request)
                return JsonResponse({'success': False, 'error': 'Usuario no registrado como cliente o tienda.'})
        else:
            return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos.'})

    return render(request, 'registration/login.html')

def home(request):
    return render(request, 'inicio/home.html')

@login_required
def index_tienda(request):
    return render(request, 'tiendas/index.html')
@login_required
def confirmar_completar(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'cliente':
            cliente_form = ClienteForm(request.POST, request.FILES)
            if cliente_form.is_valid():
                cliente = cliente_form.save(commit=False)
                cliente.user = request.user
                cliente.save()
                return redirect('index_cliente')
            else:
                print("Errores del formulario cliente:", cliente_form.errors)
                return render(request, 'registration/confirmar_completar.html', {
                    'cliente_form': cliente_form,
                    'tienda_form': TiendaForm()
                })

        elif form_type == 'tienda':
            tienda_form = TiendaForm(request.POST, request.FILES)
            if tienda_form.is_valid():
                tienda = tienda_form.save(commit=False)
                tienda.user = request.user
                tienda.save()
                return redirect('index_tienda')
            else:
                print("Errores del formulario tienda:", tienda_form.errors)
                return render(request, 'registration/confirmar_completar.html', {
                    'tienda_form': tienda_form,
                    'cliente_form': ClienteForm()
                })

    cliente_form = ClienteForm()
    tienda_form = TiendaForm()
    return render(request, 'registration/confirmar_completar.html', {
        'cliente_form': cliente_form,
        'tienda_form': tienda_form
    })

def exit(request):
    logout(request)
    return redirect(home)

def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('confirmar_completar')
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'registration/register.html', {'form': form})
@login_required
def perfil(request):
    cliente = get_object_or_404(Cliente, user=request.user)

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

    return render(request, 'clientes/perfil.html',{'cliente_form': cliente_form, 'cliente': cliente, 'user': request.user})
@login_required
def perfil_tienda(request):
    tienda = get_object_or_404(Tienda, user=request.user)

    if request.method == 'POST':
        form = TiendaForm(request.POST, request.FILES, instance=tienda)
        if form.is_valid():
            form.save()
            return redirect('perfil_tienda')
    else:
        form = TiendaForm(instance=tienda)
    return render(request, 'tiendas/perfil.html',{'form': form, 'tienda': tienda})
@login_required
def index_cliente(request):
    cliente = get_object_or_404(Cliente, user=request.user)
    return render(request, 'clientes/index.html', {'cliente': cliente, 'user': request.user})

@csrf_exempt
def validate_cliente(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()

        if user and Cliente.objects.filter(user=user).exists():
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False, 'error': 'Usuario no registrado como cliente.'})
@csrf_exempt
def validate_tienda(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user = User.objects.filter(username=username).first()

        if user and Tienda.objects.filter(user=user).exists():
            return JsonResponse({'valid': True})
        else:
            return JsonResponse({'valid': False, 'error': 'Usuario no registrado como tienda.'})

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
            tienda = get_object_or_404(Tienda, user=request.user)

            if not imagen:
                imagen = default_image_path

            producto = Producto.objects.get(id=producto_id)
            proveedor = Proveedor.objects.get(id=proveedor_id)

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

        except Producto.DoesNotExist:
            messages.error(request, 'El producto seleccionado no existe.')
        except Proveedor.DoesNotExist:
            messages.error(request, 'El proveedor seleccionado no existe.')
        except ValueError:
            messages.error(request, 'Por favor, ingrese un valor numérico válido para cantidad.')
        except Exception as e:
            messages.error(request, f'Error al asignar el producto: {str(e)}')

    tienda = get_object_or_404(Tienda, user=request.user)
    proveedores = Proveedor.objects.filter(productostiendas__usuario=request.user).distinct()
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
    productos = Producto.objects.all()
    tienda = get_object_or_404(Tienda, user=request.user)
    productos_tiendas = ProductosTiendas.objects.filter(tienda=tienda)
    proveedores = Proveedor.objects.filter(usuario=request.user, estado='activo')

    return render(request, 'productos/index.html',
                  {'productos': productos, 'productos_tiendas': productos_tiendas, 'proveedores': proveedores})
def ver_producto(request, id):
    producto_tienda = get_object_or_404(ProductosTiendas, id=id)
    return render(request, 'productos/ver_producto.html', {'producto_tienda': producto_tienda})

@login_required
def actualizar_producto(request, id):
    producto_tienda = get_object_or_404(ProductosTiendas, id=id)

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

    return render(request, 'productos/actualizar_producto.html', {
        'form': form,
        'producto_tienda': producto_tienda,
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
    proveedores = Proveedor.objects.filter(usuario=request.user)
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

            nuevo_proveedor = Proveedor(
                usuario=request.user,
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
        except Exception as e:
            messages.error(request, f'Error al asignar el proveedor: {str(e)}')

    proveedores = Proveedor.objects.filter(usuario=request.user)

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
    proveedores = get_object_or_404(Proveedor, id=id)

    if request.method == 'POST':
        try:
            razon_social = request.POST.get('txtRazonSocial')
            email = request.POST.get('txtEmail')
            telefono = request.POST.get('numTelefono')
            direccion = request.POST.get('txtdireccion')
            estado = request.POST.get('txtEstado')

            proveedores.razon_social = razon_social
            proveedores.email = email
            proveedores.telefono = telefono
            proveedores.direccion = direccion
            proveedores.estado = estado

            proveedores.full_clean()
            proveedores.save()

            messages.success(request, '¡Proveedor actualizado!')
            return redirect('index_proveedor')

        except ValueError:
            messages.error(request, 'Por favor, ingrese valores numéricos válidos para cantidad.')
        except Exception as e:
            messages.error(request, f'Error al actualizar el producto: {str(e)}')

    return render(request, 'proveedor/actualizar.html', {
        'proveedores': proveedores,
    })
def leer_proveedor(request, id):
    proveedores = get_object_or_404(Proveedor, id=id)
    return render(request, 'proveedor/leer.html', {'proveedores': proveedores})
@login_required
def register_cliente(request):
    if request.method == 'POST':
        cliente_form = ClienteForm(request.POST)
        if cliente_form.is_valid():
            cliente = cliente_form.save(commit=False)
            cliente.user = request.user
            cliente.save()
            return redirect('index')
        else:
            return render(request, 'registration/completar.html', {'cliente_form': cliente_form})
    else:
            cliente_form = ClienteForm()
            return render(request, 'registration/completar.html',  {'cliente_form': cliente_form})
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
    cliente = request.user.cliente
    direcciones = Direccion.objects.filter(cliente=cliente)
    direccion_principal = Direccion.objects.filter(cliente=cliente, principal=True).first()

    if request.method == 'POST':
        carrito = request.session.get('carrito', [])  # Suponiendo que el carrito se guarda en la sesión

        productos_en_tienda = []
        error = None

        for item in carrito:
            try:
                # Buscamos en la tabla ProductosTiendas usando producto_tienda_id
                producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'], estado='activo')

                productos_en_tienda.append({
                    'producto': producto_tienda,  # Producto en tienda relacionado
                    'nombre': producto_tienda.producto.nombre,  # Nombre del producto
                    'cantidad': item['cantidad'],  # Cantidad seleccionada
                    'precio_unitario': producto_tienda.precio_unitario,  # Precio unitario de ProductosTiendas
                    'subtotal': producto_tienda.precio_unitario * item['cantidad']  # Cálculo subtotal
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
        }

        return render(request, 'otros/confirmar_pago.html', context)

    # Renderizar la página de confirmación de pago en GET
    return render(request, 'otros/confirmar_pago.html', {
        'direcciones': direcciones,
        'direccion_principal': direccion_principal
    })


@csrf_exempt
@login_required
def crear_direccion(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            # Crear un formulario con los datos recibidos
            form = DireccionForm(data)

            if form.is_valid():
                nueva_direccion = form.save(commit=False)
                # Asignar el cliente o tienda según corresponda
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

@csrf_exempt
@login_required
def crear_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            cliente = request.user.cliente
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
                    subtotal=subtotal,
                    iva=iva,
                    total=total,
                    estado='pendiente'
                )

                for item in productos:
                    try:
                        producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'], estado='activo')
                        cantidad = int(item['cantidad'])
                        precio_unitario = float(item['precio_unitario'])
                        subtotal_producto = cantidad * precio_unitario

                        if producto_tienda.cantidad < cantidad:
                            raise ValueError(f"Producto {producto_tienda.producto.nombre} no tiene suficiente stock.")

                        ProductoOrden.objects.create(
                            orden=orden,
                            producto_tienda=producto_tienda,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario,
                            subtotal=subtotal_producto
                        )

                        producto_tienda.cantidad -= cantidad
                        producto_tienda.save()

                    except ProductosTiendas.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado o inactivo.'})

            return JsonResponse({'success': True, 'orden_id': orden.id})
        except Direccion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dirección de envío no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)

@login_required  # Asegura que solo los usuarios autenticados puedan registrar una dirección
def direccion_cliente(request):
    # Obtener el cliente autenticado
    cliente = Cliente.objects.get(user=request.user)

    if request.method == 'POST':
        # Obtener los datos del formulario
        direccion = request.POST.get('direccion')
        ciudad = request.POST.get('ciudad')
        departamento = request.POST.get('departamento')
        codigo_postal = request.POST.get('codigo_postal')
        principal = request.POST.get('principal', False)  # Si no se selecciona, se define como False

        # Si el checkbox "principal" está seleccionado, desmarcar otras direcciones como principales
        if principal:
            Direccion.objects.filter(cliente=cliente, principal=True).update(principal=False)

        # Crear y guardar la nueva dirección
        nueva_direccion = Direccion(
            direccion=direccion,
            ciudad=ciudad,
            departamento=departamento,
            codigo_postal=codigo_postal,
            principal=principal,
            cliente=cliente  # Relacionar la dirección con el cliente
        )

        nueva_direccion.save()

        # Enviar un mensaje de éxito y redirigir a la página de direcciones
        messages.success(request, 'Dirección registrada correctamente.')
        return redirect('direccion_cliente')  # Asegúrate de que este nombre coincida con tu URL

    # Obtener todas las direcciones del cliente para mostrarlas en la página
    direcciones = Direccion.objects.filter(cliente=cliente)

    context = {
        'direcciones': direcciones
    }
    return render(request, 'clientes/direccion.html', context)

@login_required
def eliminar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__user=request.user)

    if request.method == 'POST':
        direccion.delete()
        messages.success(request, 'Dirección eliminada correctamente.')
        return redirect('direccion_cliente')  # Asegúrate de que 'direccion_cliente' es la URL donde se muestran las direcciones

    return redirect('direccion_cliente')


@login_required
def actualizar_direccion(request, direccion_id):
    direccion = get_object_or_404(Direccion, id=direccion_id, cliente__user=request.user)

    if request.method == 'POST':
        form = DireccionForm(request.POST, instance=direccion)
        if form.is_valid():
            form.save()
            messages.success(request, 'Dirección actualizada correctamente.')
            return redirect(
                'direccion_cliente')  # Asegúrate de que 'direccion_cliente' es la URL de la vista de direcciones
    else:
        form = DireccionForm(instance=direccion)

    return render(request, 'clientes/actualizar_direccion.html', {'form': form, 'direccion': direccion})


@login_required
def registrar_direccion(request):
    if request.method == 'POST':
        form = DireccionForm(request.POST)
        if form.is_valid():
            direccion = form.save(commit=False)
            direccion.cliente = Cliente.objects.get(user=request.user)
            if direccion.principal:
                Direccion.objects.filter(cliente=direccion.cliente, principal=True).update(principal=False)
            direccion.save()
            messages.success(request, 'Dirección registrada correctamente.')
            return redirect('direccion_cliente')
        else:
            messages.error(request, 'Error al registrar la dirección. Verifica los campos del formulario.')
    else:
        form = DireccionForm()

    return render(request, 'clientes/direccion.html', {'form': form})
