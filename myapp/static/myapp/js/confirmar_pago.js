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

        return {
            direccion_envio_id: direccionId,
            metodo_pago_id: metodoPagoId,
            subtotal,
            iva,
            total,
            productos: carritoData.map(item => ({
                producto_tienda_id: item.producto_tienda_id,
                cantidad: item.cantidad,
                precio_unitario: item.precio
            }))
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
            alert('Su carrito está vacío. Agregue productos antes de proceder al pago.');
            return false;
        }
    
        for (let item of carritoData) {
            console.log('Producto en carrito:', JSON.stringify(item));
    
            if (!item.producto_tienda_id) { 
                alert(`El producto "${item.nombre}" no tiene un identificador válido.`);
                return false;
            }
            if (isNaN(item.cantidad) || item.cantidad <= 0) {
                alert(`La cantidad del producto "${item.nombre}" no es válida.`);
                return false;
            }
        }
    
        return true;
    }
    
    function agregarAlCarrito(producto_tienda_id, nombre, precio, cantidad) {
        if (isNaN(cantidad) || cantidad <= 0) {
            alert('Cantidad inválida. Debe ser un número mayor a 0.');
            return;
        }
    
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        const productoExistente = carrito.find(item => item.producto_tienda_id === producto_tienda_id);
    
        if (productoExistente) {
            productoExistente.cantidad += cantidad;
        } else {
            carrito.push({
                producto_tienda_id,
                nombre,
                precio,
                cantidad
            });
        }
    
        localStorage.setItem('carrito', JSON.stringify(carrito));
        console.log('Carrito actualizado:', carrito);
        actualizarTablaCarrito();
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

        carritoData.forEach((item, index) => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${item.nombre}</td>
                <td>${item.cantidad}</td>
                <td>$${item.precio.toFixed(2)}</td>
                <td>$${(item.precio * item.cantidad).toFixed(2)}</td>
                <td><button class="eliminar-btn btn btn-danger" data-product-index="${index}">Eliminar</button></td>
            `;
            cuerpoTablaCarrito.appendChild(fila);
        });

        const subtotal = carritoData.reduce((sum, item) => sum + item.precio * item.cantidad, 0);
        const iva = subtotal * 0.19;
        const total = subtotal + iva;

        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = iva.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);

        document.querySelectorAll('.eliminar-btn').forEach(boton => {
            boton.addEventListener('click', function () {
                const productoId = parseInt(this.getAttribute('data-product-id'));
                const nuevoCarrito = carritoData.filter(item => item.producto_tienda_id !== productoId);
                localStorage.setItem('carrito', JSON.stringify(nuevoCarrito));
                actualizarTablaCarrito();
            });
        });        
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

    actualizarTablaCarrito();
});

