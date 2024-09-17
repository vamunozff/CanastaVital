from django.contrib import admin
from .models import Categoria, Producto, ProductosTiendas, Proveedor,Cliente, Tienda, Promocion, MetodoPago, AtencionCliente, Direccion, Departamento, Ciudad, Orden, ProductoOrden
from django.utils.html import mark_safe, format_html

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
    list_display = ('producto', 'proveedor', 'tienda', 'precio_unitario', 'cantidad', 'estado', 'fecha_registro', 'imagen_preview')
    list_filter = ('estado', 'fecha_registro', 'producto__categoria', 'proveedor')
    search_fields = ('producto__nombre', 'proveedor__razon_social', 'tienda__nombre')
    list_per_page = 20

    fieldsets = (
        ('Información General', {
            'fields': ('producto', 'proveedor', 'tienda', 'imagen')
        }),
        ('Detalles de Inventario', {
            'fields': ('precio_unitario', 'cantidad', 'estado', 'fecha_registro')
        }),
    )

    readonly_fields = ('fecha_registro',)

    def imagen_preview(self, obj):
        if obj.imagen:
            return format_html('<img src="{}" style="width: 100px; height: auto;">', obj.imagen.url)
        return 'No Image'

    imagen_preview.short_description = 'Vista Previa de Imagen'

@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'razon_social', 'email', 'telefono', 'estado', 'fecha_registro')
    search_fields = ('razon_social', 'email', 'telefono')
    list_filter = ('tienda', 'estado', 'fecha_registro')
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
    list_display = ('cliente', 'tienda', 'direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal')
    search_fields = ('direccion', 'ciudad', 'departamento', 'codigo_postal')
    list_filter = ('ciudad', 'departamento', 'principal', 'cliente', 'tienda')
    ordering = ('-cliente',)

    fieldsets = (
        (None, {
            'fields': ('cliente', 'tienda', 'direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal')
        }),
    )
@admin.register(Departamento)
class DepartamentoAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre')
    search_fields = ('nombre',)

@admin.register(Ciudad)
class CiudadAdmin(admin.ModelAdmin):
    list_display = ('id', 'nombre', 'departamento')
    search_fields = ('nombre',)
    list_filter = ('departamento',)

@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'user', 'telefono', 'descripcion', 'logo_url', 'fecha_registro')
    search_fields = ('nombre', 'user__username', 'direccion')
    list_filter = ('fecha_registro',)

@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = ('tienda', 'nombre', 'descuento', 'fecha_inicio', 'fecha_fin', 'activo')
    search_fields = ('nombre', 'tienda__nombre')
    list_filter = ('activo', 'fecha_inicio', 'fecha_fin', 'tienda')
    ordering = ('-fecha_inicio', 'tienda')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('descuento',)
        return self.readonly_fields

@admin.register(MetodoPago)
class MetodoPagoAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tipo', 'metodo_pago', 'detalles')
    search_fields = ('cliente__user__username', 'tipo', 'detalles', 'metodo_pago')
    list_filter = ('metodo_pago', 'cliente')
    ordering = ('cliente', 'tipo')

@admin.register(AtencionCliente)
class AtencionClienteAdmin(admin.ModelAdmin):
    list_display = ('cliente', 'tienda', 'estado_atencion', 'fecha_creacion', 'mensaje', 'respuesta')
    search_fields = ('cliente__user__username', 'tienda__nombre', 'mensaje')
    list_filter = ('estado_atencion', 'fecha_creacion', 'tienda')
    ordering = ('-fecha_creacion',)

    actions = ['marcar_como_leido', 'marcar_como_respondido']

    def marcar_como_leido(self, request, queryset):
        rows_updated = queryset.update(estado_atencion=AtencionCliente.Estado.LEIDO)
        self.message_user(request, f'{rows_updated} consultas marcadas como leídas.')
    marcar_como_leido.short_description = 'Marcar seleccionadas como leídas'

    def marcar_como_respondido(self, request, queryset):
        rows_updated = queryset.update(estado_atencion=AtencionCliente.Estado.RESPONDIDO)
        self.message_user(request, f'{rows_updated} consultas marcadas como respondidas.')
    marcar_como_respondido.short_description = 'Marcar seleccionadas como respondidas'

@admin.register(Orden)
class OrdenAdmin(admin.ModelAdmin):
    list_display = ('id', 'cliente', 'tienda', 'direccion_envio', 'fecha_creacion', 'total', 'estado')
    list_filter = ('estado', 'tienda', 'fecha_creacion')
    search_fields = ('cliente__user__username', 'tienda__nombre', 'estado')
    date_hierarchy = 'fecha_creacion'
    ordering = ('-fecha_creacion',)
    readonly_fields = ('fecha_creacion',)

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('cliente', 'tienda')
        return self.readonly_fields

@admin.register(ProductoOrden)
class ProductoOrdenAdmin(admin.ModelAdmin):
    list_display = ('orden', 'producto_tienda', 'cantidad', 'precio_unitario')
    list_filter = ('orden', 'producto_tienda')
    search_fields = ('orden__id', 'producto_tienda__producto__nombre')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields + ('precio_unitario',)
        return self.readonly_fields
