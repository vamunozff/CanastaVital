from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proveedor, Cliente, Tienda, ProductosTiendas, Direccion

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
        fields = ['telefono', 'fecha_nacimiento', 'tipo_documento', 'numero_documento', 'imagen_perfil']
    def clean(self):
        cleaned_data = super().clean()
        tipo_documento = cleaned_data.get('tipo_documento')
        numero_documento = cleaned_data.get('numero_documento')
        fecha_nacimiento = cleaned_data.get('fecha_nacimiento')

        # Verificar si los campos fueron dejados en blanco y mantener el valor anterior
        if not tipo_documento:
            cleaned_data['tipo_documento'] = self.instance.tipo_documento
        if not numero_documento:
            cleaned_data['numero_documento'] = self.instance.numero_documento
        if not fecha_nacimiento:
            cleaned_data['fecha_nacimiento'] = self.instance.fecha_nacimiento

        return cleaned_data

class DireccionForm(forms.ModelForm):
    class Meta:
        model = Direccion
        fields = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal']

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
