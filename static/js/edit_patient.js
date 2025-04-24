document.addEventListener('DOMContentLoaded', function() {
    const hasInsuranceCheckbox = document.getElementById('id_has_insurance');
    const insuranceNumberInput = document.getElementById('id_insurance_number');

    function toggleInsuranceNumber() {
        if (insuranceNumberInput) {
            insuranceNumberInput.disabled = !hasInsuranceCheckbox.checked;
             if (!hasInsuranceCheckbox.checked) {
                insuranceNumberInput.value = ''; // Clear value if unchecked
                insuranceNumberInput.placeholder = 'No aplicable';
             } else {
                 insuranceNumberInput.placeholder = ''; // Reset placeholder
             }
        }
    }

    if (hasInsuranceCheckbox) {
        // Initial state on page load
        toggleInsuranceNumber();
        // Add listener for changes
        hasInsuranceCheckbox.addEventListener('change', toggleInsuranceNumber);
    }
});