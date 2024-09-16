from django import forms
from django.contrib import admin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Proveedor, Cliente, Tienda, ProductosTiendas, Direccion, Orden, Departamento, Ciudad

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


class DireccionForm(forms.ModelForm):
    departamento = forms.ModelChoiceField(queryset=Departamento.objects.all())
    ciudad = forms.ModelChoiceField(queryset=Ciudad.objects.all())

    class Meta:
        model = Direccion
        fields = ['direccion', 'ciudad', 'departamento', 'codigo_postal', 'principal']

    def clean(self):
        cleaned_data = super().clean()
        principal = cleaned_data.get("principal")
        cliente = self.instance.cliente
        tienda = self.instance.tienda

        if principal:

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
        # Personaliza el método save si necesitas realizar acciones adicionales
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance