document.addEventListener("DOMContentLoaded", function () {
    const botonPago = document.getElementById('boton-carrito');

    botonPago.addEventListener('click', function () {
        const direcciones = document.querySelectorAll('input[name="direccion"]');
        const direccionSeleccionada = Array.from(direcciones).find(radio => radio.checked);

        if (direccionSeleccionada) {
            const direccionId = direccionSeleccionada.value;

            // Validar el carrito antes de enviar la orden
            if (!validarCarrito()) {
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
                if (data.success) {
                    alert(`Orden creada con éxito. ¡Gracias por su compra!\nID de Orden: ${data.orden_id}`);
                    // Vaciar el carrito
                    localStorage.removeItem('carrito');
                    localStorage.removeItem('subtotal');
                    localStorage.removeItem('iva');
                    localStorage.removeItem('total');

                    // Redirigir a una página de confirmación o gracias
                    window.location.href = '/index_cliente/';
                } else {
                    alert(`Hubo un problema al crear la orden: ${data.error}. Inténtelo de nuevo.`);
                }
            })
            .catch(error => {
                console.error('Error al crear la orden:', error);
                alert('Error en el servidor. Por favor, inténtelo de nuevo más tarde.');
            });
        } else {
            alert('Por favor, seleccione una dirección para proceder.');
        }
    });

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




    // Función para obtener el token CSRF (si estás utilizando Django)
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

    // Código para cargar los productos del carrito
    const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
    const subtotal = parseFloat(localStorage.getItem('subtotal') || '0');
    const iva = parseFloat(localStorage.getItem('iva') || '0');
    const total = parseFloat(localStorage.getItem('total') || '0');

    function actualizarTablaCarrito() {
        const cuerpoTablaCarrito = document.getElementById('cuerpo-tabla-carrito');
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

    function actualizarTotales() {
        let subtotalCalc = 0;
        carritoData.forEach(item => {
            subtotalCalc += item.precio * item.cantidad;
        });
        const ivaCalc = subtotalCalc * 0.19;
        const totalCalc = subtotalCalc + ivaCalc;

        localStorage.setItem('subtotal', subtotalCalc.toFixed(2));
        localStorage.setItem('iva', ivaCalc.toFixed(2));
        localStorage.setItem('total', totalCalc.toFixed(2));

        document.getElementById('subtotal-carrito').textContent = subtotalCalc.toFixed(2);
        document.getElementById('iva-carrito').textContent = ivaCalc.toFixed(2);
        document.getElementById('total-carrito').textContent = totalCalc.toFixed(2);
    }

    actualizarTablaCarrito();
});
