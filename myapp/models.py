from django.db import models
from django.contrib.auth.models import User
from datetime import date
from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db import models, IntegrityError

class Rol(models.Model):
    NOMBRE_ROLES = [
        ('administrador', 'Administrador'),
        ('cliente', 'Cliente'),
        ('tienda', 'Tienda'),
    ]

    nombre = models.CharField(max_length=50, choices=NOMBRE_ROLES, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

from django.contrib.auth.models import User

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.ForeignKey(Rol, on_delete=models.CASCADE, related_name='perfiles')

    def __str__(self):
        return f'{self.user.username} - {self.rol.nombre}'

    class Meta:
        db_table = 'Perfil'

class Departamento(models.Model):
    nombre = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Departamento'
        verbose_name = 'Departamento'
        verbose_name_plural = 'Departamentos'

class Ciudad(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    departamento = models.ForeignKey(Departamento, on_delete=models.CASCADE, related_name='ciudades')

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Ciudad'
        verbose_name = 'Ciudad'
        verbose_name_plural = 'Ciudades'

class Tienda(models.Model):
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='tienda')
    nombre = models.CharField(max_length=100)
    horarios = models.TextField(null=True, blank=True)
    telefono = models.CharField(max_length=20, null=True, blank=True)
    descripcion = models.TextField(null=True, blank=True)
    logo_url = models.ImageField(upload_to='tienda_logos/', blank=True, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Tienda'

class Cliente(models.Model):
    DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]
    perfil = models.OneToOneField(Perfil, on_delete=models.CASCADE, related_name='cliente')
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_documento = models.CharField(max_length=20, choices=DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=50, default='Sin número')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen_perfil = models.ImageField(upload_to='imagenes_clientes/', default='default/Defaut.jpg')

    def __str__(self):
        return f'{self.perfil.user.username} - {self.numero_documento}'

    class Meta:
        db_table = 'Cliente'

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    direccion = models.TextField()
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    principal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.principal:
            if self.cliente:
                Direccion.objects.filter(cliente=self.cliente, principal=True).exclude(id=self.id).update(principal=False)
            if self.tienda:
                Direccion.objects.filter(tienda=self.tienda, principal=True).exclude(id=self.id).update(principal=False)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.cliente:
            return f'{self.cliente.perfil.user.username} - {self.direccion}'
        elif self.tienda:
            return f'{self.tienda.nombre} - {self.direccion}'
        else:
            return self.direccion

    class Meta:
        db_table = 'Direccion'

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(max_length=150, verbose_name="Descripción")

    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'Categoria'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

class Producto(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, verbose_name="Categoría")
    codigo = models.CharField(max_length=100, verbose_name="Código", unique=True)
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(max_length=255, verbose_name="Descripción")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Producto'
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'
        indexes = [
            models.Index(fields=['codigo']),
            models.Index(fields=['nombre']),
        ]

class Proveedor(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='proveedores')
    razon_social = models.CharField(max_length=150, verbose_name="Razón Social")
    email = models.EmailField(max_length=100, verbose_name="Email", blank=True, null=True)
    telefono = models.CharField(max_length=20, verbose_name="Teléfono", blank=True, null=True)
    direccion = models.TextField(verbose_name="Dirección", blank=True, null=True)

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de Registro")
    def __str__(self):
        return f"{self.razon_social} - {self.tienda.nombre}"
    class Meta:
        db_table = 'Proveedor'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
        unique_together = ('tienda', 'razon_social')

# esta tabla tambien va ha ser usada para el inventario
class ProductosTiendas(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='productos_tiendas')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor", related_name='productos_tiendas')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos_tiendas')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad = models.PositiveIntegerField()

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='productos_tiendas/', null=True, blank=True, verbose_name="Imagen del Producto")

    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.razon_social} - {self.tienda.nombre}"

    class Meta:
        db_table = 'ProductosTiendas'
        verbose_name = 'Producto en Tienda'
        verbose_name_plural = 'Productos en Tiendas'
        indexes = [
            models.Index(fields=['estado']),
            models.Index(fields=['precio_unitario']),
        ]
        constraints = [
            models.UniqueConstraint(fields=['producto', 'proveedor', 'tienda'], name='unique_prod_prov_tienda')
        ]

class PromocionManager(models.Manager):
    def activas(self):
        return self.filter(activo=True, fecha_inicio__lte=date.today(), fecha_fin__gte=date.today())


class Promocion(models.Model):
    tienda = models.ForeignKey('Tienda', on_delete=models.CASCADE)
    productos_aplicables = models.ManyToManyField('ProductosTiendas', related_name='promociones')
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)
    codigo_promocional = models.CharField(max_length=50, unique=True, blank=True, null=True)
    condiciones = models.TextField(blank=True, null=True)
    cantidad_minima = models.IntegerField(blank=True, null=True)
    cantidad_maxima = models.IntegerField(blank=True, null=True)

    def clean(self):
        if self.cantidad_minima is not None and self.cantidad_maxima is not None:
            if self.cantidad_minima > self.cantidad_maxima:
                raise ValidationError("La cantidad mínima no puede ser mayor que la cantidad máxima.")
        if self.descuento < 0:
            raise ValidationError("El descuento no puede ser un valor negativo.")
    def save(self, *args, **kwargs):
        if not self.codigo_promocional:
            self.codigo_promocional = str(uuid.uuid4())[:8]

        self.clean()
        super(Promocion, self).save(*args, **kwargs)

    class Meta:
        db_table = 'Promocion'
        ordering = ['-fecha_inicio']
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'

class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordenes')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='ordenes')
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.SET_NULL, null=True, blank=True, related_name='ordenes')
    fecha_creacion = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PROCESANDO = 'procesando', 'Procesando'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'

    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)

    def __str__(self):
        return f"Orden {self.id} - Cliente: {self.cliente.perfil.user.username} - Tienda: {self.tienda.nombre} - Fecha: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
    def clean(self):
        if self.total < 0:
            raise ValidationError('El total no puede ser negativo.')
    class Meta:
        db_table = 'ordenes'
        verbose_name = 'Orden'
        verbose_name_plural = 'Órdenes'

class ProductoOrden(models.Model):
    orden = models.ForeignKey(Orden, on_delete=models.CASCADE, related_name='productos_orden')
    producto_tienda = models.ForeignKey(ProductosTiendas, on_delete=models.CASCADE, related_name='productos_orden')
    cantidad = models.PositiveIntegerField()
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.producto_tienda.producto.nombre} - Orden {self.orden.id}"

    class Meta:
        db_table = 'productos_orden'
        verbose_name = 'Producto en Orden'
        verbose_name_plural = 'Productos en Órdenes'

class MetodoPago(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='metodos_pago')
    tipo = models.CharField(max_length=50)
    detalles = models.TextField()

    class Metodo(models.TextChoices):
        TARJETA_CREDITO = 'tarjeta_credito', 'Tarjeta de Crédito'
        TARJETA_DEBITO = 'tarjeta_debito', 'Tarjeta de Débito'
        TRANSFERENCIA_BANCARIA = 'transferencia_bancaria', 'Transferencia Bancaria'
        PAYPAL = 'paypal', 'PayPal'

    metodo_pago = models.CharField(max_length=50, choices=Metodo.choices)

    def __str__(self):
        return f"{self.tipo} - Cliente: {self.cliente.user.username}"

    class Meta:
        db_table = 'metodo_pago'
class AtencionCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='atencion_cliente')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='atencion_cliente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    mensaje = models.TextField()
    respuesta = models.TextField(null=True, blank=True)
    estado = models.BooleanField(default=False)

    class Estado(models.TextChoices):
        NO_LEIDO = 'no_leido', 'No Leído'
        LEIDO = 'leido', 'Leído'
        RESPONDIDO = 'respondido', 'Respondido'

    estado_atencion = models.CharField(max_length=50, choices=Estado.choices, default=Estado.NO_LEIDO)

    def __str__(self):
        return f"Consulta {self.id} - Cliente: {self.cliente.user.username} - Tienda: {self.tienda.nombre}"

    class Meta:
        db_table = 'atencion_cliente'
        verbose_name = 'Atención al Cliente'
        verbose_name_plural = 'Atención al Cliente'