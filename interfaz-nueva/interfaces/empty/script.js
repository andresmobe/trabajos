// Muestra u oculta el menú al hacer clic en el ícono
const btnMenu = document.getElementById('btnMenu');
const menu = document.getElementById('menuDesplegable');

btnMenu.addEventListener('click', function () {
  menu.classList.toggle('mostrar');
});
