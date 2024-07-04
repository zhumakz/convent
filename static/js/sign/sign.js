const form = document.querySelector(".sign__form");
const number = form.number;
const code = form.code;
const popupForm = document.querySelector(".sign__popup-form");
const inputs = document.querySelectorAll(".sign__popup-item");
const buttonSend = document.querySelector(".sign__send-code");

popupClose[0].addEventListener("click", () => {
  clearInterval(interval);
});