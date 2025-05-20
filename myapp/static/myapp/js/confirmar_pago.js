document.addEventListener("DOMContentLoaded", function () {
    const botonPago = document.getElementById('boton-carrito');
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
                // Mostrar mensaje de "Procesando su solicitud"
                Swal.fire({
                    title: 'Procesando su solicitud...',
                    text: 'Por favor espere un momento.',
                    allowOutsideClick: false,
                    allowEscapeKey: false,
                    didOpen: () => {
                        Swal.showLoading();
                    }
                });

                // Esperar 1.5 segundos y luego mostrar éxito
                setTimeout(() => {
                    Swal.fire({
                        icon: 'success',
                        title: '¡Compra exitosa!',
                        text: `Tu ID de orden es: ${data.orden_id}`,
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        vaciarCarrito();
                        window.location.href = '/index_cliente/';
                    });
                }, 1500);
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
            producto_tienda_id: parseInt(item.producto_tienda_id || item.id),
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

        // Crear un nuevo array con el formato correcto
        const carritoCorregido = [];

        for (let item of carritoData) {
            console.log('Producto en carrito:', JSON.stringify(item));

            // Usar id si producto_tienda_id no está disponible
            const productoId = parseInt(item.producto_tienda_id || item.id);
            if (isNaN(productoId) || productoId <= 0) { 
                Swal.fire('Error', `El producto "${item.nombre}" no tiene un identificador válido.`, 'error');
                console.error(`ID inválido para ${item.nombre}: ${item.id || item.producto_tienda_id}`);
                return false;
            }
            
            const cantidad = parseInt(item.cantidad);
            if (isNaN(cantidad) || cantidad <= 0) {
                Swal.fire('Error', `La cantidad del producto "${item.nombre}" no es válida.`, 'error');
                return false;
            }
            
            // Crear un nuevo objeto con el formato correcto
            carritoCorregido.push({
                producto_tienda_id: productoId,
                nombre: item.nombre,
                precio: parseFloat(item.precio),
                cantidad: cantidad
            });
        }
        
        // Guardar el carrito con el formato correcto
        localStorage.setItem('carrito', JSON.stringify(carritoCorregido));
        
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
            filaMensaje.innerHTML = '<td colspan="8" class="text-center">Tu carrito está vacío.</td>';
            cuerpoTablaCarrito.appendChild(filaMensaje);
        } else {
            carritoData.forEach((item, index) => {
                const precioUnitario = parseFloat(item.precio).toFixed(2);
                const descuento = item.descuento || 0;
                const descuentoTexto = descuento > 0 ? descuento + '%' : '—';
                const precioActualizado = descuento > 0 ? (item.precio * (1 - descuento / 100)).toFixed(2) : precioUnitario;
                const precioTotal = (precioActualizado * item.cantidad).toFixed(2);

                const fila = document.createElement('tr');
                fila.innerHTML = `
                    <td>${item.nombre}</td>
                    <td>${item.cantidad}</td>
                    <td>$${precioUnitario}</td>
                    <td>${descuentoTexto}</td>
                    <td>$${precioActualizado}</td>
                    <td>$${precioTotal}</td>
                    <td>
                        <button class="btn btn-outline-secondary btn-sm btn-menos" data-index="${index}" title="Quitar uno"><i class="fas fa-minus"></i></button>
                        <button class="btn btn-outline-secondary btn-sm btn-mas" data-index="${index}" title="Agregar uno"><i class="fas fa-plus"></i></button>
                    </td>
                `;
                cuerpoTablaCarrito.appendChild(fila);
            });
        }

        // Cambia el cálculo del subtotal para que use el precio con descuento
        const subtotal = carritoData.reduce((sum, item) => {
            const descuento = item.descuento || 0;
            const precioActualizado = descuento > 0
                ? (parseFloat(item.precio) * (1 - descuento / 100))
                : parseFloat(item.precio);
            return sum + (precioActualizado * parseInt(item.cantidad));
        }, 0);

        const iva = subtotal * 0.19;
        const total = subtotal + iva;

        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = iva.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);

        // Guardar los totales en localStorage
        localStorage.setItem('subtotal', subtotal.toString());
        localStorage.setItem('iva', iva.toString());
        localStorage.setItem('total', total.toString());

        // Botones menos, más y eliminar
        document.querySelectorAll('.btn-menos').forEach(boton => {
            boton.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-index'));
                modificarCantidad(idx, -1);
            });
        });
        document.querySelectorAll('.btn-mas').forEach(boton => {
            boton.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-index'));
                modificarCantidad(idx, 1);
            });
        });
        document.querySelectorAll('.eliminar-btn').forEach(boton => {
            boton.addEventListener('click', function() {
                const idx = parseInt(this.getAttribute('data-index'));
                eliminarProducto(idx);
            });
        });
    }

    function modificarCantidad(index, delta) {
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        if (index >= 0 && index < carrito.length) {
            carrito[index].cantidad += delta;
            if (carrito[index].cantidad <= 0) {
                carrito.splice(index, 1);
            }
            localStorage.setItem('carrito', JSON.stringify(carrito));
            actualizarTablaCarrito();
        }
    }

    function eliminarProducto(index) {
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        if (index >= 0 && index < carrito.length) {
            carrito.splice(index, 1);
            localStorage.setItem('carrito', JSON.stringify(carrito));
            actualizarTablaCarrito();
        }
    }

    const botonVaciarCarrito = document.getElementById('vaciar-carrito');
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

    // Inicializar la tabla del carrito al cargar la página
    actualizarTablaCarrito();
});