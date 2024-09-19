document.addEventListener("DOMContentLoaded", function () {
    const botonPago = document.getElementById('boton-carrito');
    const botonVaciarCarrito = document.getElementById('vaciar-carrito');
    const spinner = document.getElementById('spinner'); // Seleccionar el spinner

    botonPago.addEventListener('click', function () {
        botonPago.disabled = true;
        spinner.style.display = 'block'; // Mostrar el spinner

        const direcciones = document.querySelectorAll('input[name="direccion"]');
        const direccionSeleccionada = Array.from(direcciones).find(radio => radio.checked);

        if (direccionSeleccionada) {
            const direccionId = direccionSeleccionada.value;

            // Validar el carrito antes de enviar la orden
            if (!validarCarrito()) {
                botonPago.disabled = false; // Rehabilitar el botón si la validación falla
                spinner.style.display = 'none'; // Ocultar el spinner
                return;
            }

            // Obtener datos del carrito del localStorage
            const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
            const subtotal = parseFloat(localStorage.getItem('subtotal') || '0');
            const iva = parseFloat(localStorage.getItem('iva') || '0');
            const total = parseFloat(localStorage.getItem('total') || '0');

            // Crear la orden y enviar los datos al backend
            const ordenData = {
                direccion_envio_id: direccionId,
                subtotal: subtotal,
                iva: iva,
                total: total,
                productos: carritoData.map(item => ({
                    producto_tienda_id: item.id, // Asegúrate de que esta propiedad existe en los datos del carrito
                    cantidad: item.cantidad,
                    precio_unitario: item.precio
                }))
            };

            fetch('/api/crear_orden/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify(ordenData)
            })
            .then(response => response.json())
            .then(data => {
                spinner.style.display = 'none'; // Ocultar el spinner

                if (data.success) {
                    alert(`Orden creada con éxito. ¡Gracias por su compra!\nID de Orden: ${data.orden_id}`);
                    vaciarCarrito();
                    window.location.href = '/index_cliente/';
                } else {
                    alert(`Hubo un problema al crear la orden: ${data.error}. Inténtelo de nuevo.`);
                    botonPago.disabled = false;
                }
            })
            .catch(error => {
                console.error('Error al crear la orden:', error);
                alert('Error en el servidor. Por favor, inténtelo de nuevo más tarde.');
                botonPago.disabled = false;
                spinner.style.display = 'none'; // Ocultar el spinner
            });
        } else {
            alert('Por favor, seleccione una dirección para proceder.');
            botonPago.disabled = false;
            spinner.style.display = 'none'; // Ocultar el spinner
        }
    });

    // Función para vaciar el carrito después de la compra
    function vaciarCarrito() {
        localStorage.removeItem('carrito');
        localStorage.removeItem('subtotal');
        localStorage.removeItem('iva');
        localStorage.removeItem('total');
        actualizarTablaCarrito();
    }

    // Función para validar el carrito
    function validarCarrito() {
        console.log('Ejecutando validarCarrito');
        const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
        console.log('Datos del carrito en validarCarrito:', carritoData);

        // Validar si el carrito está vacío
        if (carritoData.length === 0) {
            alert('Su carrito está vacío. Agregue productos antes de proceder al pago.');
            return false;
        }

        // Validar que todos los productos tengan una cantidad válida
        for (let item of carritoData) {
            console.log('Producto en carrito:', item);
            if (!item.id) {
                alert(`El producto no tiene un identificador válido.`);
                return false;
            }
            if (isNaN(item.cantidad) || item.cantidad <= 0) {
                alert(`La cantidad de un producto no es válida. Por favor, ajuste las cantidades.`);
                return false;
            }
        }

        return true;
    }

    function agregarAlCarrito(productoTiendaId, nombreProducto, precioProducto, cantidad) {
        const carrito = JSON.parse(localStorage.getItem('carrito')) || [];
        const productoExistente = carrito.find(item => item.producto_tienda_id === productoTiendaId);

        if (productoExistente) {
            productoExistente.cantidad += cantidad;
        } else {
            carrito.push({
                producto_tienda_id: productoTiendaId,
                nombre: nombreProducto,
                precio: precioProducto,
                cantidad: cantidad
            });
        }

        localStorage.setItem('carrito', JSON.stringify(carrito));
        console.log('Producto añadido al carrito:', carrito);
    }

    function getCSRFToken() {
        let cookieValue = null;
        const name = 'csrftoken';
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
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

        const botonesEliminar = document.querySelectorAll('.eliminar-btn');
        botonesEliminar.forEach(boton => {
            boton.addEventListener('click', function () {
                const index = this.getAttribute('data-product-index');
                carritoData.splice(index, 1);
                localStorage.setItem('carrito', JSON.stringify(carritoData));
                actualizarTablaCarrito();
            });
        });
    }

    // Función para vaciar el carrito cuando se hace clic en el botón
    if (botonVaciarCarrito) {
        botonVaciarCarrito.addEventListener('click', function() {
            if (confirm('¿Estás seguro de que deseas vaciar el carrito?')) {
                vaciarCarrito();
            }
        });
    }

    actualizarTablaCarrito();
});
