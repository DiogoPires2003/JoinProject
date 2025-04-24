$(document).ready(function() {
    const dateInput = $('#id_date');
    const hoursContainer = $('#availableHours');
    const selectedStartHourInput = $('#selectedHour');
    const form = $('#editAppointmentForm');
    const hourErrorContainer = $('#hour-error-message-container');


    function fetchAndDisplayAvailableHours(selectedDateStr) {
         hoursContainer.html('<small class="text-muted w-100 text-center">Cargando horas...</small>');
         hourErrorContainer.empty();
         selectedStartHourInput.val(''); // Reset hidden field

         if (!serviceId || !selectedDateStr) {
              hoursContainer.html('<small class="text-muted w-100 text-center">Seleccione una fecha.</small>');
             return;
         }

         console.log("Fetching hours for:", selectedDateStr, "Service:", serviceId); // Log para debug

        hoursContainer.empty();
        const simulatedHours = [];
        let currentHour = 8; let currentMinute = 0; const endDayHour = 20;
        while (currentHour < endDayHour) {
            const startStr = `${String(currentHour).padStart(2, '0')}:${String(currentMinute).padStart(2, '0')}`;
            let endTotalMinutes = (currentHour * 60 + currentMinute) + serviceDuration;
            let endH = Math.floor(endTotalMinutes / 60) % 24;
            let endM = endTotalMinutes % 60;
            const endStr = `${String(endH).padStart(2, '0')}:${String(endM).padStart(2, '0')}`;
            let isBooked = false;
            for(const booked of bookedAppointments) {
                if(booked.date === selectedDateStr && booked.id !== currentAppointmentId) {
                    if (startStr < booked.end && endStr > booked.start) {
                        isBooked = true; break;
                    }
                }
            }
            if (!isBooked) simulatedHours.push({ start: startStr, end: endStr });
            currentMinute += 30;
            currentHour += Math.floor(currentMinute / 60);
            currentMinute %= 60;
        }
        if (simulatedHours.length > 0) {
            let hourSet = false;
            simulatedHours.forEach(hour => {
                const isActive = (selectedDateStr === initialDate && hour.start === initialStartHour);
                // Aquí está el cambio: mostramos tanto la hora de inicio como la de fin
                const button = `<button type="button" class="btn btn-outline-primary hour-btn ${isActive ? 'active' : ''}"
                                data-start="${hour.start}" data-end="${hour.end}">
                                    ${hour.start} - ${hour.end}
                                </button>`;
                hoursContainer.append(button);
                if(isActive) { selectedStartHourInput.val(hour.start); hourSet = true; }
            });
            if (selectedDateStr === initialDate && !hourSet) { selectedStartHourInput.val(''); initialStartHour = ''; }
        } else {
            hoursContainer.html('<p class="text-info w-100 text-center">No hay horas disponibles (simulación).</p>');
            selectedStartHourInput.val('');
        }
    } // Fin fetchAndDisplayAvailableHours

    // --- Evento cambio de fecha ---
    dateInput.on('change', function() {
        const selectedDate = $(this).val();
        initialStartHour = '';
        fetchAndDisplayAvailableHours(selectedDate);
    });

    // --- Evento click en botón de hora ---
    hoursContainer.on('click', '.hour-btn', function() {
        const $this = $(this);
        selectedStartHourInput.val($this.data('start'));
        $('.hour-btn', hoursContainer).removeClass('active');
        $this.addClass('active');
        hourErrorContainer.empty();
    });

    // --- Validación frontend antes de enviar ---
    form.on('submit', function(event) {
        hourErrorContainer.empty(); // Limpia errores previos
        if (!selectedStartHourInput.val()) {
             hourErrorContainer.html('Debe seleccionar una hora disponible.');
             event.preventDefault(); // Detiene el envío
             return false;
        }
    });

    fetchAndDisplayAvailableHours(dateInput.val());
});