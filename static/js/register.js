function toggleInsuranceNumber() {
    var hasInsuranceCheckbox = document.getElementById('id_has_insurance');
    var insuranceNumberField = document.getElementById('insuranceNumberContainer');
    var insuranceNumberInput = document.getElementById('id_insurance_number'); // Get the input itself

    if (hasInsuranceCheckbox.checked) {
        insuranceNumberField.style.display = 'block';
        insuranceNumberInput.setAttribute('required', 'required'); // Make it required for JS validation
    } else {
        insuranceNumberField.style.display = 'none';
        insuranceNumberInput.removeAttribute('required'); // Remove required
        // Optionally clear validation state if it was previously invalid
        insuranceNumberInput.classList.remove('is-invalid', 'is-valid');
        const errorDiv = insuranceNumberInput.nextElementSibling;
        if (errorDiv && errorDiv.classList.contains('invalid-feedback')) {
            errorDiv.style.display = 'none';
            errorDiv.textContent = '';
        }
    }
}


function validateForm(form, submitButton, originalButtonHTML) {
    const validators = {
        firstNameInput: (value) => {
            if (!value) return 'El nombre es requerido';
            if (value.length < 2) return 'El nombre debe tener al menos 2 caracteres';
            return '';
        },
        lastNameInput: (value) => {
            if (!value) return 'El apellido es requerido';
            if (value.length < 2) return 'El apellido debe tener al menos 2 caracteres';
            return '';
        },
        dniInput: (value) => {
            if (!value) return 'El DNI/NIE es requerido';
            const dniRegex = /^[0-9XYZ][0-9]{7}[A-Z]$/i;
            if (!dniRegex.test(value)) return 'DNI/NIE no válido';
            return '';
        },
        emailInput: (value) => {
            if (!value) return 'El correo electrónico es requerido';
            const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
            if (!emailRegex.test(value)) return 'Correo electrónico no válido';
            return '';
        },
        phoneInput: (value) => {
            if (!value) return 'El teléfono es requerido';
            const phoneRegex = /^[0-9]{9}$/;
            if (!phoneRegex.test(value)) return 'Teléfono no válido (9 dígitos)';
            return '';
        },
        passwordInput: (value) => {
            if (!value) return 'La contraseña es requerida';
            if (value.length < 8) return 'La contraseña debe tener al menos 8 caracteres';
            return '';
        },
        confirmPasswordInput: (value) => {
            const password = document.getElementById('passwordInput').value;
            if (!value) return 'Debe confirmar la contraseña';
            if (value !== password) return 'Las contraseñas no coinciden';
            return '';
        },
        id_insurance_number: (value) => {
            const hasInsurance = document.getElementById('id_has_insurance').checked;
            if (hasInsurance) {
                if (!value) return 'El número de mutua es requerido';
                if (!/^[A-Z][0-9]{5}$/.test(value)) return 'Debe comenzar con una letra seguida de 5 dígitos';
            }
            return '';
        }
    };

    function validateField(input) {
        // Do not validate hidden insurance field if not required
        if (input.id === 'id_insurance_number' && !document.getElementById('id_has_insurance').checked) {
            input.classList.remove('is-invalid', 'is-valid');
            const errorDiv = input.closest('.form-floating').querySelector('.invalid-feedback') || input.nextElementSibling;
            if (errorDiv) {
                errorDiv.textContent = '';
                errorDiv.style.display = 'none';
            }
            return true;
        }

        const errorDiv = input.closest('.form-floating').querySelector('.invalid-feedback') || input.nextElementSibling;
        const error = validators[input.id]?.(input.value.trim());

        if (error) {
            input.classList.add('is-invalid');
            input.classList.remove('is-valid');
            if (errorDiv) {
                errorDiv.textContent = error;
                errorDiv.style.display = 'block';
            }
        } else {
            input.classList.remove('is-invalid');

            if (input.value.trim() || !input.hasAttribute('required')) {
                input.classList.add('is-valid');
            }
            if (errorDiv) {
                errorDiv.textContent = '';
                errorDiv.style.display = 'none';
            }
        }
        return !error;
    }


    form.querySelectorAll('input').forEach(input => {
        if (input.type !== 'checkbox') {
            input.addEventListener('input', () => validateField(input));
            input.addEventListener('blur', () => validateField(input));
        }
    });


    const passwordInput = document.getElementById('passwordInput');
    if (passwordInput) {
        passwordInput.addEventListener('input', () => {
            const confirmPassword = document.getElementById('confirmPasswordInput');
            if (confirmPassword && confirmPassword.value) {
                validateField(confirmPassword);
            }
        });
    }

    form.addEventListener('submit', (e) => {
        e.preventDefault();

        let isFormValid = true;

        form.querySelectorAll('input').forEach(input => {
            if (input.type !== 'checkbox') {
                if (input.offsetParent !== null) {
                    if (!validateField(input)) {
                        isFormValid = false;
                    }
                }
            }
        });
        // Specifically check insurance number if it's supposed to be visible and required
        const insuranceCheckbox = document.getElementById('id_has_insurance');
        const insuranceNumberInput = document.getElementById('id_insurance_number');
        if (insuranceCheckbox && insuranceCheckbox.checked && insuranceNumberInput) {
            if (!validateField(insuranceNumberInput)) {
                isFormValid = false;
            }
        }


        if (isFormValid) {

            if (submitButton) {
                submitButton.disabled = true;
                submitButton.innerHTML = `
                    <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                    Cargando...
                `;
            }
            form.submit();
        } else {

            if (submitButton) {
                submitButton.disabled = false;
                submitButton.innerHTML = originalButtonHTML;
            }

            const firstInvalid = form.querySelector('.is-invalid');
            if (firstInvalid) {
                firstInvalid.focus();
            }
        }
    });
}


document.addEventListener('DOMContentLoaded', function() {

    var hasInsuranceCheckbox = document.getElementById('id_has_insurance');
    if (hasInsuranceCheckbox) {
        hasInsuranceCheckbox.addEventListener('change', toggleInsuranceNumber);
        toggleInsuranceNumber();
    }

    const registrationForm = document.getElementById('registrationForm');
    const registerSubmitButton = document.getElementById('registerSubmitButton');

    const originalButtonHTML = registerSubmitButton ? registerSubmitButton.innerHTML : 'Registrarse';

    if (registrationForm && registerSubmitButton) {

        registerSubmitButton.disabled = false;
        registerSubmitButton.innerHTML = originalButtonHTML;

        validateForm(registrationForm, registerSubmitButton, originalButtonHTML);
    }
});


