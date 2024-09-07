from django.contrib import admin
from .models import Categoria, Producto, ProductosTiendas, Proveedor,Cliente, Tienda, Promocion, Venta, DetalleVenta, Inventario, MetodoPago, AtencionCliente, Direccion
from django.utils.html import mark_safe

@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo', 'categoria', 'descripcion', 'fecha_registro')
    search_fields = ('nombre', 'codigo', 'descripcion')
    list_filter = ('categoria', 'fecha_registro')
    ordering = ('nombre',)

@admin.register(ProductosTiendas)
class ProductosTiendasAdmin(admin.ModelAdmin):
    list_display = ('producto', 'proveedor', 'usuario', 'precio_unitario', 'cantidad', 'estado', 'fecha_registro', 'imagen_preview')
    list_filter = ('estado', 'fecha_registro', 'producto__categoria', 'proveedor')
    search_fields = ('producto__nombre', 'proveedor__razon_social', 'usuario__username')
    list_per_page = 20

    fieldsets = (
        ('Información General', {
            'fields': ('producto', 'proveedor', 'usuario', 'imagen')
        }),
        ('Detalles de Inventario', {
            'fields': ('precio_unitario', 'cantidad', 'estado', 'fecha_registro')
        }),
    )

    readonly_fields = ('fecha_registro',)

    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.select_related('producto', 'proveedor', 'usuario')
        return queryset

    def imagen_preview(self, obj):
        if obj.imagen:
            return mark_safe(f'<img src="{obj.imagen.url}" width="50" height="50" />')
        return "No Image"

    imagen_preview.short_description = 'Vista Previa'

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('usuario', 'razon_social', 'email', 'telefono', 'estado', 'fecha_registro')
    search_fields = ('razon_social', 'email', 'telefono')
    list_filter = ('usuario', 'estado', 'fecha_registro')
    ordering = ('razon_social',)

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('user', 'tipo_documento', 'numero_documento', 'telefono', 'fecha_nacimiento', 'fecha_registro', 'imagen_perfil')
    list_filter = ('tipo_documento', 'fecha_nacimiento')
    search_fields = ('user__username', 'numero_documento')
    ordering = ('-fecha_registro',)

    fields = ('user', 'telefono', 'fecha_nacimiento', 'tipo_documento', 'numero_documento', 'imagen_perfil')
    readonly_fields = ('fecha_registro',)

@admin.register(Direccion)
class DireccionAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal')
    search_fields = ('direccion', 'ciudad', 'departamento', 'codigo_postal')
    list_filter = ('ciudad', 'departamento', 'principal')
    ordering = ('-cliente',)

    fieldsets = (
        (None, {
            'fields': ('cliente', 'direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal')
        }),
    )

@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'direccion', 'telefono', 'fecha_registro')
    search_fields = ('nombre', 'user__username', 'direccion')
    list_filter = ('fecha_registro',)

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'tienda', 'descuento', 'tipo_descuento', 'fecha_inicio', 'fecha_fin', 'activo')
    search_fields = ('nombre', 'tienda__nombre')
    list_filter = ('activo', 'fecha_inicio', 'fecha_fin')

@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'fecha', 'total')
    search_fields = ('cliente__user__username', 'fecha')
    list_filter = ('fecha',)

@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ('venta', 'producto_tienda', 'cantidad', 'precio')
    search_fields = ('venta__id', 'producto_tienda__producto__nombre')
    list_filter = ('venta__fecha',)

@admin.register(Inventario)
class InventarioAdmin(admin.ModelAdmin):
    list_display = ('producto_tienda', 'tienda', 'cantidad')
    search_fields = ('producto_tienda__producto__nombre', 'tienda__nombre')
    list_filter = ('tienda',)

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('tipo', 'descripcion')
    search_fields = ('tipo',)

@admin.register(AtencionCliente)
class AtencionClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'asunto', 'estado', 'fecha_creacion')
    search_fields = ('cliente__user__username', 'asunto')
    list_filter = ('estado', 'fecha_creacion')
