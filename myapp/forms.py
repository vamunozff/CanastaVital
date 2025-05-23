from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proveedor, Cliente, Tienda, ProductosTiendas, Direccion, Orden, Departamento, Ciudad, Promocion
from datetime import datetime, time
from decimal import Decimal, InvalidOperation
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import date

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("El nombre de usuario ya está en uso.")
        return username
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Las contraseñas no coinciden.")
        return password2

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'email', 'telefono', 'direccion', 'estado']


class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['telefono', 'fecha_nacimiento', 'tipo_documento', 'numero_documento', 'imagen_perfil']
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'telefono': forms.TextInput(attrs={'class': 'form-control'}),
            'tipo_documento': forms.Select(attrs={'class': 'form-control'}),
            'numero_documento': forms.TextInput(attrs={'class': 'form-control'}),
            'imagen_perfil': forms.FileInput(attrs={'class': 'form-control'}),
        }

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data.get('fecha_nacimiento')
        if fecha and fecha > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha

    def clean_numero_documento(self):
        numero_documento = self.cleaned_data['numero_documento']
        if len(numero_documento) < 6:
            raise forms.ValidationError("El número de documento es demasiado corto.")
        return numero_documento

    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        numero_documento = cleaned_data.get('numero_documento')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')

        if not tipo_documento:
            cleaned_data['tipo_documento'] = self.instance.tipo_documento
        if not numero_documento:
            cleaned_data['numero_documento'] = self.instance.numero_documento
        if not fecha_nacimiento:
            cleaned_data['fecha_nacimiento'] = self.instance.fecha_nacimiento

        return cleaned_data


class DireccionForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    ciudad = forms.ModelChoiceField(queryset=Ciudad.objects.all())

    class Meta:
        model = Direccion
        fields = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal']

    def __init__(self, *args, **kwargs):
        self.cliente = kwargs.pop('cliente', None)
        self.tienda = kwargs.pop('tienda', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        principal = cleaned_data.get("principal")

        # Validar que el formulario esté asociado a un cliente o tienda
        if not self.cliente and not self.tienda:
            raise forms.ValidationError("La dirección debe estar asociada a un cliente o una tienda.")

        if principal:
            # Validar que no haya más de una dirección principal para el cliente
            if self.cliente and Direccion.objects.filter(cliente=self.cliente, principal=True).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este cliente ya tiene una dirección principal.")

            # Validar que no haya más de una dirección principal para la tienda
            if self.tienda and Direccion.objects.filter(tienda=self.tienda, principal=True).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Esta tienda ya tiene una dirección principal.")

        return cleaned_data

class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ['nombre', 'horarios', 'telefono', 'descripcion', 'logo_url']

class ProductosTiendasForm(forms.ModelForm):
    class Meta:
        model = ProductosTiendas
        fields = ['producto', 'proveedor', 'precio_unitario', 'cantidad', 'estado', 'imagen']

    def clean_precio_unitario(self):
        precio = self.cleaned_data.get('precio_unitario')

        if isinstance(precio, str) and ',' in precio:
            precio = precio.replace(',', '.')
        try:
            precio = float(precio)
        except ValueError:
            raise forms.ValidationError('Ingrese un número válido para el precio unitario.')
        return precio

class OrdenForm(forms.ModelForm):
    class Meta:
        model = Orden
        fields = ['cliente', 'tienda', 'direccion_envio', 'fecha_creacion', 'total', 'estado']
        widgets = {
            'fecha_creacion': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'total': forms.NumberInput(attrs={'step': '0.01'}),
            'estado': forms.Select(choices=Orden.Estado.choices),
        }

    def clean_total(self):
        total = self.cleaned_data.get('total')
        if total < 0:
            raise forms.ValidationError('El total no puede ser negativo.')
        return total

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class PromocionForm(forms.ModelForm):
    class Meta:
        model = Promocion
        fields = [
            'nombre',
            'descripcion',
            'descuento_porcentaje',
            'fecha_inicio',
            'fecha_fin',
            'codigo_promocional',
            'condiciones',
            'cantidad_minima',
            'cantidad_maxima',
            'productos_aplicables',
            'activo',
        ]
        widgets = {
            'fecha_inicio': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'productos_aplicables': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }

    def clean_descuento_porcentaje(self):
        descuento = self.cleaned_data.get('descuento_porcentaje')
        if descuento is not None:
            if not isinstance(descuento, int):
                raise forms.ValidationError("El descuento debe ser un número entero.")

            if descuento < 0 or descuento > 100:
                raise forms.ValidationError("El porcentaje de descuento debe estar entre 0 y 100.")
        return descuento
