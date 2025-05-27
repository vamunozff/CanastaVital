document.addEventListener("DOMContentLoaded", function () {
    const botonPago = document.getElementById('boton-carrito');
    const botonVaciarCarrito = document.getElementById('vaciar-carrito');
    const spinner = document.getElementById('spinner');

    botonPago.addEventListener('click', async function () {
        botonPago.disabled = true;
        spinner.style.display = 'block';

        const direccionSeleccionada = document.querySelector('input[name="direccion"]:checked');
        const metodoPagoSeleccionado = document.getElementById('metodo_pago').value;

        if (!direccionSeleccionada) {
            Swal.fire('Error', 'Por favor, seleccione una dirección.', 'warning');
            finalizarProceso();
            return;
        }

        if (!metodoPagoSeleccionado) {
            Swal.fire('Error', 'Seleccione un método de pago.', 'warning');
            finalizarProceso();
            return;
        }

        if (!validarCarrito()) {
            finalizarProceso();
            return;
        }

        botonPago.textContent = 'Procesando...';

        try {
            const ordenData = prepararDatosOrden(direccionSeleccionada.value, metodoPagoSeleccionado);
            const response = await fetch('/api/crear_orden/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(ordenData)
            });
        
            if (!response.ok) {
                throw new Error(`Error HTTP: ${response.status}`);
            }
        
            const data = await response.json();
            spinner.style.display = 'none';
        
            if (data.success) {
                Swal.fire('¡Compra exitosa!', `Tu ID de orden es: ${data.orden_id}`, 'success');
                vaciarCarrito();
                window.location.href = '/index_cliente/';
            } else {
                Swal.fire('Error', `No se pudo crear la orden: ${data.error}`, 'error');
                botonPago.disabled = false;
            }
        } catch (error) {
            console.error('Error en la compra:', error);
            Swal.fire('Error', 'No se pudo procesar tu pedido.', 'error');
            finalizarProceso();
        }        
    });

    function finalizarProceso() {
        botonPago.disabled = false;
        botonPago.innerHTML  = 'Proceder al pago';
        spinner.style.display = 'none';
    }

    function prepararDatosOrden(direccionId, metodoPagoId) {
        const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
        const subtotal = parseFloat(localStorage.getItem('subtotal') || '0');
        const iva = subtotal * 0.19;
        const total = subtotal + iva;

        // Asegurarse de que todos los IDs sean números
        const productosValidados = carritoData.map(item => ({
            producto_tienda_id: parseInt(item.producto_tienda_id),
            cantidad: parseInt(item.cantidad),
            precio_unitario: parseFloat(item.precio)
        }));

        return {
            direccion_envio_id: parseInt(direccionId),
            metodo_pago_id: parseInt(metodoPagoId),
            subtotal,
            iva,
            total,
            productos: productosValidados
        };
    }

    
    function vaciarCarrito() {
        localStorage.removeItem('carrito');
        localStorage.removeItem('subtotal');
        localStorage.removeItem('iva');
        localStorage.removeItem('total');
        actualizarTablaCarrito();
    }

    function validarCarrito() {
        console.log('Ejecutando validarCarrito');
        const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
        console.log('Datos del carrito en validarCarrito:', carritoData);
    
        if (carritoData.length === 0) {
            Swal.fire('Carrito vacío', 'Su carrito está vacío. Agregue productos antes de proceder al pago.', 'warning');
            return false;
        }
    
        for (let item of carritoData) {
            console.log('Producto en carrito:', JSON.stringify(item));
    
            // Convertir a número y validar
            const productoId = parseInt(item.producto_tienda_id);
            if (isNaN(productoId) || productoId <= 0) { 
                Swal.fire('Error', `El producto "${item.nombre}" no tiene un identificador válido.`, 'error');
                console.error(`ID inválido para ${item.nombre}: ${item.producto_tienda_id}`);
                return false;
            }
            
            const cantidad = parseInt(item.cantidad);
            if (isNaN(cantidad) || cantidad <= 0) {
                Swal.fire('Error', `La cantidad del producto "${item.nombre}" no es válida.`, 'error');
                return false;
            }
            
            // Actualizar el item con los valores convertidos
            item.producto_tienda_id = productoId;
            item.cantidad = cantidad;
        }
        
        // Guardar el carrito con los valores convertidos
        localStorage.setItem('carrito', JSON.stringify(carritoData));
        
        return true;
    }
    
    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        document.cookie.split(';').forEach(cookie => {
            cookie = cookie.trim();
            if (cookie.startsWith(name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
            }
        });
        return cookieValue;
    }

    function actualizarTablaCarrito() {
        const cuerpoTablaCarrito = document.getElementById('cuerpo-tabla-carrito');
        const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
        cuerpoTablaCarrito.innerHTML = '';

        if (carritoData.length === 0) {
            const filaMensaje = document.createElement('tr');
            filaMensaje.id = 'mensaje-vacio';
            filaMensaje.innerHTML = '<td colspan="5" class="text-center">Tu carrito está vacío.</td>';
            cuerpoTablaCarrito.appendChild(filaMensaje);
        } else {
            carritoData.forEach((item, index) => {
                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${item.nombre}</td>
                    <td>${item.cantidad}</td>
                    <td>$${parseFloat(item.precio).toFixed(2)}</td>
                    <td>$${(parseFloat(item.precio) * parseInt(item.cantidad)).toFixed(2)}</td>
                    <td><button class="eliminar-btn btn btn-danger" data-index="${index}">Eliminar</button></td>
                `;
                cuerpoTablaCarrito.appendChild(fila);
            });
        }

        const subtotal = carritoData.reduce((sum, item) => sum + parseFloat(item.precio) * parseInt(item.cantidad), 0);
        const iva = subtotal * 0.19;
        const total = subtotal + iva;

        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = iva.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);

        // Guardar los totales en localStorage
        localStorage.setItem('subtotal', subtotal.toString());
        localStorage.setItem('iva', iva.toString());
        localStorage.setItem('total', total.toString());

        // Agregar event listeners a los botones de eliminar
        document.querySelectorAll('.eliminar-btn').forEach(boton => {
            boton.addEventListener('click', function() {
                const index = parseInt(this.getAttribute('data-index'));
                eliminarProducto(index);
            });
        });        
    }

    function eliminarProducto(index) {
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        if (index >= 0 && index < carrito.length) {
            carrito.splice(index, 1);
            localStorage.setItem('carrito', JSON.stringify(carrito));
            actualizarTablaCarrito();
        }
    }

    if (botonVaciarCarrito) {
        botonVaciarCarrito.addEventListener('click', function () {
            Swal.fire({
                title: '¿Vaciar carrito?',
                text: 'Esta acción no se puede deshacer.',
                icon: 'warning',
                showCancelButton: true,
                confirmButtonText: 'Sí, vaciar',
                cancelButtonText: 'Cancelar'
            }).then((result) => {
                if (result.isConfirmed) {
                    vaciarCarrito();
                }
            });
        });
    }

    // Inicializar la tabla del carrito
    actualizarTablaCarrito();
});