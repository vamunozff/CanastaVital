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
        widgets = {
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean_fecha_nacimiento(self):
        fecha_nacimiento = self.cleaned_data.get('fecha_nacimiento')
        if fecha_nacimiento and fecha_nacimiento > date.today():
            raise forms.ValidationError("La fecha de nacimiento no puede ser en el futuro.")
        return fecha_nacimiento

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

DEPARTAMENTOS = [
    ('ANT', 'Antioquia'),
    ('BOL', 'Bolívar'),
    # Agrega aquí todos los departamentos de Colombia
]

CIUDADES = [
    ('BOG', 'Bogotá'),
    ('MED', 'Medellín'),
    # Agrega aquí todas las ciudades o municipios relevantes
]

class DireccionForm(forms.ModelForm):
    departamento = forms.ChoiceField(choices=DEPARTAMENTOS)
    ciudad = forms.ChoiceField(choices=CIUDADES)

    class Meta:
        model = Direccion
        fields = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal']

    def clean(self):
        cleaned_data = super().clean()
        principal = cleaned_data.get("principal")
        cliente = self.instance.cliente  # El cliente asociado a la dirección
        tienda = self.instance.tienda    # La tienda asociada a la dirección

        # Si la dirección es marcada como principal
        if principal:
            # Verificar si ya hay una dirección principal para ese cliente
            if cliente and Direccion.objects.filter(cliente=cliente, principal=True).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError("Este cliente ya tiene una dirección principal.")

            # Verificar si ya hay una dirección principal para esa tienda
            if tienda and Direccion.objects.filter(tienda=tienda, principal=True).exclude(pk=self.instance.pk).exists():
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
        widgets = {
            'estado': forms.Select(choices=[('activo', 'Activo'), ('inactivo', 'Inactivo')]),
        }
