// PRELOADER
const preloader = document.querySelector(".preloader");
const preloaderIcon = document.querySelector(".preloader__icon");
const progressLine = document.querySelector(".preloader__progress-line");

document.addEventListener("DOMContentLoaded", () => {
  if(navigator.appCodeName == "Mozilla") {
    preloader.classList.add("preloader--remove");
    document.body.classList.remove("body--overflow");
  }
  if (!preloader) return;

  const files = document.querySelectorAll("svg, video, img");

  preloaderIcon.classList.add("preloader__icon--active");

  let count = 0;
  if (!files.length) {
    preloader.classList.add("preloader--remove");
    document.body.classList.remove("body--overflow");
    return;
  }
  [...files].forEach((file, i) => {
   // console.log(file.complete);
    if (file.complete) {
      count++;
      progressLine.style.width = `${(count / files.length) * 100}%`;
    } else {
      file.addEventListener("load", () => {
        progressLine.style.width = `${(count / files.length) * 100}%`;

        if (i == files.length - 1) {
          preloader.classList.add("preloader--remove");
          document.body.classList.remove("body--overflow");
        }
        count++;
      });
    }
  });
});

// MENU

const menuButton = document.querySelector(".menu-button");
const menu = document.querySelector(".menu");

function toggleMenu() {
  menu.classList.toggle("menu--active");
}

if (menu) {
  document.body.addEventListener("click", ({ target }) => {
    if (target === menuButton) toggleMenu();
    else if (menu.classList.contains("menu--active") && target !== menu)
      menu.classList.remove("menu--active");
  });
}

// BACK-BUTTON

const backs = document.querySelectorAll(".back");

[...backs].forEach((back) =>
  back.addEventListener("click", () => window.history.back())
);

//POPUP

const popupClose = document.querySelectorAll(".popup-close");
const popupsClose = document.querySelectorAll(".popups-close");

const popups = document.querySelectorAll(".popup");
const popupButtons = document.querySelectorAll(".popup-button");
let obj;
if (popups.length >= 1) {
  obj = {};
  [...popups].forEach((popup) => {
    obj[popup.dataset.index] = popup;
  });
  [...popupButtons].forEach((button) =>
    button.addEventListener("click", () => {
      obj[button.dataset.index].classList.add("popup--active");
      document.body.classList.add("body--overflow");
    })
  );
  [...popupClose].forEach((close) => {
    close.addEventListener("click", () => {
      obj[close.dataset.index].classList.remove("popup--active");
      document.body.classList.remove("body--overflow");
    });
  });
} else if (popups[0]) {
  popupButtons[0] &&
    popupButtons[0].addEventListener("click", () => {
      popups[0].classList.add("popup--active");
      document.body.classList.add("body--overflow");
    });

  popupClose[0] &&
    popupClose[0].addEventListener("click", () => {
      popups[0].classList.remove("popup--active");
      document.body.classList.remove("body--overflow");
    });
}

function activePopup(index) {
  console.log(index);
  obj[index].classList.add("popup--active");
}

if (popupsClose.length) {
  [...popupsClose].forEach((close) => {
    close.addEventListener("click", () => {
      document.body.classList.remove("body--overflow");

      Object.keys(obj).forEach((popup) => {
        obj[popup].classList.remove("popup--active");
      });
    });
  });
}

let vh = window.innerHeight * 0.01;
document.documentElement.style.setProperty("--vh", `${vh}px`);

window.addEventListener("resize", () => {
  let vh = window.innerHeight * 0.01;
  document.documentElement.style.setProperty("--vh", `${vh}px`);
});

function domReady(fn) {
  if (
    document.readyState === "complete" ||
    document.readyState === "interactive"
  ) {
    setTimeout(fn, 1000);
  } else {
    document.addEventListener("DOMContentLoaded", fn);
  }
}

class Timer {
  constructor(tag) {
    this.tag = tag;
    this.timer = document.createElement("div");
    this.timer.classList.add("timer-minutes");
    this.timer.textContent = "2:00";
    this.timerLine = document.createElement("div");
    this.timerLine.classList.add("timer-line");
    this.timerProgressLine = document.createElement("div");
    this.timerProgressLine.classList.add("timer-progress-line");
    this.timerLine.append(this.timerProgressLine);
    this.interval = null;
    this.seconds = 120;
  }

  // Функия когда таймер начинает отсчет
  timerStart = () => {
    this.timerLine.style.display = "block";
    this.tag.append(this.timer);
    this.tag.append(this.timerLine);
    this.interval = setInterval(() => {
      this.seconds--;
      this.timerProgressLine.style.width = `${
        100 - (this.seconds / 120) * 100
      }%`;
      this.timer.textContent =
        this.seconds >= 60
          ? "1:" +
            (this.seconds % 60 > 9
              ? this.seconds % 60
              : "0" + (this.seconds % 60))
          : "0:" +
            (this.seconds % 60 > 9 ? this.seconds % 60 : "0" + this.seconds);

      if (!this.seconds) clearInterval(this.interval);
    }, 1000);
  };

  closeInterval = () => {
    if (this.interval) {
      clearInterval(this.interval);
      this.timer.textContent = "";
      this.seconds = 120;
      this.timerLine.style.display = "none";
    }
  };
}
