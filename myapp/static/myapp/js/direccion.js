document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('direccionForm');

    form.addEventListener('submit', function(event) {
        event.preventDefault();  // Evita el envío tradicional del formulario

        const formData = new FormData(form);  // Captura los datos del formulario

        fetch(registrarDireccionUrl,  {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                // Si la dirección se registró con éxito, muestra una alerta de SweetAlert
                Swal.fire({
                    icon: 'success',
                    title: '¡Dirección registrada!',
                    text: 'La nueva dirección ha sido registrada correctamente.',
                    confirmButtonText: 'Aceptar'
                }).then(() => {
                    // Cerrar el modal, resetear el formulario y recargar la página
                    $('#modalNuevaDireccion').modal('hide');
                    form.reset();
                    window.location.reload();  // Recargar la página después de la confirmación
                });
            } else {
                // Si hubo un error en la validación, muestra los errores
                Swal.fire({
                    icon: 'error',
                    title: 'Error al registrar',
                    text: 'Error: ' + data.message,
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