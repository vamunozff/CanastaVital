document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('direccionForm');

    form.addEventListener('submit', function (event) {
        event.preventDefault(); // Evita el envío tradicional del formulario

        const formData = new FormData(form);

        fetch(registrarDireccionUrl, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Recargar la página tras un registro exitoso
                window.location.reload();
            } else {
                // Mostrar errores si el formulario no es válido
                Swal.fire({
                    icon: 'error',
                    title: 'Error al registrar',
                    text: data.message,
                    confirmButtonText: 'Reintentar'
                });
            }
        })
        .catch(error => {
            console.error('Error al procesar la solicitud:', error);
            Swal.fire({
                icon: 'error',
                title: 'Error en el servidor',
                text: 'Hubo un problema al procesar la solicitud. Intente nuevamente.',
                confirmButtonText: 'Reintentar'
            });
        });
    });
});

document.addEventListener('DOMContentLoaded', function() {
    var deptCreate = document.getElementById('id_departamento');
    var ciudadCreate = document.getElementById('id_ciudad');

    // Cargar departamentos al cargar la página
    fetch('/get-datos/')
        .then(response => response.json())
        .then(data => {
            deptCreate.innerHTML = '<option value="">Seleccione un departamento</option>';
            data.departamentos.forEach(departamento => {
                var option = document.createElement('option');
                option.value = departamento.id;
                option.text = departamento.nombre;
                deptCreate.add(option);
            });
        })
        .catch(error => console.error('Error al cargar departamentos:', error));

    // Cargar ciudades al seleccionar un departamento
    deptCreate.addEventListener('change', function() {
        var departamentoId = this.value;
        ciudadCreate.innerHTML = '<option value="">Seleccione una ciudad</option>';

        if (departamentoId) {
            fetch(`/get-datos/?departamento=${departamentoId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.ciudades.length > 0) {
                        data.ciudades.forEach(ciudad => {
                            var option = document.createElement('option');
                            option.value = ciudad.id;
                            option.text = ciudad.nombre;
                            ciudadCreate.add(option);
                        });
                    } else {
                        var option = document.createElement('option');
                        option.text = 'No hay ciudades disponibles';
                        ciudadCreate.add(option);
                    }
                })
                .catch(error => console.error('Error al cargar ciudades:', error));
        }
    });
});


$('#modalNuevaDireccion').on('hidden.bs.modal', function () {
    $(this).find(':focus').blur();  // Eliminar el foco del botón de cierre
});
