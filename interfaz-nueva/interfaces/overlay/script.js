// Abre y cierra el menú de pantalla completa (overlay)
const btnAbrir = document.getElementById('btnAbrir');
const btnCerrar = document.getElementById('btnCerrar');
const overlay = document.getElementById('overlay');

btnAbrir.addEventListener('click', function () {
  overlay.classList.add('activo');
});

btnCerrar.addEventListener('click', function () {
  overlay.classList.remove('activo');
});
