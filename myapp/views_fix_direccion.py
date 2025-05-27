@login_required
def registrar_direccion(request):
    # Verificar si la solicitud viene de la página de confirmación de pago
    referer = request.META.get('HTTP_REFERER', '')
    es_confirmacion_pago = 'confirmar_pago' in referer
    
    # Determinar el grupo activo del usuario desde la sesión
    grupo_activo = request.session.get('groups', None)
    
    # Obtener cliente y tienda (si existen)
    cliente = getattr(request.user, 'cliente', None)
    tienda = getattr(request.user, 'tienda', None)
    
    # Si estamos en la página de confirmación de pago, siempre usamos el perfil de cliente
    if es_confirmacion_pago and cliente:
        usar_perfil = 'Cliente'
    # De lo contrario, usamos el grupo activo
    elif grupo_activo in ['Cliente', 'Tienda']:
        usar_perfil = grupo_activo
    else:
        messages.error(request, "No se pudo determinar el perfil a usar. Por favor, selecciona un rol.")
        return redirect('direccion')
    
    # Determinar qué perfil usar para la dirección
    perfil_cliente = cliente if usar_perfil == 'Cliente' else None
    perfil_tienda = tienda if usar_perfil == 'Tienda' else None
    
    if request.method == 'POST':
        # Pasar cliente o tienda al formulario según corresponda
        form = DireccionForm(request.POST, cliente=perfil_cliente, tienda=perfil_tienda)
        if form.is_valid():
            direccion = form.save(commit=False)
            
            # Asociar la dirección al perfil correspondiente
            if perfil_cliente:
                direccion.cliente = perfil_cliente
                direccion.tienda = None  # Asegurarse de que no esté asociada a una tienda
            elif perfil_tienda:
                direccion.tienda = perfil_tienda
                direccion.cliente = None  # Asegurarse de que no esté asociada a un cliente
            
            direccion.save()
            
            # Si la solicitud es AJAX, devolver respuesta JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True, 
                    'message': 'Dirección registrada exitosamente.',
                    'direccion_id': direccion.id
                })
            
            messages.success(request, "Dirección registrada exitosamente.")
            return redirect('direccion')
        else:
            # Mostrar errores del formulario
            print(form.errors)  # Imprime los errores en la consola para depuración
            
            # Si la solicitud es AJAX, devolver errores como JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': False, 
                    'message': 'Por favor, corrija los errores en el formulario.',
                    'errors': form.errors
                }, status=400)
            
            messages.error(request, "Por favor, corrija los errores en el formulario.")
    else:
        form = DireccionForm(cliente=perfil_cliente, tienda=perfil_tienda)
    
    return render(request, 'otros/direccion.html', {'form': form})