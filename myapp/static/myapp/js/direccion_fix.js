document.addEventListener('DOMContentLoaded', function () {
    // Seleccionar todos los formularios de dirección, no solo el que tiene ID direccionForm
    const forms = document.querySelectorAll('form[action*="registrar_direccion"]');
    
    forms.forEach(form => {
        form.addEventListener('submit', function (event) {
            event.preventDefault(); // Evita el envío tradicional del formulario
            
            const formData = new FormData(form);
            const url = form.getAttribute('action');
            
            // Añadir encabezado para indicar que es una solicitud AJAX
            fetch(url, {
                method: 'POST',
                body: formData,
                headers: {
                    'X-Requested-With': 'XMLHttpRequest',
                    'X-CSRFToken': form.querySelector('[name=csrfmiddlewaretoken]').value,
                }
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error en la respuesta del servidor: ' + response.status);
                }
                return response.json();
            })
            .then(data => {
                if (data.success) {
                    // Mostrar mensaje de éxito
                    Swal.fire({
                        icon: 'success',
                        title: '¡Éxito!',
                        text: data.message || 'Dirección registrada correctamente',
                        confirmButtonText: 'Aceptar'
                    }).then(() => {
                        // Recargar la página tras un registro exitoso
                        window.location.reload();
                    });
                } else {
                    // Mostrar errores si el formulario no es válido
                    let errorMessage = data.message || 'Error al registrar la dirección';
                    
                    // Si hay errores específicos, mostrarlos
                    if (data.errors) {
                        errorMessage += '<ul>';
                        for (const field in data.errors) {
                            data.errors[field].forEach(error => {
                                errorMessage += `<li>${field}: ${error}</li>`;
                            });
                        }
                        errorMessage += '</ul>';
                    }
                    
                    Swal.fire({
                        icon: 'error',
                        title: 'Error al registrar',
                        html: errorMessage,
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

    // Función para cargar departamentos y ciudades
    function setupDepartamentosYCiudades() {
        const departamentoSelects = document.querySelectorAll('select[name="departamento"]');
        
        departamentoSelects.forEach(deptSelect => {
            const formContainer = deptSelect.closest('form') || deptSelect.closest('div.modal-body');
            const ciudadSelect = formContainer.querySelector('select[name="ciudad"]');
            
            if (!ciudadSelect) return;
            
            // Cargar departamentos al cargar la página
            fetch('/get-datos/')
                .then(response => response.json())
                .then(data => {
                    // Mantener la opción seleccionada si existe
                    const selectedDeptId = deptSelect.value;
                    
                    deptSelect.innerHTML = '<option value="">Seleccione un departamento</option>';
                    data.departamentos.forEach(departamento => {
                        const option = document.createElement('option');
                        option.value = departamento.id;
                        option.text = departamento.nombre;
                        if (departamento.id == selectedDeptId) {
                            option.selected = true;
                        }
                        deptSelect.add(option);
                    });
                    
                    // Si hay un departamento seleccionado, cargar sus ciudades
                    if (deptSelect.value) {
                        cargarCiudades(deptSelect.value, ciudadSelect);
                    }
                })
                .catch(error => console.error('Error al cargar departamentos:', error));
            
            // Cargar ciudades al seleccionar un departamento
            deptSelect.addEventListener('change', function() {
                const departamentoId = this.value;
                cargarCiudades(departamentoId, ciudadSelect);
            });
        });
    }
    
    function cargarCiudades(departamentoId, ciudadSelect) {
        ciudadSelect.innerHTML = '<option value="">Seleccione una ciudad</option>';
        
        if (departamentoId) {
            fetch(`/get-datos/?departamento=${departamentoId}`)
                .then(response => response.json())
                .then(data => {
                    if (data.ciudades && data.ciudades.length > 0) {
                        data.ciudades.forEach(ciudad => {
                            const option = document.createElement('option');
                            option.value = ciudad.id;
                            option.text = ciudad.nombre;
                            ciudadSelect.add(option);
                        });
                    } else {
                        const option = document.createElement('option');
                        option.text = 'No hay ciudades disponibles';
                        ciudadSelect.add(option);
                    }
                })
                .catch(error => console.error('Error al cargar ciudades:', error));
        }
    }
    
    // Inicializar departamentos y ciudades
    setupDepartamentosYCiudades();
    
    // Manejar la apertura del modal
    const modals = document.querySelectorAll('.modal');
    if (modals.length > 0) {
        modals.forEach(modal => {
            modal.addEventListener('shown.bs.modal', function() {
                setupDepartamentosYCiudades();
            });
            
            modal.addEventListener('hidden.bs.modal', function() {
                // Limpiar el formulario al cerrar el modal
                const form = modal.querySelector('form');
                if (form) form.reset();
            });
        });
    }
});