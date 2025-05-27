"""
Función perfil_cliente corregida para actualizar correctamente los datos del cliente.
Copiar esta función y reemplazar la existente en views.py
"""

@login_required
@user_is_cliente
def perfil_cliente(request):
    try:
        cliente = Cliente.objects.get(usuario=request.user)
    except Cliente.DoesNotExist:
        messages.error(request, "No tienes un perfil de cliente asociado.")
        return redirect('home')

    if request.method == 'POST':
        # Crear un diccionario con los datos del formulario para el modelo Cliente
        cliente_data = {
            'telefono': request.POST.get('telefono', ''),
            'fecha_nacimiento': request.POST.get('fecha_nacimiento', None),
            'numero_documento': request.POST.get('numero_documento', ''),
            'tipo_documento': cliente.tipo_documento  # Mantener el tipo de documento actual
        }
        
        # Manejar la imagen de perfil si se proporciona
        if 'imagen_perfil' in request.FILES:
            cliente_data['imagen_perfil'] = request.FILES['imagen_perfil']
        
        # Actualizar datos del modelo Cliente
        cliente_form = ClienteForm(cliente_data, request.FILES, instance=cliente)
        
        if cliente_form.is_valid():
            with transaction.atomic():  # Usar transacción para garantizar que ambos modelos se actualicen o ninguno
                cliente_form.save()
                
                # Actualizar datos del modelo User
                request.user.first_name = request.POST.get('first_name', request.user.first_name)
                request.user.last_name = request.POST.get('last_name', request.user.last_name)
                request.user.save()
                
                messages.success(request, "Perfil actualizado correctamente.")
                return redirect('perfil_cliente')
        else:
            # Mostrar errores específicos del formulario
            for field, errors in cliente_form.errors.items():
                for error in errors:
                    messages.error(request, f"Error en {field}: {error}")
    else:
        cliente_form = ClienteForm(instance=cliente)

    context = {
        'cliente': cliente,
        'user': request.user,
        'cliente_form': cliente_form,
    }
    return render(request, 'clientes/perfil.html', context)