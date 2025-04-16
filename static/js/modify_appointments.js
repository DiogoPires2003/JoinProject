document.addEventListener('DOMContentLoaded', function() {
    // Obtener elementos del DOM
    const dateInput = document.querySelector('[name="date"]');
    const serviceDuration = parseInt(document.getElementById('serviceDuration').value);
    
    console.log("Duración del servicio:", serviceDuration, "minutos");
    
    // Añadir event listener para cambio de fecha
    dateInput.addEventListener('change', function() {
        loadAvailableHours();
    });
    
    // Event listener para cambio de servicio (si existe)
    const serviceSelect = document.querySelector('[name="service_id"]');
    if (serviceSelect) {
        serviceSelect.addEventListener('change', function() {
            loadAvailableHours();
        });
    }
    
    // Carga inicial de horas disponibles para la fecha preseleccionada
    loadAvailableHours();
    
    // Función para cargar horas disponibles basadas en fecha y servicio seleccionados
    function loadAvailableHours() {
        const selectedDate = dateInput.value;
        const serviceId = document.querySelector('[name="service_id"]').value;
        
        if (!selectedDate || !serviceId) {
            return;
        }
        
        // Mostrar mensaje de carga
        const horaDisponiblesContainer = document.getElementById('horaDisponibles');
        horaDisponiblesContainer.innerHTML = '<p class="text-center">Cargando horarios disponibles...</p>';

        // Obtener información del servicio para verificar su duración
        $.ajax({
            url: "/api/servicios/",
            method: "GET",
            success: function(servicios) {
                // Encontrar el servicio seleccionado por ID
                var servicioSeleccionado = servicios.find(function(servicio) {
                    return servicio.id == serviceId;
                });

                if (!servicioSeleccionado) {
                    horaDisponiblesContainer.innerHTML = '<p class="text-center text-danger">Error: No se encontró información del servicio seleccionado.</p>';
                    return;
                }

                // Obtener la duración en minutos del servicio
                var duracionServicio = servicioSeleccionado.duracion_minutos;

                // Si la duración es 0 o no está definida, usar el valor del DOM o 30 minutos como predeterminado
                if (!duracionServicio || duracionServicio <= 0) {
                    duracionServicio = serviceDuration || 30;
                }

                // Determinar horas disponibles para la fecha seleccionada
                const availableHours = getAvailableHours(selectedDate, serviceId, duracionServicio);
                displayAvailableHours(availableHours, duracionServicio);

                // Mostrar información del servicio seleccionado
                displayServiceInfo(servicioSeleccionado);

                // Obtener la fecha y hora actual de la cita
                const currentAppointmentDate = getCurrentAppointmentDate();
                const currentStartHour = getCurrentAppointmentStartHour();

                // Si la fecha seleccionada es diferente a la fecha actual de la cita,
                // entonces limpiamos la selección para obligar a elegir un nuevo horario
                if (selectedDate !== currentAppointmentDate) {
                    document.getElementById('selectedHour').value = '';
                    document.getElementById('selectedEndHour').value = '';
                }
            },
            error: function() {
                horaDisponiblesContainer.innerHTML = '<p class="text-center text-danger">Error al obtener información de los servicios.</p>';
            }
        });
    }

    // Función para obtener la fecha actual de la cita que estamos modificando
    function getCurrentAppointmentDate() {
        // Buscamos en las citas reservadas la que coincide con el ID actual
        for (const appointment of bookedAppointments) {
            if (appointment.id === currentAppointmentId) {
                return appointment.date;
            }
        }
        return null;
    }

    // Función para obtener la hora de inicio actual de la cita que estamos modificando
    function getCurrentAppointmentStartHour() {
        // Buscamos en las citas reservadas la que coincide con el ID actual
        for (const appointment of bookedAppointments) {
            if (appointment.id === currentAppointmentId) {
                return appointment.start;
            }
        }
        return null;
    }

    // Función para obtener horas disponibles basadas en fecha y servicio
    function getAvailableHours(date, serviceId, duracionServicio) {
        // Definir horario de trabajo (8:00 a 18:00)
        const businessHours = [];

        // Obtener la hora actual de la cita que estamos modificando
        const currentStartHour = getCurrentAppointmentStartHour();
        const currentAppointmentDate = getCurrentAppointmentDate();

        // Crear slots cada 'duracionServicio' minutos
        for (let hour = 8; hour < 20; hour++) {
            for (let minute = 0; minute < 60; minute += duracionServicio) {
                // Verificar que no creamos slots que terminen después de las 18:00
                const endMinutes = hour * 60 + minute + duracionServicio;
                if (endMinutes <= 20 * 60) {
                    // Formato de hora correctamente
                    const formattedHour = hour.toString().padStart(2, '0');
                    const formattedMinute = minute.toString().padStart(2, '0');
                    const timeSlot = `${formattedHour}:${formattedMinute}`;

                    // Excluir el horario actual de la cita si estamos en la misma fecha
                    if (date === currentAppointmentDate && timeSlot === currentStartHour) {
                        continue; // Saltamos este horario porque es el actual de la cita
                    }

                    // Solo añadir este slot si no se solapa con ninguna cita existente
                    if (!isTimeSlotOverlapping(date, serviceId, timeSlot, duracionServicio)) {
                        businessHours.push(timeSlot);
                    }
                }
            }
        }

        return businessHours;
    }

    // Función para verificar si un slot de tiempo se solaparía con citas existentes
    function isTimeSlotOverlapping(date, serviceId, startTime, duracionServicio) {
        // Parsear startTime a minutos
        const [startHour, startMinute] = startTime.split(':').map(num => parseInt(num));
        const startTimeInMinutes = startHour * 60 + startMinute;

        // Calcular hora de fin basada en la duración del servicio
        const endTimeInMinutes = startTimeInMinutes + duracionServicio;

        // Verificar solapamiento con cada cita reservada
        for (const appointment of bookedAppointments) {
            // Saltar la cita actual que estamos modificando (si estamos en modo edición)
            if (appointment.id === currentAppointmentId) {
                continue;
            }

            // Solo verificar citas en la misma fecha
            if (appointment.date === date) {
                // Parsear horas de la cita a minutos
                const [apptStartHour, apptStartMinute] = appointment.start.split(':').map(num => parseInt(num));
                const apptStartTimeInMinutes = apptStartHour * 60 + apptStartMinute;

                let apptEndTimeInMinutes;

                if (appointment.end) {
                    const [apptEndHour, apptEndMinute] = appointment.end.split(':').map(num => parseInt(num));
                    apptEndTimeInMinutes = apptEndHour * 60 + apptEndMinute;
                } else {
                    // Si no hay hora de fin, asumimos la duración del servicio actual
                    apptEndTimeInMinutes = apptStartTimeInMinutes + duracionServicio;
                }

                // Verificar solapamiento
                if (startTimeInMinutes < apptEndTimeInMinutes && endTimeInMinutes > apptStartTimeInMinutes) {
                    return true; // Hay solapamiento
                }
            }
        }

        return false; // No hay solapamiento
    }

    // Función para formatear tiempo de minutos a HH:MM
    function formatTime(minutes) {
        const hours = Math.floor(minutes / 60);
        const mins = minutes % 60;
        return `${hours.toString().padStart(2, '0')}:${mins.toString().padStart(2, '0')}`;
    }

    // Función para mostrar horas disponibles en la UI
    function displayAvailableHours(hours, duracionServicio) {
        const horaDisponiblesContainer = document.getElementById('horaDisponibles');
        horaDisponiblesContainer.innerHTML = '';

        if (hours.length === 0) {
            horaDisponiblesContainer.innerHTML = '<p class="text-center mt-3">No hay horas disponibles para la fecha seleccionada.</p>';
            return;
        }

        hours.forEach(hour => {
            // Parsear la hora de inicio
            const [startHour, startMinute] = hour.split(':').map(num => parseInt(num));
            const startTimeInMinutes = startHour * 60 + startMinute;

            // Calcular hora de fin basada en la duración del servicio
            const endTimeInMinutes = startTimeInMinutes + duracionServicio;
            const endHour = Math.floor(endTimeInMinutes / 60);
            const endMinute = endTimeInMinutes % 60;
            const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;

            // Formatear el texto de visualización como "X:XX a X:XX"
            const displayText = `${hour} a ${endTime}`;

            const hourBtn = document.createElement('button');
            hourBtn.type = 'button';
            hourBtn.className = 'btn hour-btn btn-available'; // Todas las horas son disponibles
            hourBtn.textContent = displayText;
            hourBtn.dataset.horaInicio = hour;
            hourBtn.dataset.horaFin = endTime;

            hourBtn.addEventListener('click', function() {
                // Quitar clase 'selected' de todos los botones de hora
                document.querySelectorAll('.hour-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });

                // Añadir clase 'selected' al botón clicado
                this.classList.add('selected');

                // Actualizar inputs ocultos con horas de inicio y fin seleccionadas
                document.getElementById('selectedHour').value = this.dataset.horaInicio;
                document.getElementById('selectedEndHour').value = this.dataset.horaFin;
            });

            horaDisponiblesContainer.appendChild(hourBtn);
        });
    }

    // Función para mostrar información del servicio seleccionado
    function displayServiceInfo(servicioSeleccionado) {
        // Eliminar información de servicio previa
        $('.info-servicio').remove();

        if (servicioSeleccionado) {
            var infoServicio = '<div class="mt-3 mb-4 p-3 bg-light rounded info-servicio">' +
                '<h5>' + servicioSeleccionado.nombre + '</h5>' +
                '<p class="mb-1"><small>Duración: ' + servicioSeleccionado.duracion_minutos + ' minutos</small></p>';

            if (servicioSeleccionado.descripcion) {
                infoServicio += '<p class="mb-1"><small>' + servicioSeleccionado.descripcion + '</small></p>';
            }

            if (servicioSeleccionado.precio) {
                infoServicio += '<p class="mb-0"><small>Precio: €' + servicioSeleccionado.precio.toFixed(2) + '</small></p>';
            }

            if (servicioSeleccionado.incluido_mutua) {
                infoServicio += '<p class="mb-0 text-success"><small><strong>Incluido en mutua</strong></small></p>';
            }

            infoServicio += '</div>';

            // Insertar antes de los horarios disponibles
            $(infoServicio).insertBefore('#horaDisponibles');
        }
    }

   // Validación del formulario antes de enviarlo
    $('form').on('submit', function(e) {
        var servicioId = $('[name="service_id"]').val();
        var fecha = $('[name="date"]').val();
        var horaInicio = $('#selectedHour').val();

        if (!servicioId || !fecha || !horaInicio) {
            e.preventDefault();
            alert("Por favor complete todos los campos requeridos: servicio, fecha y hora.");
            return false;
        }

        const currentAppointmentDate = getCurrentAppointmentDate();
        const currentStartHour = getCurrentAppointmentStartHour();

        // Verificar que no se está intentando guardar con la misma fecha y hora
        if (fecha === currentAppointmentDate && horaInicio === currentStartHour) {
            e.preventDefault();
            alert("Debes seleccionar una fecha u horario diferente al actual.");
            return false;
        }

        // Mostrar mensaje de éxito
        alert("¡Cita modificada con éxito!");

        return true;
    });

    // Verificar si venimos de un envío exitoso del formulario
    if (sessionStorage.getItem('formSubmitted') === 'true' &&
        document.querySelector('.alert-info') &&
        document.querySelector('.alert-info').textContent.includes('Cita modificada correctamente')) {

        // Obtener y mostrar el diálogo
        const successDialog = document.getElementById('reservaExitosaDialog');
        successDialog.showModal();

        // Limpiar el indicador de envío de formulario
        sessionStorage.removeItem('formSubmitted');

        // Opcional: agregar cerrar el diálogo al hacer clic fuera
        successDialog.addEventListener('click', function(event) {
            const rect = successDialog.getBoundingClientRect();
            const isInDialog = (rect.top <= event.clientY && event.clientY <= rect.top + rect.height &&
                rect.left <= event.clientX && event.clientX <= rect.left + rect.width);
            if (!isInDialog) {
                successDialog.close();
                window.location.href = '{% url "my_appointments" %}';
            }
        });
    }
});