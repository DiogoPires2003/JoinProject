document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginButton = document.getElementById('loginSubmitButton');
    const originalButtonHTML = loginButton ? loginButton.innerHTML : 'Acceder';

    if (loginForm && loginButton) {

        loginButton.disabled = false;
        loginButton.innerHTML = originalButtonHTML;

        loginForm.addEventListener('submit', function(event) {

            loginButton.disabled = true;
            loginButton.innerHTML = `
                <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                Cargando...
            `;

        });
    }
});