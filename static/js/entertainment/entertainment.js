// const form = document.querySelector(".add__form");
//
// class Form {
//     constructor(form) {
//         this.count = form.querySelector(".add__coins");
//         this.plus = form.querySelector(".add__plus");
//         this.minus = form.querySelector(".add__minus");
//         this.plusTop = form.querySelectorAll(".add__plus-top");
//
//         [...this.plusTop].forEach((button) =>
//             button.addEventListener("click", () => {
//                 this.count.value = button.dataset.plus;
//             })
//         );
//
//         this.plus.addEventListener("click", () => this.count.value++);
//         this.minus.addEventListener("click", () => this.count.value--);
//
//         form.addEventListener("submit", (e) => {
//             e.preventDefault();
//
//             //activePopup(3);
//         });
//     }
// }
//
//
// new Form(form);
