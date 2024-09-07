from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import logout
from .forms import CustomUserCreationForm, ClienteForm, TiendaForm
from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse
from django.contrib.auth.models import User
from .models import Producto, ProductosTiendas, Proveedor, Cliente, Tienda
from django.contrib import messages
from .forms import ProductosTiendasForm
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
                return JsonResponse({'success': False, 'error': 'Usuario no registrado como cliente o tienda.'})
        else:
            return JsonResponse({'success': False, 'error': 'Usuario o contraseña incorrectos.'})

    return render(request, 'registration/login.html')

def home(request):
    return render(request, 'inicio/home.html')

@login_required
def index(request):
    return render(request, 'tiendas/index.html')
@login_required
def confirmar_completar(request):
    if request.method == 'POST':
        form_type = request.POST.get('form_type')

        if form_type == 'cliente':
            cliente_form = ClienteForm(request.POST)
            if cliente_form.is_valid():
                cliente = cliente_form.save(commit=False)
                cliente.user = request.user
                cliente.save()
                return redirect('index_cliente')
            else:
                return render(request, 'registration/confirmar_completar.html', {
                    'cliente_form': cliente_form,
                    'tienda_form': TiendaForm()
                })

        elif form_type == 'tienda':
            tienda_form = TiendaForm(request.POST, request.FILES)
            if tienda_form.is_valid():
                print("Formulario válido")
                tienda = tienda_form.save(commit=False)
                tienda.user = request.user
                tienda.save()
                return redirect('index')
            else:
                print("Errores del formulario:", tienda_form.errors)
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

            if not imagen:
                imagen = default_image_path

            producto = Producto.objects.get(id=producto_id)
            proveedor = Proveedor.objects.get(id=proveedor_id)

            nuevo_producto_tienda = ProductosTiendas(
                producto=producto,
                proveedor=proveedor,
                usuario=request.user,
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

    proveedores = Proveedor.objects.filter(productostiendas__usuario=request.user).distinct()
    productos_tiendas = ProductosTiendas.objects.filter(usuario=request.user)

    return render(request, 'productos/index.html', {
        'productos': Producto.objects.all(),
        'proveedores': proveedores,
        'productos_tiendas': productos_tiendas
    })

def actualizarProductosTiendas_list(request):
    pass
def eliminarPrductosTiendas(request, id):
    productosTiendas = ProductosTiendas.objects.get(id=id)
    productosTiendas.delete()
    messages.success(request, 'Producto eliminado correctamente.')
    return redirect('productos')
@login_required
def index_producto(request):
    productos = Producto.objects.all()
    if request.user.is_authenticated:
        productos_tiendas = ProductosTiendas.objects.filter(usuario=request.user)
        proveedores = Proveedor.objects.filter(usuario=request.user)

        print(f"Proveedores para el usuario {request.user.username}:")
        for proveedor in proveedores:
            print(proveedor.razon_social)

        return render(request, 'productos/index.html',
                      {'productos': productos, 'productos_tiendas': productos_tiendas, 'proveedores': proveedores})
    else:
        messages.warning(request, 'Debe iniciar sesión para visualizar los productos asignados.')
        return render(request, 'productos/index.html', {'productos': productos})
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

def busqueda_tiendas(request):
    tiendas = Tienda.objects.all()
    return render(request, 'tiendas/busqueda.html', {'tiendas': tiendas})