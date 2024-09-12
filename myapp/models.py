from django.db import models
from django.contrib.auth.models import User
from datetime import date
class Cliente(models.Model):
    DOCUMENTO_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('TI', 'Tarjeta de Identidad'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_documento = models.CharField(max_length=20, choices=DOCUMENTO_CHOICES, default='CC')
    numero_documento = models.CharField(max_length=50, default='Sin número')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen_perfil = models.ImageField(upload_to='imagenes_clientes/', default='default/Defaul.jpg')

    def __str__(self):
        return f'{self.user.username} - {self.numero_documento}'

    class Meta:
        db_table = 'Cliente'
class Tienda(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tienda')
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
        verbose_name = 'Tienda'
        verbose_name_plural = 'Tiendas'

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    direccion = models.TextField()
    ciudad = models.CharField(max_length=100)
    departamento = models.CharField(max_length=100)
    codigo_postal = models.CharField(max_length=10, null=True, blank=True)
    principal = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.principal:
            if self.cliente:
                Direccion.objects.filter(cliente=self.cliente, principal=True).update(principal=False)
            if self.tienda:
                Direccion.objects.filter(tienda=self.tienda, principal=True).update(principal=False)
        super().save(*args, **kwargs)

    def __str__(self):
        if self.cliente:
            return f'{self.cliente.user.username} - {self.direccion}'
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='proveedores')
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
        return self.razon_social

    class Meta:
        db_table = 'Proveedor'
        verbose_name = "Proveedor"
        verbose_name_plural = "Proveedores"
class ProductosTiendas(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='productos_tiendas')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor", related_name='productos_tiendas')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos_tiendas')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad = models.IntegerField()

    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
    ]
    estado = models.CharField(max_length=50, choices=ESTADO_CHOICES, verbose_name="Estado")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen = models.ImageField(upload_to='productos_tiendas/', null=True, blank=True, verbose_name="Imagen del Producto")

    def __str__(self):
        return f"{self.producto.nombre} - {self.proveedor.razon_social} - {self.tienda.nombre}"

    class Meta:
        db_table = 'ProductosTiendas'
        verbose_name = 'Producto en Tienda'
        verbose_name_plural = 'Productos en Tiendas'

class PromocionManager(models.Manager):
    def activas(self):
        return self.filter(activo=True, fecha_inicio__lte=date.today(), fecha_fin__gte=date.today())

class Promocion(models.Model):
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    nombre = models.CharField(max_length=100)
    descripcion = models.TextField(null=True, blank=True)
    descuento = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_inicio = models.DateField()
    fecha_fin = models.DateField()
    activo = models.BooleanField(default=True)

    objects = PromocionManager()

    def save(self, *args, **kwargs):
        if self.fecha_inicio > self.fecha_fin:
            raise ValueError("La fecha de inicio no puede ser posterior a la fecha de fin.")
        if self.fecha_fin < date.today():
            self.activo = False
        super(Promocion, self).save(*args, **kwargs)

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'Promocion'
        constraints = [
            models.UniqueConstraint(fields=['tienda'], condition=models.Q(activo=True),
                                    name='unique_active_promotion_per_store')
        ]

class Venta(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    fecha = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Venta {self.id} - {self.cliente.user.username}'

    class Meta:
        db_table = 'Venta'
class DetalleVenta(models.Model):
    venta = models.ForeignKey(Venta, on_delete=models.CASCADE)
    producto_tienda = models.ForeignKey('ProductosTiendas', on_delete=models.CASCADE)
    cantidad = models.IntegerField()
    precio = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'Detalle {self.id} - Venta {self.venta.id}'

    class Meta:
        db_table = 'DetalleVenta'

class Inventario(models.Model):
    producto_tienda = models.ForeignKey('ProductosTiendas', on_delete=models.CASCADE)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE)
    cantidad = models.IntegerField()

    def __str__(self):
        return f'Inventario {self.id} - {self.producto_tienda.producto.nombre}'

    class Meta:
        db_table = 'Inventario'
class MetodoPago(models.Model):
    tipo = models.CharField(max_length=50)
    descripcion = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.tipo

    class Meta:
        db_table = 'MetodoPago'
class AtencionCliente(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE)
    asunto = models.CharField(max_length=100)
    descripcion = models.TextField()
    estado = models.CharField(max_length=50, choices=[
        ('abierto', 'Abierto'),
        ('en progreso', 'En Progreso'),
        ('cerrado', 'Cerrado')
    ])
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.asunto} - {self.cliente.user.username}'

    class Meta:
        db_table = 'AtencionCliente'