// Abre y cierra la barra lateral al hacer clic en el ícono de menú
const btnMenu = document.getElementById('btnMenu');
const sidebar = document.getElementById('sidebar');

btnMenu.addEventListener('click', function () {
  sidebar.classList.toggle('abierto');
});
