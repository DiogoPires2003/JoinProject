$(document).ready(function() {


    const serviceInput = $('#id_service');
    const dateInput = $('#id_date');
    const hoursContainer = $('#availableHours');
    const selectedStartHourInput = $('#id_selected_start_hour');
    const selectedEndHourInput = $('#id_selected_end_hour');
    const form = $('#createAppointmentForm');
    const hourErrorContainer = $('#hour-error-message-container');


    function fetchAvailableHours() {
        const serviceId = serviceInput.val();
        const date = dateInput.val();


        hoursContainer.html('<small class="text-muted w-100 text-center">Cargando horas...</small>');
        selectedStartHourInput.val('');
        selectedEndHourInput.val('');
        hourErrorContainer.empty();

        if (serviceId && date) {

            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const selectedDate = new Date(date + 'T00:00:00');

            if (selectedDate < today) {
                hoursContainer.html('<p class="text-danger w-100 text-center">No se puede seleccionar una fecha pasada.</p>');
                return;
            }

            $.ajax({
                url: AVAILABLE_HOURS_URL,
                data: { service_id: serviceId, date: date },
                success: function(response) {
                    hoursContainer.empty();
                    if (response.available_hours && response.available_hours.length > 0) {
                        response.available_hours.forEach(hour => {
                            const button = `<button type="button" class="btn btn-outline-primary hour-btn" data-start="${hour.start}" data-end="${hour.end}">
                                                ${hour.start} - ${hour.end}
                                            </button>`;
                            hoursContainer.append(button);
                        });
                    } else if (response.error) {
                        hoursContainer.html(`<p class="text-danger w-100 text-center">Error: ${response.error}</p>`);
                    } else {
                        hoursContainer.html('<p class="text-info w-100 text-center">No hay horas disponibles.</p>');
                    }
                },
                error: function(xhr, status, error) {
                    console.error("AJAX Error:", status, error);
                    hoursContainer.html('<p class="text-danger w-100 text-center">Error al cargar las horas. Inténtelo de nuevo.</p>');
                }
            });
        } else {
             hoursContainer.html('<small class="text-muted w-100 text-center">Seleccione un servicio y una fecha para ver las horas.</small>');
        }
    }


    serviceInput.on('change', fetchAvailableHours);
    dateInput.on('change', fetchAvailableHours);


    hoursContainer.on('click', '.hour-btn', function() {
        const $this = $(this);
        selectedStartHourInput.val($this.data('start'));
        selectedEndHourInput.val($this.data('end'));
        $('.hour-btn', hoursContainer).removeClass('active');
        $this.addClass('active');
        hourErrorContainer.empty();
    });


    form.on('submit', function(event) {
        hourErrorContainer.empty();
        if (!selectedStartHourInput.val() || !selectedEndHourInput.val()) {
             hourErrorContainer.html('<p class="text-danger mt-1 mb-0">Debe seleccionar una hora disponible.</p>');
             return false;
        }
    });

});