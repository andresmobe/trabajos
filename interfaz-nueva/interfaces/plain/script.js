// Resalta el link del menú en el que el usuario hace clic
document.querySelectorAll('nav a').forEach(function (link) {
  link.addEventListener('click', function (e) {
    e.preventDefault();
    document.querySelectorAll('nav a').forEach(function (l) {
      l.classList.remove('activo');
    });
    this.classList.add('activo');
  });
});
