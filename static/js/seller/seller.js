const form = document.querySelector(".seller__form");

class Form {
  constructor(form) {
    this.input = form.querySelector(".seller__number");

    form.addEventListener("click", ({ target }) => {
      if (target.classList.contains("seller__button")) {
        this.input.value += target.value;
      }else if(target.classList.contains("seller__delete") ) {
        console.log('1')
        this.input.value  = this.input.value.slice(0, this.input.value.length - 1)
      }
    });


    form.addEventListener('submit',(e)  => {
      e.preventDefault();

      activePopup(1)
    })
  }
}

new Form(form);


const qr = document.querySelector('.qr')
qr.addEventListener('click', () => activePopup(2))