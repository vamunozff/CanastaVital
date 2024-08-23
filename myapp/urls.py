from django.urls import path
from .views import login, hello, index, exit, register, home, perfil, categoria, index_producto, index_proveedor, asignar_proveedor, register_cliente, perfil_tienda, index_cliente, login_view
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', home, name='home'),
    path('login/', login, name='login'),
    path('index/', index, name='index'),
    path('logout/', exit, name='exit'),
    path('register/', register, name='register'),
    path('perfil/', perfil, name='perfil'),
    path('perfil_tienda/', perfil_tienda, name='perfil_tienda'),
    path('index_cliente/', index_cliente, name='index_cliente'),
    path('categorias/', categoria, name='categorias'),
    path('asignarProducto/', views.asignarProducto),
    path('productos/eliminarPrductosTiendas/<int:id>', views.eliminarPrductosTiendas),
    path('productos/actualizarProductosTiendas/', views.actualizarProductosTiendas_list, name='actualizarProductosTiendas_list'),
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
    path('confirmar_completar/', views.confirmar_completar, name='confirmar_completar'),
    path('accounts/login/', login_view, name='login'),
    path('validate_cliente/', views.validate_cliente, name='validate_cliente'),
    path('validate_tienda/', views.validate_tienda, name='validate_tienda'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
