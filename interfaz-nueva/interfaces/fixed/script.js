// Le agrega una sombra al header fijo cuando el usuario hace scroll hacia abajo
const header = document.querySelector('header');

window.addEventListener('scroll', function () {
  if (window.scrollY > 10) {
    header.classList.add('con-sombra');
  } else {
    header.classList.remove('con-sombra');
  }
});
