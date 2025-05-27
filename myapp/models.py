from django.db import models
from django.contrib.auth.models import User, Permission , Group
from datetime import date
from django.utils import timezone
from django.utils.timezone import now
from django.core.exceptions import ValidationError
from datetime import datetime
from django.db import models, IntegrityError
from django.core.validators import RegexValidator
from django.utils import timezone
import uuid

class Tienda(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='tienda')
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

class Cliente(models.Model):
    usuario = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cliente')
    telefono = models.CharField(max_length=20, null=True, blank=True)
    fecha_nacimiento = models.DateField(null=True, blank=True)
    tipo_documento = models.CharField(
        max_length=20,
        choices=[
            ('CC', 'Cédula de Ciudadanía'),
            ('TI', 'Tarjeta de Identidad'),
            ('CE', 'Cédula de Extranjería'),
            ('PA', 'Pasaporte'),
        ],
        default='CC',
        verbose_name="Tipo de Documento"
    )
    numero_documento = models.CharField(max_length=50, default='Sin número')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    imagen_perfil = models.ImageField(upload_to='imagenes_clientes/', default='default/Default.png')

    def __str__(self):
        return f'{self.usuario.username} - {self.numero_documento}'

    class Meta:
        db_table = 'Cliente'
        verbose_name = 'Cliente'
        verbose_name_plural = 'Clientes'

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

class Direccion(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='direcciones', null=True, blank=True)
    direccion = models.TextField()
    ciudad = models.ForeignKey(Ciudad, on_delete=models.PROTECT)
    departamento = models.ForeignKey(Departamento, on_delete=models.PROTECT)
    codigo_postal = models.CharField(
        max_length=10, 
        blank=True,  # Permitir que se deje vacío
        null=True,   # Permitir valores nulos en la base de datos
        validators=[RegexValidator(
            regex='^[0-9]{5}(?:-[0-9]{4})?$',
            message='Formato de código postal no válido'
        )]
    )
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
            return f'{self.cliente.usuario.username} - {self.direccion}'
        elif self.tienda:
            return f'{self.tienda.nombre} - {self.direccion}'
        else:
            return self.direccion

    class Meta:
        db_table = 'Direccion'

class Categoria(models.Model):
    nombre = models.CharField(max_length=100, verbose_name="Nombre")
    descripcion = models.TextField(max_length=150, verbose_name="Descripción")
    icono = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.nombre
    class Meta:
        db_table = 'Categoria'
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"

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

# esta tabla tambien va ha ser usada para el inventario
class ProductosTiendas(models.Model):
    producto = models.ForeignKey(Producto, on_delete=models.CASCADE, related_name='productos_tiendas')
    proveedor = models.ForeignKey(Proveedor, on_delete=models.CASCADE, verbose_name="Proveedor", related_name='productos_tiendas')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='productos_tiendas')
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cantidad = models.PositiveIntegerField()
    stock_minimo = models.PositiveIntegerField(null=True, blank=True, verbose_name="Stock mínimo") 

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
    descuento_porcentaje = models.IntegerField(help_text="Porcentaje de descuento (ej: 20%)")
    fecha_inicio = models.DateTimeField(default=timezone.now)
    fecha_fin = models.DateTimeField()
    activo = models.BooleanField(default=True)
    codigo_promocional = models.CharField(max_length=50, unique=True, blank=True, null=True)
    condiciones = models.TextField(blank=True, null=True)
    cantidad_minima = models.IntegerField(blank=True, null=True)
    cantidad_maxima = models.IntegerField(blank=True, null=True)
    imagen = models.ImageField(upload_to='promociones/', blank=True, null=True)

    def clean(self):
        if self.cantidad_minima is not None and self.cantidad_maxima is not None:
            if self.cantidad_minima > self.cantidad_maxima:
                raise ValidationError("La cantidad mínima no puede ser mayor que la cantidad máxima.")
        if self.descuento_porcentaje < 0 or self.descuento_porcentaje > 100:
            raise ValidationError("El descuento debe estar entre 0 y 100.")

    def save(self, *args, **kwargs):
        if not self.codigo_promocional:
            self.codigo_promocional = str(uuid.uuid4())[:8]

        now = timezone.now()
        print(f"Ahora: {now}, Fecha Inicio: {self.fecha_inicio}, Fecha Fin: {self.fecha_fin}")

        if self.fecha_inicio <= now <= self.fecha_fin:
            self.activo = True
        else:
            self.activo = False
        print(f"Activo: {self.activo}")

        self.clean()
        super(Promocion, self).save(*args, **kwargs)

        self.activar_promociones_validas()

    @classmethod
    def activar_promociones_validas(cls):
        now = timezone.now()
        cls.objects.filter(fecha_inicio__lte=now, fecha_fin__gte=now).update(activo=True)

    class Meta:
        db_table = 'Promocion'
        ordering = ['-fecha_inicio']
        verbose_name = 'Promoción'
        verbose_name_plural = 'Promociones'


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
        return f"Consulta {self.id} - Cliente: {self.cliente.usuario.username} - Tienda: {self.tienda.nombre}"

    class Meta:
        db_table = 'atencion_cliente'
        verbose_name = 'Atención al Cliente'
        verbose_name_plural = 'Atención al Cliente'

class Orden(models.Model):
    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name='ordenes')
    tienda = models.ForeignKey(Tienda, on_delete=models.CASCADE, related_name='ordenes')
    direccion_envio = models.ForeignKey(Direccion, on_delete=models.CASCADE)
    fecha_creacion = models.DateTimeField(default=timezone.now)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    iva = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    promocion = models.ForeignKey('Promocion', on_delete=models.SET_NULL, null=True, blank=True)
    metodo_pago = models.ForeignKey('MetodoPago', on_delete=models.PROTECT)
    fecha_venta = models.DateTimeField(null=True, blank=True)

    class Estado(models.TextChoices):
        PENDIENTE = 'pendiente', 'Pendiente'
        PROCESANDO = 'procesando', 'Procesando'
        COMPLETADA = 'completada', 'Completada'
        CANCELADA = 'cancelada', 'Cancelada'

    estado = models.CharField(max_length=50, choices=Estado.choices, default=Estado.PENDIENTE)

    def __str__(self):
        return f"Orden {self.id} - Cliente: {self.cliente.usuario.username} - Tienda: {self.tienda.nombre} - Fecha: {self.fecha_creacion.strftime('%Y-%m-%d %H:%M:%S')}"
    
    def clean(self):
        if self.total < 0:
            raise ValidationError('El total no puede ser negativo.')
        if self.subtotal < 0:
            raise ValidationError('El subtotal no puede ser negativo.')
        if self.iva < 0:
            raise ValidationError('El IVA no puede ser negativo.')

    def calcular_total(self):
        total = sum(detalle.subtotal() for detalle in self.productos_orden.all())
        self.total = total
        self.save()

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
    nombre = models.CharField(max_length=100, unique=True) 
    descripcion = models.TextField(blank=True, null=True)  

    def __str__(self):
        return self.nombre

    class Meta:
        db_table = 'metodo_pago'
        verbose_name = 'Método de Pago'
        verbose_name_plural = 'Métodos de Pago'
