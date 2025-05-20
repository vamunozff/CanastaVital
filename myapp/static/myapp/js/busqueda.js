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
        const precioProducto = parseFloat(productoElemento.querySelector('.precio-producto').textContent.replace(/[^0-9.,]/g, '').replace(',', '.'));
        const idProductoTienda = evento.target.getAttribute('data-product-id');
        const descuento = parseInt(evento.target.getAttribute('data-descuento')) || 0;

        // Verificar si el producto ya está en el carrito
        const indiceProductoExistente = itemsCarrito.findIndex(item => item.id === idProductoTienda);

        if (indiceProductoExistente !== -1) {
            itemsCarrito[indiceProductoExistente].cantidad += 1;
        } else {
            itemsCarrito.push({
                id: idProductoTienda,
                nombre: nombreProducto,
                precio: precioProducto, // Guardar el precio como número decimal
                cantidad: 1,
                descuento: descuento
            });
        }

        localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
        actualizarTablaCarrito();
        actualizarContadorCarrito(itemsCarrito.reduce((total, item) => total + item.cantidad, 0));
    }

    // Función para actualizar la tabla del carrito
    function actualizarTablaCarrito() {
        cuerpoTablaCarrito.innerHTML = '';
        let subtotal = 0;

        itemsCarrito.forEach(item => {
            const precioUnitario = parseFloat(item.precio).toFixed(2);
            const descuento = item.descuento || 0;
            const descuentoTexto = descuento > 0 ? descuento + '%' : '—';
            const precioActualizado = descuento > 0 ? (item.precio * (1 - descuento / 100)).toFixed(2) : precioUnitario;
            const precioTotal = (precioActualizado * item.cantidad).toFixed(2);
            subtotal += parseFloat(precioTotal);

            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${item.nombre}</td>
                <td>${item.cantidad}</td>
                <td>$${precioUnitario}</td>
                <td>${descuentoTexto}</td>
                <td>$${precioActualizado}</td>
                <td>$${precioTotal}</td>
                <td>
                    <button class="btn btn-outline-secondary btn-sm btn-menos" data-product-id="${item.id}" title="Quitar uno"><i class="fas fa-minus"></i></button>
                    <button class="btn btn-outline-secondary btn-sm btn-mas" data-product-id="${item.id}" title="Agregar uno"><i class="fas fa-plus"></i></button>
                </td>
            `;
            cuerpoTablaCarrito.appendChild(fila);
        });

        // Calcular IVA y total
        const iva = 0.19;
        const ivaMonto = parseFloat((subtotal * iva).toFixed(2));
        const total = parseFloat((subtotal + ivaMonto).toFixed(2));

        document.getElementById('subtotal-carrito').textContent = subtotal.toFixed(2);
        document.getElementById('iva-carrito').textContent = ivaMonto.toFixed(2);
        document.getElementById('total-carrito').textContent = total.toFixed(2);

        // Asignar eventos a los botones menos y más
        const botonesMenos = document.querySelectorAll('.btn-menos');
        const botonesMas = document.querySelectorAll('.btn-mas');
        botonesMenos.forEach(boton => boton.addEventListener('click', disminuirCantidad));
        botonesMas.forEach(boton => boton.addEventListener('click', aumentarCantidad));
    }

    // Función para disminuir la cantidad
    function disminuirCantidad(evento) {
        const idProducto = evento.currentTarget.getAttribute('data-product-id');
        const index = itemsCarrito.findIndex(item => item.id === idProducto);
        if (index !== -1) {
            if (itemsCarrito[index].cantidad > 1) {
                itemsCarrito[index].cantidad -= 1;
            } else {
                // Si la cantidad es 1 y se presiona menos, eliminar el producto
                itemsCarrito.splice(index, 1);
            }
            localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
            actualizarTablaCarrito();
            actualizarContadorCarrito(itemsCarrito.reduce((total, item) => total + item.cantidad, 0));
        }
    }

    // Función para aumentar la cantidad
    function aumentarCantidad(evento) {
        const idProducto = evento.currentTarget.getAttribute('data-product-id');
        const index = itemsCarrito.findIndex(item => item.id === idProducto);
        if (index !== -1) {
            itemsCarrito[index].cantidad += 1;
            localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
            actualizarTablaCarrito();
            actualizarContadorCarrito(itemsCarrito.reduce((total, item) => total + item.cantidad, 0));
        }
    }

    // Función para vaciar todo el carrito
    const botonVaciarCarrito = document.getElementById('vaciar-carrito');
    if (botonVaciarCarrito) {
        botonVaciarCarrito.addEventListener('click', function () {
            itemsCarrito = [];
            localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
            actualizarTablaCarrito();
            actualizarContadorCarrito(0);
        });
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
        localStorage.setItem('carrito', JSON.stringify(itemsCarrito));
        localStorage.setItem('subtotal', document.getElementById('subtotal-carrito').textContent);
        localStorage.setItem('iva', document.getElementById('iva-carrito').textContent);
        localStorage.setItem('total', document.getElementById('total-carrito').textContent);
        window.location.href = '/confirmar_pago/';
    });

    // Evento para cerrar el modal de confirmación de dirección (si existe)
    const cerrarModalDireccion = document.getElementById('cerrar-modal-direccion');
    if (cerrarModalDireccion) {
        cerrarModalDireccion.addEventListener('click', function () {
            document.getElementById('modal-direccion').style.display = 'none';
        });
    }
});

// Función para actualizar el contador del carrito en el icono
function actualizarContadorCarrito(nuevoConteo) {
    let badge = document.querySelector('.fa-cart-shopping + .badge, .fa-cart-shopping ~ .badge, .fa-cart-shopping').parentElement.querySelector('.badge');
    if (!badge) {
        // Si no existe el badge, créalo
        let icon = document.querySelector('.fa-cart-shopping');
        if (icon) {
            badge = document.createElement('span');
            badge.className = 'position-absolute top-0 start-100 translate-middle badge rounded-pill bg-danger';
            icon.parentElement.appendChild(badge);
        }
    }
    if (badge) {
        badge.textContent = nuevoConteo;
        badge.style.display = nuevoConteo > 0 ? 'inline' : 'none';
    }
}
