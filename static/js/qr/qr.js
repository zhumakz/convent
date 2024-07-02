document.addEventListener("DOMContentLoaded", function () {
    // function onScanSuccess(decodeText, decodeResult) {
    //   activePopup(2);
    // }

    let htmlscanner = new Html5QrcodeScanner("my-qr-reader", {
      fps: 10,
      qrbos: 250,
    });
    htmlscanner.render(onScanSuccess);
    function onScanSuccess(decodedText, decodedResult) {
        // Handle the scanned result here.
        // For example, send the decoded text to the server for processing.
        fetch("{% url 'handle_qr_data' %}", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
                'X-CSRFToken': '{{ csrf_token }}'
            },
            body: new URLSearchParams({
                'qr_data': decodedText
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.status === 'ok') {
                // Show success popup
                document.querySelector('[data-index="2"]').classList.add('popup--active');
            } else {
                // Handle error
                alert(data.message);
            }
        })
        .catch(error => console.error('Error:', error));
    }

    let html5QrCodeScanner = new Html5QrcodeScanner(
        "my-qr-reader", { fps: 10, qrbox: 250 });
    html5QrCodeScanner.render(onScanSuccess);
});

// const qr = document.querySelector(".profile__button");
// const addQr = document.querySelector(".add__inner");
//
// addQr.addEventListener("click", () => activePopup(3));
//
// qr.addEventListener("click", () => {
//   domReady(function () {
//
//     function onScanSuccess(decodeText, decodeResult) {
//       activePopup(2);
//     }
//
//     let htmlscanner = new Html5QrcodeScanner("my-qr-reader", {
//       fps: 10,
//       qrbos: 250,
//     });
//     htmlscanner.render(onScanSuccess);
//   });
// });
