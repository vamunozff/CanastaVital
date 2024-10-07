from django.urls import path
from .views import completar_registro, hello, index_administrador, index_tienda, logout_view, register, home, perfil_cliente, categoria, index_producto, index_proveedor, asignar_proveedor, perfil_tienda, index_cliente, login_view, busqueda_tiendas, busqueda_productos, get_datos
from . import views
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('completar_registro', completar_registro, name='completar_registro'),
    path('accounts/login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('index_tienda/', index_tienda, name='index_tienda'),
    path('register/', views.register, name='register'),
    path('perfil_cliente/', perfil_cliente, name='perfil_cliente'),
    path('perfil_tienda/', perfil_tienda, name='perfil_tienda'),
    path('index_cliente/', index_cliente, name='index_cliente'),
    path('index_administrador/', index_administrador, name='index_administrador'),
    path('categorias/', categoria, name='categorias'),
    path('asignarProducto/', views.asignarProducto),
    path('index_producto/', index_producto, name='index_producto'),
    path('index_producto/ver_producto/<int:id>/', views.ver_producto, name='ver_producto'),
    path('index_producto/actualizar_producto/<int:id>/', views.actualizar_producto, name='actualizar_producto'),
    path('index_producto/actualizar_producto/', views.actualizar_producto, name='actualizar_producto_list'),
    path('index_producto/eliminar_producto/<int:id>/', views.eliminar_producto, name='eliminar_producto'),
    path('index_proveedor/', index_proveedor, name='index_proveedor'),
    path('asignar_proveedor/', views.asignar_proveedor),
    path('index_proveedor/eliminar_proveedor/<int:id>/', views.eliminar_proveedor, name='eliminar_proveedor'),
    path('index_proveedor/actualizar_proveedor/<int:id>/', views.actualizar_proveedor, name='actualizar_proveedor'),
    path('index_proveedor/leer_proveedor/<int:id>/', views.leer_proveedor, name='leer_proveedor'),

    path('register_cliente/', views.register_cliente, name='register_cliente'),
    path('register_tienda/', views.register_tienda, name='register_tienda'),

    path('busqueda_tiendas/', busqueda_tiendas, name='busqueda_tiendas'),
    path('productos/busqueda_productos/<int:tienda_id>/', busqueda_productos, name='busqueda_productos'),
    path('confirmar_pago/', views.confirmar_pago, name='confirmar_pago'),
    path('api/crear_direccion/', views.crear_direccion, name='crear_direccion'),
    path('api/crear_orden/', views.crear_orden, name='crear_orden'),
    path('direccion/', views.direccion, name='direccion'),
    path('registrar-direccion/', views.registrar_direccion, name='registrar_direccion'),
    path('eliminar_direccion/<int:direccion_id>/', views.eliminar_direccion, name='eliminar_direccion'),
    path('actualizar_direccion/<int:direccion_id>/', views.actualizar_direccion, name='actualizar_direccion'),
    path('get-datos/', get_datos, name='get_datos'),
    path('promocion/', views.promocion, name='promocion'),
    path('promocion/editar/<int:id>/', views.editar_promocion, name='editar_promocion'),
    path('promocion/eliminar/<int:id>/', views.eliminar_promocion, name='eliminar_promocion'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
