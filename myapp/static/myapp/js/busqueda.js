document.addEventListener("DOMContentLoaded", function () {
    // Obtener elementos del DOM
    const botonCarrito = document.getElementById('boton-carrito');
    const contenedorCarrito = document.getElementById('contenedor-carrito');
    const cerrarCarrito = document.getElementById('cerrar-carrito');
    const superposicionCarrito = document.getElementById('superposicion-carrito');
    const cuerpoTablaCarrito = document.getElementById('cuerpo-tabla-carrito');
    const botonesAgregarCarrito = document.querySelectorAll('.agregar-al-carrito');
    const botonPagar = document.getElementById('pagar');

    // Variable para almacenar los productos en el carrito
    let itemsCarrito = JSON.parse(localStorage.getItem('carrito')) || [];

    // Función para mostrar el carrito
    function mostrarCarrito() {
        contenedorCarrito.style.display = 'block';
        superposicionCarrito.style.display = 'block';
    }

    // Función para cerrar el carrito
    function ocultarCarrito() {
        contenedorCarrito.style.display = 'none';
        superposicionCarrito.style.display = 'none';
    }

    // Función para agregar productos al carrito
    function agregarAlCarrito(evento) {
    const productoElemento = evento.target.closest('.producto');
    const nombreProducto = productoElemento.querySelector('.nombre-producto').textContent;
    const precioProducto = productoElemento.querySelector('.precio-producto').textContent;
    const idProductoTienda = evento.target.getAttribute('data-product-id');  // Cambiar a producto_tienda_id

    // Verificar si el producto ya está en el carrito
    const indiceProductoExistente = itemsCarrito.findIndex(item => item.id === idProductoTienda);

    if (indiceProductoExistente !== -1) {
        // Si el producto ya está en el carrito, incrementar la cantidad
        itemsCarrito[indiceProductoExistente].cantidad += 1;
    } else {
        // Si no está en el carrito, agregarlo
        itemsCarrito.push({
            id: idProductoTienda,  // Cambiar a producto_tienda_id
            nombre: nombreProducto,
            precio: parseFloat(precioProducto.replace('$', '').replace(',', '')), // Eliminar el símbolo $ y la coma
            cantidad: 1
        });
    }

    // Guardar el carrito en localStorage
    localStorage.setItem('carrito', JSON.stringify(itemsCarrito));

    // Actualizar el carrito en la interfaz
    actualizarTablaCarrito();
}


    // Función para actualizar la tabla del carrito
    function actualizarTablaCarrito() {
        // Limpiar la tabla del carrito
        cuerpoTablaCarrito.innerHTML = '';

        // Calcular subtotal
        let subtotal = 0;
        itemsCarrito.forEach(item => {
            subtotal += item.precio * item.cantidad;
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${item.nombre}</td>
                <td>${item.cantidad}</td>
                <td>$${item.precio.toFixed(2)}</td>
                <td>$${(item.precio * item.cantidad).toFixed(2)}</td>
                <td><button class="actualizar-btn btn btn-primary">Actualizar</button></td>
                <td><button class="eliminar-btn btn btn-danger" data-product-id="${item.id}">Eliminar</button></td>
            `;
            cuerpoTablaCarrito.appendChild(fila);
        });

        // Calcular IVA y total
        const iva = 0.19;
        const ivaMonto = subtotal * iva;
        const total = subtotal + ivaMonto;
        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = ivaMonto.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);

        // Asignar eventos de eliminación de productos
        const botonesEliminar = document.querySelectorAll('.eliminar-btn');
        botonesEliminar.forEach(boton => boton.addEventListener('click', eliminarDelCarrito));
    }

    // Función para eliminar productos del carrito
function eliminarDelCarrito(evento) {
    const idProductoTienda = evento.target.getAttribute('data-product-id');  // Cambiar a producto_tienda_id
    itemsCarrito = itemsCarrito.filter(item => item.id !== idProductoTienda);

    // Guardar el carrito actualizado en localStorage
    localStorage.setItem('carrito', JSON.stringify(itemsCarrito));

    actualizarTablaCarrito();
}
    // Cargar carrito desde localStorage al iniciar la página
    function cargarCarritoDesdeLocalStorage() {
        if (itemsCarrito.length > 0) {
            actualizarTablaCarrito();
        }
    }

    // Eventos para mostrar y cerrar el carrito
    botonCarrito.addEventListener('click', mostrarCarrito);
    cerrarCarrito.addEventListener('click', ocultarCarrito);
    superposicionCarrito.addEventListener('click', ocultarCarrito);

    // Asignar evento a cada botón de "Agregar al carrito"
    botonesAgregarCarrito.forEach(boton => boton.addEventListener('click', agregarAlCarrito));

    // Cargar el carrito almacenado cuando se carga la página
    cargarCarritoDesdeLocalStorage();

    // Evento para el botón "Pagar"
    botonPagar.addEventListener('click', function () {
    if (itemsCarrito.length === 0) {
        alert('El carrito está vacío. Por favor, agregue productos.');
        return;
    }

    // Guardar los datos del carrito en localStorage
    localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
    localStorage.setItem('subtotal', document.getElementById('subtotal-carrito').textContent);
    localStorage.setItem('iva', document.getElementById('iva-carrito').textContent);
    localStorage.setItem('total', document.getElementById('total-carrito').textContent);

    // Redirigir a la página de confirmación de pago
    window.location.href = '/confirmar_pago/';
});
});

// Evento para cerrar el modal de confirmación de dirección
document.getElementById('cerrar-modal-direccion')?.addEventListener('click', function () {
    document.getElementById('modal-direccion').style.display = 'none';
});
