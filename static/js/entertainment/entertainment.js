const qr = document.querySelector(".entertainment__button");

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

