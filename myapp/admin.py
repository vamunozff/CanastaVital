from django.contrib import admin
from .models import Rol, Perfil, Categoria, Producto, ProductosTiendas, Proveedor,Cliente, Tienda, Promocion, MetodoPago, AtencionCliente, Direccion, Departamento, Ciudad, Orden, ProductoOrden
from django.utils.html import mark_safe, format_html

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('nombre',)
    search_fields = ('nombre',)
    list_filter = ('nombre',)
    ordering = ('nombre',)

@admin.register(Perfil)
class PerfilAdmin(admin.ModelAdmin):
    list_display = ('user', 'rol_nombre')
    search_fields = ('user__username', 'rol__nombre')
    list_filter = ('rol',)
    ordering = ('user__username',)

    def rol_nombre(self, obj):
        return obj.rol.nombre
    rol_nombre.short_description = 'Rol'

@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ('perfil_usuario', 'tipo_documento', 'numero_documento', 'telefono', 'fecha_registro')
    search_fields = ('perfil__user__username', 'numero_documento', 'telefono')
    list_filter = ('tipo_documento', 'fecha_registro')
    ordering = ('perfil__user__username',)

    fieldsets = (
        (None, {
            'fields': ('perfil', 'telefono', 'fecha_nacimiento', 'tipo_documento', 'numero_documento', 'imagen_perfil')
        }),
        ('Información de registro', {
            'fields': ('fecha_registro',),
        }),
    )

    readonly_fields = ('fecha_registro',)
    list_editable = ('telefono', 'tipo_documento')

    def perfil_usuario(self, obj):
        return obj.perfil.user.username
    perfil_usuario.short_description = 'Usuario'

@admin.register(Tienda)
class TiendaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'perfil_usuario', 'telefono', 'fecha_registro', 'logo_preview')
    search_fields = ('nombre', 'perfil__user__username', 'telefono')
    list_filter = ('fecha_registro',)
    ordering = ('nombre',)

    fieldsets = (
        (None, {
            'fields': ('perfil', 'nombre', 'telefono', 'horarios', 'descripcion', 'logo_url')
        }),
        ('Información de registro', {
            'fields': ('fecha_registro',),
        }),
    )

    readonly_fields = ('fecha_registro',)
    list_editable = ('telefono',)

    def perfil_usuario(self, obj):
        return obj.perfil.user.username
    perfil_usuario.short_description = 'Usuario'

    def logo_preview(self, obj):
        if obj.logo_url:
            return format_html('<img src="{}" width="50" height="50"/>', obj.logo_url.url)
        return "No Logo"
    logo_preview.short_description = 'Logo'

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


@admin.register(Promocion)
class PromocionAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'tienda', 'get_descuento_porcentaje', 'fecha_inicio', 'fecha_fin',
        'activo', 'cantidad_minima', 'cantidad_maxima', 'get_productos_aplicables'
    )
    list_filter = ('tienda', 'activo', 'fecha_inicio', 'fecha_fin')
    search_fields = ('nombre', 'codigo_promocional')
    ordering = ('fecha_inicio',)
    prepopulated_fields = {'codigo_promocional': ('nombre',)}

    fieldsets = (
        (None, {
            'fields': (
                'nombre', 'tienda', 'descripcion', 'descuento_porcentaje', 'fecha_inicio',
                'fecha_fin', 'activo', 'codigo_promocional', 'condiciones',
                'productos_aplicables', 'cantidad_minima', 'cantidad_maxima'
            )
        }),
    )

    def has_change_permission(self, request, obj=None):
        if obj and not obj.activo:
            return False
        return super().has_change_permission(request, obj)

    def get_productos_aplicables(self, obj):
        return ", ".join([str(producto) for producto in obj.productos_aplicables.all()])
    get_productos_aplicables.short_description = 'Productos Aplicables'

    def get_descuento_porcentaje(self, obj):
        return f"{obj.descuento_porcentaje}%"
    get_descuento_porcentaje.short_description = 'Descuento'

    actions = ['activar_promociones', 'desactivar_promociones']

    def activar_promociones(self, request, queryset):
        queryset.update(activo=True)
        self.message_user(request, "Las promociones seleccionadas han sido activadas.")

    def desactivar_promociones(self, request, queryset):
        queryset.update(activo=False)
        self.message_user(request, "Las promociones seleccionadas han sido desactivadas.")


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
    list_display = ('id', 'cliente', 'tienda', 'direccion_envio', 'total', 'estado', 'fecha_creacion', 'fecha_venta')
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
