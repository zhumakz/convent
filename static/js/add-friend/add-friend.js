const form = document.querySelector(".add-friend__form");

class Form {
  constructor(form) {
    this.count = form.querySelector(".add-friend__coins");
    this.plus = form.querySelector(".add-friend__plus");
    this.minus = form.querySelector(".add-friend__minus");
    this.plusTop = form.querySelectorAll(".add-friend__plus-top");

    [...this.plusTop].forEach((button) =>
      button.addEventListener("click", () => {
        this.count.value = +this.count.value + +button.dataset.plus;
      })
    );

    this.plus.addEventListener("click", () => this.count.value++);
    this.minus.addEventListener("click", () => this.count.value--);

    form.addEventListener("submit", (e) => {
      e.preventDefault();

      activePopup(3);
    });
  }
}

new Form(form);
