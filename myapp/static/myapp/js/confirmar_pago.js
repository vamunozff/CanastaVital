document.addEventListener("DOMContentLoaded", function () {
    const botonPago = document.getElementById('boton-carrito');
    const modalDireccion = document.getElementById('modal-direccion');
    const cerrarModal = document.getElementById('cerrar-modal-direccion');
    const direccionSeleccionada = document.getElementById('direccion-seleccionada');
    const selectDireccion = document.getElementById('select-direccion');
    const formDireccion = document.getElementById('form-confirmar-direccion');

    // Mostrar el modal al hacer clic en "Proceder al Pago"
    botonPago.addEventListener('click', function () {
        modalDireccion.style.display = 'block';
    });

    // Cerrar el modal al hacer clic en la "X"
    cerrarModal.addEventListener('click', function () {
        modalDireccion.style.display = 'none';
    });

    // Manejar el cambio en el selector de direcciones
    if (selectDireccion) {
        selectDireccion.addEventListener('change', function () {
            const direccionSeleccionadaTexto = selectDireccion.options[selectDireccion.selectedIndex].innerHTML;
            direccionSeleccionada.innerHTML = direccionSeleccionadaTexto;
        });
    }

    // Confirmar dirección y procesar el pago
    formDireccion?.addEventListener('submit', function (evento) {
        evento.preventDefault();
        const direccion = document.getElementById('direccion').value.trim();
        const ciudad = document.getElementById('ciudad').value.trim();
        const codigoPostal = document.getElementById('codigo-postal').value.trim();

        if (direccion && ciudad && codigoPostal) {
            // Verificar si la dirección ya existe en el selector
            const opciones = Array.from(selectDireccion.options);
            const direccionExistente = opciones.some(option => option.textContent.includes(direccion) && option.textContent.includes(ciudad) && option.textContent.includes(codigoPostal));

            if (!direccionExistente) {
                // Agregar la nueva dirección al selector
                const nuevoOption = document.createElement('option');
                nuevoOption.innerHTML = `${direccion}<br>${ciudad}<br>${codigoPostal}`;
                nuevoOption.value = '';  // Opcional: asignar un ID o algún valor si lo necesitas
                selectDireccion.appendChild(nuevoOption);
                selectDireccion.value = nuevoOption.value;
                direccionSeleccionada.innerHTML = nuevoOption.innerHTML;
            }

            // Confirmar el pago después de seleccionar o ingresar la dirección
            alert(`Gracias por su compra. Su pedido será enviado a:\n${direccion}\n${ciudad}\n${codigoPostal}`);
            modalDireccion.style.display = 'none';

            // Vaciar el carrito solo después de confirmar la dirección y el pago
            localStorage.removeItem('carrito');
            localStorage.removeItem('subtotal');
            localStorage.removeItem('iva');
            localStorage.removeItem('total');
            alert('El carrito se ha vaciado.');
        } else {
            alert('Por favor, complete todos los campos.');
        }
    });

    // Cerrar el modal al hacer clic fuera
    window.onclick = function (evento) {
        if (evento.target == modalDireccion) {
            modalDireccion.style.display = 'none';
        }
    };
});

// Código para cargar los productos del carrito
document.addEventListener("DOMContentLoaded", function () {
    const carritoData = JSON.parse(localStorage.getItem('carrito')) || [];
    const subtotal = parseFloat(localStorage.getItem('subtotal') || '0');
    const iva = parseFloat(localStorage.getItem('iva') || '0');
    const total = parseFloat(localStorage.getItem('total') || '0');

    function actualizarTablaCarrito() {
        const cuerpoTablaCarrito = document.getElementById('cuerpo-tabla-carrito');
        cuerpoTablaCarrito.innerHTML = '';

        carritoData.forEach(item => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${item.nombre}</td>
                <td>${item.cantidad}</td>
                <td>$${item.precio.toFixed(2)}</td>
                <td>$${(item.precio * item.cantidad).toFixed(2)}</td>
                <td><button class="eliminar-btn btn btn-danger" data-product-id="${item.id}">Eliminar</button></td>
            `;
            cuerpoTablaCarrito.appendChild(fila);
        });

        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = iva.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);
    }

    actualizarTablaCarrito();
});
