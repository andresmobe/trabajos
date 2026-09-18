// El header pasa de transparente a fondo blanco cuando se hace scroll
const header = document.querySelector('header');

window.addEventListener('scroll', function () {
  if (window.scrollY > 80) {
    header.classList.add('fondo-solido');
  } else {
    header.classList.remove('fondo-solido');
  }
});
