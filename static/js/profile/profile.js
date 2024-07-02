


const timer = new Timer(document.querySelector('.timer'))


document.querySelector('.find-button').addEventListener('click',() => timer.timerStart())
document.querySelector('.find__button-close').addEventListener('click', () => timer.closeInterval())