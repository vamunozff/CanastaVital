
        document.addEventListener('DOMContentLoaded', function() {
            const proveedorSelect = document.getElementById('txtProveedor_id');
            const proveedorModal = new bootstrap.Modal(document.getElementById('proveedorModal'));

            document.querySelectorAll('.proveedor-info').forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    document.getElementById('proveedorNombre').innerText = `Nombre: ${item.getAttribute('data-nombre')}`;
                    document.getElementById('proveedorDireccion').innerText = `Dirección: ${item.getAttribute('data-direccion')}`;
                    document.getElementById('proveedorTelefono').innerText = `Teléfono: ${item.getAttribute('data-telefono')}`;
                    document.getElementById('proveedorEmail').innerText = `Email: ${item.getAttribute('data-email')}`;
                    proveedorModal.show();
                });
            });

                    // Script para el modal de la categoría
            const categoriaModal = new bootstrap.Modal(document.getElementById('categoriaModal'));

            document.querySelectorAll('.categoria-info').forEach(item => {
                item.addEventListener('click', function(e) {
                    e.preventDefault();
                    // Cargar los datos de la categoría al modal
                    document.getElementById('categoriaNombre').innerText = `Nombre: ${item.getAttribute('data-nombre')}`;
                    document.getElementById('categoriaDescripcion').innerText = `Descripción: ${item.getAttribute('data-descripcion')}`;
                    // Mostrar el modal
                    categoriaModal.show();
                });
            });
        });



    document.getElementById('search-button').addEventListener('click', function() {
    let searchQuery = document.getElementById('search-input').value.toLowerCase();
    let rows = document.querySelectorAll('#product-table-body tr');
    rows.forEach(row => {
        let productName = row.querySelector('td:nth-child(2)').innerText.toLowerCase();
        if (productName.includes(searchQuery)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

document.getElementById('filter-status').addEventListener('change', function() {
    let selectedStatus = this.value.toLowerCase();
    let rows = document.querySelectorAll('#product-table-body tr');
    rows.forEach(row => {
        let productStatus = row.querySelector('td:nth-child(8) span').innerText.toLowerCase();
        if (selectedStatus === '' || productStatus.includes(selectedStatus)) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});

document.getElementById('filter-category').addEventListener('change', function() {
    let selectedCategory = this.value;
    let rows = document.querySelectorAll('#product-table-body tr');
    rows.forEach(row => {
        let productCategory = row.querySelector('td:nth-child(5)').innerText.trim();
        if (selectedCategory === '' || productCategory === selectedCategory) {
            row.style.display = '';
        } else {
            row.style.display = 'none';
        }
    });
});
