/* The sample packet page: a sheet opens in the 2000 px lightbox. */
(() => {
  const lightbox = document.getElementById('lightbox');
  const image = document.getElementById('lightbox-img');
  const close = () => { lightbox.hidden = true; image.classList.remove('zoomed'); };
  image.addEventListener('click', () => image.classList.toggle('zoomed'));
  document.getElementById('lightbox-close').addEventListener('click', close);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !lightbox.hidden) close(); });
  document.querySelectorAll('.sample-open').forEach((button) => button.addEventListener('click', () => {
    image.src = button.dataset.full;
    image.alt = button.dataset.alt;
    lightbox.hidden = false;
    document.getElementById('lightbox-close').focus();
  }));
})();
