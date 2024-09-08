document.addEventListener("DOMContentLoaded", function () {
    // Obtener elementos del DOM
    const botonCarrito = document.getElementById('boton-carrito');
    const contenedorCarrito = document.getElementById('contenedor-carrito');
    const cerrarCarrito = document.getElementById('cerrar-carrito');
    const superposicionCarrito = document.getElementById('superposicion-carrito');
    const cuerpoTablaCarrito = document.getElementById('cuerpo-tabla-carrito');
    const botonesAgregarCarrito = document.querySelectorAll('.agregar-al-carrito');

    // Variable para almacenar los productos en el carrito
    let itemsCarrito = [];

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
        const nombreProducto = productoElemento.querySelector('p').textContent;
        const precioProducto = productoElemento.querySelector('p:nth-child(4)').textContent;
        const idProducto = evento.target.getAttribute('data-product-id');

        // Verificar si el producto ya está en el carrito
        const indiceProductoExistente = itemsCarrito.findIndex(item => item.id === idProducto);

        if (indiceProductoExistente !== -1) {
            // Si el producto ya está en el carrito, incrementar la cantidad
            itemsCarrito[indiceProductoExistente].cantidad += 1;
        } else {
            // Si no está en el carrito, agregarlo
            itemsCarrito.push({
                id: idProducto,
                nombre: nombreProducto,
                precio: parseFloat(precioProducto.replace('$', '').replace(',', '')), // Eliminar el símbolo $ y la coma
                cantidad: 1
            });
        }

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
                <td><button class="actualizar-btn">Actualizar</button></td>
                <td><button class="eliminar-btn" data-product-id="${item.id}">Eliminar</button></td>
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
        const idProducto = evento.target.getAttribute('data-product-id');
        itemsCarrito = itemsCarrito.filter(item => item.id !== idProducto);
        actualizarTablaCarrito();
    }

    // Eventos para mostrar y cerrar el carrito
    botonCarrito.addEventListener('click', mostrarCarrito);
    cerrarCarrito.addEventListener('click', ocultarCarrito);
    superposicionCarrito.addEventListener('click', ocultarCarrito);

    // Asignar evento a cada botón de "Agregar al carrito"
    botonesAgregarCarrito.forEach(boton => boton.addEventListener('click', agregarAlCarrito));
});
