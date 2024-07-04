const form = document.querySelector(".sign__form");
const number = form.number;
const code = form.code;
const popupForm = document.querySelector(".sign__popup-form");
const inputs = document.querySelectorAll(".sign__popup-item");
const buttonSend = document.querySelector(".sign__send-code");



form.addEventListener("submit", (e) => {
  e.preventDefault();
  popups[0].classList.add("popup--active");
  document.body.classList.add("body--overflow");

  second();
});

const text = buttonSend.textContent.slice(0, buttonSend.textContent.length - 2);
let interval;

popupClose[0].addEventListener("click", () => {
  clearInterval(interval);
});
function second() {
  let time = 59;

  interval = setInterval(() => {
    buttonSend.textContent = text + (time > 9 ? time : "0" + time);

    if (time <= 0) {
      buttonSend.disabled = false;
      clearInterval(interval);
    }
    time--;
  }, 1000);
}

buttonSend.addEventListener("click", () => {
  time = 59;
  second();
});

// let activeIndex = 0;
//
// popupForm.addEventListener("input", ({ target }) => {
//   if (target.value.match(/[^0-9]/g)) {
//     target.value = target.value.slice(0, target.value.length - 1);
//     return;
//   }
//   if (!target.value.length && activeIndex) {
//     activeIndex--;
//     popupForm[activeIndex].focus();
//     return;
//   }
//   let tmp = "";
//   if (target !== popupForm[activeIndex]) {
//     popupForm[activeIndex].value = target.value;
//     activeIndex++;
//     target.value = "";
//     popupForm[activeIndex].focus();
//   } else if (target.value.length == 2 && activeIndex !== 3) {
//     tmp = target.value.slice(1, 2);
//     target.value = target.value.slice(0, 1);
//     activeIndex++;
//
//     popupForm[activeIndex].value = tmp;
//     popupForm[activeIndex].focus();
//   } else if (activeIndex == 3 && target.value.length == 2) {
//     target.value = target.value[1];
//   }
//
//   if (activeIndex === 3 && target.value.length) {
//     const code = target.value;
//     // Тут надо писать запрос формы на проверку кода
//     // и если код совбадет  перенаправить на страницу другую
//     window.location.pathname = "/selfie.html";
//   }
// });
