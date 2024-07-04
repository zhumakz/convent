document.addEventListener("DOMContentLoaded", function () {
    const errorMessage = document.querySelector(".error-message");
    const errorMessagePopup = document.querySelector(".error-message-popup");

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
    }

    function hideError() {
        errorMessage.style.display = 'none';
    }

    function showErrorPopup(message) {
        errorMessagePopup.textContent = message;
        errorMessagePopup.style.display = 'flex';
    }

    function hideErrorPopup() {
        errorMessagePopup.style.display = 'none';
    }


    let phoneInput = document.getElementById('phoneNumber');
    let im = new Inputmask("+7 (999) 999-99-99");
    im.mask(phoneInput);
});