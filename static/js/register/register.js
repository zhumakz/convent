const btn = document.querySelector('.register__select');
const list = document.querySelector('.register__select-list');

btn.addEventListener('click', () => btn.classList.toggle('register__select--active'))

list.addEventListener('click', ({target}) => {
    if(target.classList.contains('register__list-button')) {
        btn.children[0].textContent = target.textContent;
        btn.children[0].style.opacity = 1
        btn.classList.remove('register__select--active')
    }
})