document.addEventListener('DOMContentLoaded', function() {
    // Get the date input element
    const dateInput = document.querySelector('[name="date"]');

    // Add event listener for date change
    dateInput.addEventListener('change', function() {
        loadAvailableHours();
    });

    // Initial load of available hours for the pre-selected date
    loadAvailableHours();

    // Function to load available hours based on selected date and service
    function loadAvailableHours() {
        const selectedDate = dateInput.value;
        const serviceId = document.querySelector('[name="service_id"]').value;

        if (!selectedDate || !serviceId) {
            return;
        }

        // Determine available hours for the selected date
        const availableHours = getAvailableHours(selectedDate, serviceId);
        displayAvailableHours(availableHours);

        // Select the current appointment's time if it exists
        const currentStartHour = document.getElementById('selectedHour').value;
        if (currentStartHour) {
            const hourButtons = document.querySelectorAll('.hour-btn');
            hourButtons.forEach(btn => {
                if (btn.dataset.hora === currentStartHour) {
                    btn.classList.add('selected');
                }
            });
        }
    }

    // Function to get available hours based on date and service
    function getAvailableHours(date, serviceId) {
        // Define business hours (8:00 to 18:00)
        const businessHours = [];
        for (let hour = 8; hour < 18; hour++) {
            businessHours.push(`${hour.toString().padStart(2, '0')}:00`);
            businessHours.push(`${hour.toString().padStart(2, '0')}:30`);
        }

        // Filter out booked hours for the selected date and service
        const bookedHours = [];
        bookedAppointments.forEach(appointment => {
            if (appointment.date === date && appointment.service_id == serviceId && appointment.id !== currentAppointmentId) {
                bookedHours.push(appointment.start);
            }
        });

        // Return available hours (hours that are not booked)
        return businessHours.filter(hour => !bookedHours.includes(hour));
    }

    // Function to display available hours in the UI
    function displayAvailableHours(hours) {
        const horaDisponiblesContainer = document.getElementById('horaDisponibles');
        horaDisponiblesContainer.innerHTML = '';

        if (hours.length === 0) {
            horaDisponiblesContainer.innerHTML = '<p>No hay horas disponibles para la fecha seleccionada.</p>';
            return;
        }

        hours.forEach(hour => {
            // Calculate end hour (30 minutes later)
            const [h, m] = hour.split(':');
            let endHour = parseInt(h);
            let endMinute = parseInt(m) + 30;

            if (endMinute >= 60) {
                endHour += 1;
                endMinute -= 60;
            }

            const endTime = `${endHour.toString().padStart(2, '0')}:${endMinute.toString().padStart(2, '0')}`;

            const hourBtn = document.createElement('button');
            hourBtn.type = 'button';
            hourBtn.className = 'hour-btn';
            hourBtn.textContent = hour;
            hourBtn.dataset.hora = hour;
            hourBtn.dataset.endHora = endTime;

            hourBtn.addEventListener('click', function() {
                // Remove 'selected' class from all hour buttons
                document.querySelectorAll('.hour-btn').forEach(btn => {
                    btn.classList.remove('selected');
                });

                // Add 'selected' class to the clicked button
                this.classList.add('selected');

                // Update hidden inputs with selected start and end hours
                document.getElementById('selectedHour').value = this.dataset.hora;
                document.getElementById('selectedEndHour').value = this.dataset.endHora;
            });

            horaDisponiblesContainer.appendChild(hourBtn);
        });
    }
});