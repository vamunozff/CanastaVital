"""
Función crear_orden corregida para eliminar la referencia a Perfil
"""

@login_required
def crear_orden(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)

            # Obtener el cliente directamente del usuario actual
            try:
                cliente = Cliente.objects.get(usuario=request.user)
            except Cliente.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'No tienes un cliente asociado a tu cuenta.'}, status=400)

            direccion_envio_id = data.get('direccion_envio_id')
            subtotal = float(data.get('subtotal', 0))
            iva = float(data.get('iva', 0))
            total = float(data.get('total', 0))
            productos = data.get('productos', [])

            if not productos:
                return JsonResponse({'success': False, 'error': 'El carrito está vacío.'})

            direccion_envio = Direccion.objects.get(id=direccion_envio_id, cliente=cliente)

            tienda_ids = set()
            for item in productos:
                try:
                    producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'])
                    tienda_ids.add(producto_tienda.tienda.id)
                except ProductosTiendas.DoesNotExist:
                    return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado.'})

            if len(tienda_ids) != 1:
                return JsonResponse({'success': False, 'error': 'Todos los productos deben pertenecer a la misma tienda.'})

            tienda_id = tienda_ids.pop()
            tienda = Tienda.objects.get(id=tienda_id)

            with transaction.atomic():

                orden = Orden.objects.create(
                    cliente=cliente,
                    tienda=tienda,
                    direccion_envio=direccion_envio,
                    subtotal=0,
                    iva=iva,
                    total=total,
                    estado='pendiente'
                )

                subtotal_orden = 0

                for item in productos:
                    try:
                        producto_tienda = ProductosTiendas.objects.get(id=item['producto_tienda_id'], estado='activo')
                        cantidad = int(item['cantidad'])
                        precio_unitario = float(item['precio_unitario'])
                        subtotal_producto = cantidad * precio_unitario
                        subtotal_orden += subtotal_producto

                        # Crear ProductoOrden
                        ProductoOrden.objects.create(
                            orden=orden,
                            producto_tienda=producto_tienda,
                            cantidad=cantidad,
                            precio_unitario=precio_unitario
                        )

                        producto_tienda.cantidad -= cantidad
                        producto_tienda.save()

                    except ProductosTiendas.DoesNotExist:
                        return JsonResponse({'success': False, 'error': f'Producto en tienda con ID {item["producto_tienda_id"]} no encontrado o inactivo.'})

                orden.subtotal = subtotal_orden
                orden.save()

            return JsonResponse({'success': True, 'orden_id': orden.id})

        except Direccion.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Dirección de envío no encontrada.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

    return JsonResponse({'success': False, 'error': 'Método no permitido'}, status=405)