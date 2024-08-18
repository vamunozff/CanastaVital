from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proveedor, Cliente, Tienda, ProductosTiendas

class CustomUserCreationForm(UserCreationForm):
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

class ProveedorForm(forms.ModelForm):
    class Meta:
        model = Proveedor
        fields = ['razon_social', 'email', 'telefono', 'direccion', 'estado']

class ClienteForm(forms.ModelForm):
    class Meta:
        model = Cliente
        fields = ['direccion', 'telefono', 'fecha_nacimiento', 'tipo_documento', 'numero_documento']

class TiendaForm(forms.ModelForm):
    class Meta:
        model = Tienda
        fields = ['nombre', 'direccion', 'horarios', 'telefono', 'descripcion', 'logo_url']

class ProductosTiendasForm(forms.ModelForm):
    class Meta:
        model = ProductosTiendas
        fields = ['producto', 'proveedor', 'precio_unitario', 'cantidad', 'estado', 'imagen']
        widgets = {
            'estado': forms.Select(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')]),
        }