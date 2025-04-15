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
                
                // Seleccionar la hora actual de la cita si existe
                const currentStartHour = document.getElementById('selectedHour').value;
                if (currentStartHour) {
                    const hourButtons = document.querySelectorAll('.hour-btn');
                    hourButtons.forEach(btn => {
                        if (btn.dataset.horaInicio === currentStartHour) {
                            btn.classList.add('selected');
                        }
                    });
                }
            },
            error: function() {
                horaDisponiblesContainer.innerHTML = '<p class="text-center text-danger">Error al obtener información de los servicios.</p>';
            }
        });
    }
    
    // Función para obtener horas disponibles basadas en fecha y servicio
    function getAvailableHours(date, serviceId, duracionServicio) {
        // Definir horario de trabajo (8:00 a 18:00)
        const businessHours = [];
        // Crear slots cada 'duracionServicio' minutos
        for (let hour = 8; hour < 18; hour++) {
            for (let minute = 0; minute < 60; minute += duracionServicio) {
                // Formato de hora correctamente
                const formattedHour = hour.toString().padStart(2, '0');
                const formattedMinute = minute.toString().padStart(2, '0');
                businessHours.push(`${formattedHour}:${formattedMinute}`);
            }
        }
        
        // Filtrar slots que se solaparían con otras citas
        return businessHours.filter(time => {
            // Verificar si este slot se solaparía con alguna cita reservada
            return !isOverlapping(date, serviceId, time, duracionServicio);
        });
    }
    
    // Función para verificar si un slot de tiempo se solaparía con citas existentes
    function isOverlapping(date, serviceId, startTime, duracionServicio) {
        // Parsear startTime a minutos
        const [startHour, startMinute] = startTime.split(':').map(num => parseInt(num));
        const startTimeInMinutes = startHour * 60 + startMinute;
        
        // Calcular hora de fin basada en la duración del servicio
        const endTimeInMinutes = startTimeInMinutes + duracionServicio;
        
        // Verificar solapamiento con cada cita reservada
        for (const appointment of bookedAppointments) {
            // Saltar la cita actual que estamos modificando
            if (appointment.id === currentAppointmentId) {
                continue;
            }
            
            // Solo verificar citas en la misma fecha y para el mismo servicio
            if (appointment.date === date && appointment.service_id == serviceId) {
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
        
        // También verificar si la cita se extendería más allá del horario comercial (18:00)
        if (endTimeInMinutes > 18 * 60) {
            return true; // Se extiende más allá de la hora de cierre
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
            hourBtn.className = 'btn hour-btn';
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
        return true;
    });
});