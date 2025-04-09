$(document).ready(function() {
    // Initialize select2
    $('#servicioInput').select2({
        placeholder: "Seleccione el tipo de servicio",
        allowClear: true
    });

    // Fetch services via AJAX
    $.ajax({
        url: "/api/servicios/",
        method: "GET",
        success: function(response) {
            $('#servicioInput').empty().append('<option value="" disabled selected>Seleccione el tipo de servicio</option>');
            response.forEach(function(service) {
                $('#servicioInput').append(new Option(service.nombre, service.id));
            });
        },
        error: function() {
            alert("Error al cargar los servicios.");
        }
    });

    // Validate if the selected date is in the past
    $('#fechaInput').on('change', function() {
        var selectedDate = $(this).val();
        var currentDate = new Date();
        var formattedCurrentDate = currentDate.toISOString().split('T')[0]; // Format as YYYY-MM-DD

        if (selectedDate < formattedCurrentDate) {
            alert("No se puede seleccionar una fecha que ya ha pasado.");
            $(this).val('');  // Clear the selected date field
        } else {
            // Si la fecha es válida y hay un servicio seleccionado, cargamos las horas
            var servicioId = $('#servicioInput').val();
            if (servicioId) {
                cargarHorasDisponibles(servicioId, selectedDate);
            }
        }
    });

    // Cargar las horas disponibles cuando se selecciona un servicio (si ya hay una fecha seleccionada)
    $('#servicioInput').on('change', function() {
        var servicioId = $(this).val();
        var fecha = $('#fechaInput').val();

        if (servicioId && fecha) {
            cargarHorasDisponibles(servicioId, fecha);
        }
    });

    // Update hidden input when an hour is selected - delegación de eventos para botones dinámicos
    $(document).on('click', '.hour-btn', function() {
        var startHour = $(this).data('hora-inicio');
        var endHour = $(this).data('hora-fin');

        // Asegúrate de que los valores se están asignando correctamente
        $('#selectedHour').val(startHour);
        $('#selectedEndHour').val(endHour);

        // Resaltar el botón seleccionado
        $('.hour-btn').removeClass('selected');
        $(this).addClass('selected');
    });

    // Validación del formulario antes de enviarlo
    $('form').on('submit', function(e) {
        var servicioId = $('#servicioInput').val();
        var fecha = $('#fechaInput').val();
        var horaInicio = $('#selectedHour').val();

        if (!servicioId || !fecha || !horaInicio) {
            e.preventDefault();
            alert("Por favor complete todos los campos requeridos: servicio, fecha y hora.");
            return false;
        }
        return true;
    });
});

// Function to load available hours based on service duration
function cargarHorasDisponibles(servicioId, fecha) {
    $('#horaDisponibles').empty();
    $('.info-servicio').remove();
    $('#horaDisponibles').html('<p class="text-center">Cargando horarios disponibles...</p>');

    // Primero, obtener la duración del servicio seleccionado
    $.ajax({
        url: "/api/servicios/",
        method: "GET",
        success: function(servicios) {
            // Encontrar el servicio seleccionado por ID
            var servicioSeleccionado = servicios.find(function(servicio) {
                return servicio.id == servicioId;
            });

            if (!servicioSeleccionado) {
                $('#horaDisponibles').html('<p class="text-center text-danger">Error: No se encontró información del servicio seleccionado.</p>');
                return;
            }

            // Limpiar el contenedor
            $('#horaDisponibles').empty();

            // Obtener la duración en minutos del servicio
            var duracionServicio = servicioSeleccionado.duracion_minutos;

            // Si la duración es 0 o no está definida, usar 30 minutos como valor predeterminado
            if (!duracionServicio || duracionServicio <= 0) {
                duracionServicio = 30;
            }

            // Horario de trabajo
            var horaInicio = 8;  // 8 AM
            var horaFin = 20;    // 8 PM

            var slotsCreados = 0;

            // Generar los slots de tiempo según la duración del servicio
            for (var hora = horaInicio; hora < horaFin; hora++) {
                for (var minuto = 0; minuto < 60; minuto += duracionServicio) {
                    // Si la combinación de hora + duración excede el horario de cierre, no la mostramos
                    var finalizaEnHora = hora + Math.floor((minuto + duracionServicio) / 60);
                    var finalizaEnMinuto = (minuto + duracionServicio) % 60;

                    if (finalizaEnHora > horaFin || (finalizaEnHora === horaFin && finalizaEnMinuto > 0)) {
                        continue;
                    }

                    var horaInicioFormateada =
                        (hora < 10 ? '0' : '') + hora + ':' +
                        (minuto === 0 ? '00' : (minuto < 10 ? '0' + minuto : minuto));

                    var horaFinFormateada =
                        (finalizaEnHora < 10 ? '0' : '') + finalizaEnHora + ':' +
                        (finalizaEnMinuto === 0 ? '00' : (finalizaEnMinuto < 10 ? '0' + finalizaEnMinuto : finalizaEnMinuto));

                    // Check if this time slot is already booked
                    var isBooked = false;

                    // Loop through booked appointments
                    for (var i = 0; i < bookedAppointments.length; i++) {
                        var appointment = bookedAppointments[i];

                        // Check appointments for the selected date AND service
                        if (appointment.date === fecha && appointment.service_id == servicioId) {
                            // Convertir horas a minutos desde el inicio del día para facilitar comparaciones
                            var citaInicio = appointment.start.split(':');
                            var citaHoraInicio = parseInt(citaInicio[0]);
                            var citaMinInicio = parseInt(citaInicio[1]);
                            var citaInicioMinutos = citaHoraInicio * 60 + citaMinInicio;

                            var citaFin;
                            var citaFinMinutos;

                            if (appointment.end) {
                                citaFin = appointment.end.split(':');
                                citaFinMinutos = parseInt(citaFin[0]) * 60 + parseInt(citaFin[1]);
                            } else {
                                // Si no hay hora de fin, asumimos la duración del servicio actual
                                citaFinMinutos = citaInicioMinutos + appointment.duracion_minutos || duracionServicio;
                            }

                            // Slot actual en minutos
                            var slotInicioMinutos = hora * 60 + minuto;
                            var slotFinMinutos = finalizaEnHora * 60 + finalizaEnMinuto;

                            // Verificar si hay solapamiento
                            if ((slotInicioMinutos < citaFinMinutos && slotFinMinutos > citaInicioMinutos)) {
                                isBooked = true;
                                break;
                            }
                        }
                    }

                    // Only create button if time slot is not booked
                    if (!isBooked) {
                        var button = $('<button type="button" class="btn hour-btn" data-hora-inicio="' + horaInicioFormateada + '" data-hora-fin="' + horaFinFormateada + '">' +
                                      horaInicioFormateada + ' a ' + horaFinFormateada + '</button>');

                        $('#horaDisponibles').append(button);
                        slotsCreados++;
                    }
                }
            }

            // Si no hay horas disponibles, mostrar un mensaje
            if (slotsCreados === 0) {
                $('#horaDisponibles').html('<p class="text-center mt-3">No hay horas disponibles para este servicio en la fecha seleccionada.</p>');
            }

            // Mostrar información del servicio seleccionado
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
        },
        error: function() {
            $('#horaDisponibles').html('<p class="text-center text-danger">Error al obtener información de los servicios.</p>');
        }
    });
}