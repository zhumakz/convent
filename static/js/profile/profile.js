const qr = document.querySelector(".profile__button");
const addQr = document.querySelector(".add__inner");

addQr.addEventListener("click", () => activePopup(3));

qr.addEventListener("click", () => {
  domReady(function () {

    function onScanSuccess(decodeText, decodeResult) {
      activePopup(2);
    }

    let htmlscanner = new Html5QrcodeScanner("my-qr-reader", {
      fps: 10,
      qrbos: 250,
    });
    htmlscanner.render(onScanSuccess);
  });
});



const timer = new Timer(document.querySelector('.timer'))


document.querySelector('.find-button').addEventListener('click',() => timer.timerStart())
document.querySelector('.find__button-close').addEventListener('click', () => timer.closeInterval())