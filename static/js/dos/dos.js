const timer = new Timer(document.querySelector(".timer"));
const title = document.querySelector('.dos__title')
const button = document.querySelector(".dos__button-start");
const buttonStop = document.querySelector(".dos__button-stop");
button.addEventListener("click", () => {
  button.style.display = 'none'
  title.style.display = 'none'
  timer.timerStart();
});

buttonStop.addEventListener('click', () => {
  button.style.display = 'block'
  title.style.display = 'block'
  timer.closeInterval();
})


document.querySelector('.qr').addEventListener('click',() => activePopup(2))