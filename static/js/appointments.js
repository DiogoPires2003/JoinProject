$(document).ready(function() {
    // Initialize select2
    $('#servicioInput').select2({
        placeholder: "Seleccione el tipo de servicio",
        allowClear: true
    });

    // Populate services using local data or backend-provided data
    if (typeof availableServices !== 'undefined' && Array.isArray(availableServices)) {
        $('#servicioInput').empty().append('<option value="" disabled selected>Seleccione el tipo de servicio</option>');
        availableServices.forEach(function(service) {
            $('#servicioInput').append(new Option(service.nombre, service.id));
        });
    } else {
        alert("Error al cargar los servicios.");
    }

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

    // Replace this with local data or backend-provided data
    var servicioSeleccionado = bookedAppointments.find(function(appointment) {
        return appointment.service_id == servicioId;
    });

    if (!servicioSeleccionado) {
        $('#horaDisponibles').html('<p class="text-center text-danger">Error: No se encontró información del servicio seleccionado.</p>');
        return;
    }

    // Obtener la duración en minutos del servicio
    var duracionServicio = servicioSeleccionado.duracion_minutos || 30;

    // Horario de trabajo
    var horaInicio = 8;  // 8 AM
    var horaFin = 20;    // 8 PM

    var slotsCreados = 0;

    // Generar los slots de tiempo según la duración del servicio
    for (var hora = horaInicio; hora < horaFin; hora++) {
        for (var minuto = 0; minuto < 60; minuto += duracionServicio) {
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

            var isBooked = bookedAppointments.some(function(appointment) {
                return appointment.date === fecha &&
                    appointment.service_id == servicioId &&
                    ((hora * 60 + minuto) < (parseInt(appointment.end.split(':')[0]) * 60 + parseInt(appointment.end.split(':')[1])) &&
                    (finalizaEnHora * 60 + finalizaEnMinuto) > (parseInt(appointment.start.split(':')[0]) * 60 + parseInt(appointment.start.split(':')[1])));
            });

            if (!isBooked) {
                var button = $('<button type="button" class="btn hour-btn" data-hora-inicio="' + horaInicioFormateada + '" data-hora-fin="' + horaFinFormateada + '">' +
                              horaInicioFormateada + ' a ' + horaFinFormateada + '</button>');

                $('#horaDisponibles').append(button);
                slotsCreados++;
            }
        }
    }

    if (slotsCreados === 0) {
        $('#horaDisponibles').html('<p class="text-center mt-3">No hay horas disponibles para este servicio en la fecha seleccionada.</p>');
    }
}