document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('[data-toggle]').forEach((btn) => {
    btn.addEventListener('click', () => {
      const target = document.querySelector(btn.getAttribute('data-toggle'));
      if (target) target.classList.toggle('open');
      btn.classList.toggle('active');
    });
  });
});
