/* The homepage: the quick-start card (it hands the job and address to /start/), the FAQ and the sample viewer. */
(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const { attachSuggest } = window.PP;

  /* ---- Quick start card: the pills choose the job, the form submits to /start/?job=&address= ---- */
  $$('.jt-pill').forEach((pill) => pill.addEventListener('click', () => {
    $$('.jt-pill').forEach((other) => other.setAttribute('aria-checked', String(other === pill)));
    $('#hero-job').value = pill.dataset.job;
  }));
  const heroForm = $('#hero-form');
  const heroSuggest = attachSuggest($('#hero-address'), $('#hero-suggestions'), () => heroForm.requestSubmit(), 'hero-suggestion');
  heroForm.addEventListener('submit', () => heroSuggest.cancel());

  /* ---- FAQ accordion: one open at a time, real buttons with aria-expanded; the height animates in CSS ---- */
  const faqItems = $$('.faq-item');
  faqItems.forEach((item) => item.querySelector('.faq-q').addEventListener('click', () => {
    const open = !item.classList.contains('is-open');
    faqItems.forEach((other) => {
      const isThis = other === item && open;
      other.classList.toggle('is-open', isThis);
      other.querySelector('.faq-q').setAttribute('aria-expanded', String(isThis));
    });
  }));

  /* ---- Sample packet viewer ---- */
  const lightbox = $('#lightbox');
  const closeLightbox = () => { lightbox.hidden = true; $('#lightbox-img').classList.remove('zoomed'); };
  $('#lightbox-img').addEventListener('click', (event) => event.currentTarget.classList.toggle('zoomed'));
  $('#lightbox-close').addEventListener('click', closeLightbox);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !lightbox.hidden) closeLightbox(); });

  const sampleTabs = $$('.doc-tab');
  function showSample(tab) {
    sampleTabs.forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
    const image = $('#sample-img');
    image.srcset = `/assets/samples/${tab.dataset.sample}-300.webp 300w, /assets/samples/${tab.dataset.sample}-1000.webp 1000w`;
    image.src = `/assets/samples/${tab.dataset.sample}-1000.webp`;
    image.dataset.full = `/assets/samples/${tab.dataset.sample}-2000.webp`;
    image.alt = `Sample packet sheet: ${tab.dataset.label}`;
    $('#zoom-text').textContent = ['02-site-plan', '03-single-line'].includes(tab.dataset.sample) ? 'Click diagram to zoom' : 'Click sheet to zoom';
  }
  sampleTabs.forEach((tab) => tab.addEventListener('click', () => showSample(tab)));
  $('.doc-tabs').addEventListener('keydown', (event) => {
    const index = sampleTabs.indexOf(document.activeElement);
    const step = { ArrowRight: 1, ArrowLeft: -1 }[event.key];
    if (index < 0 || !step) return;
    event.preventDefault();
    const next = sampleTabs[(index + step + sampleTabs.length) % sampleTabs.length];
    showSample(next);
    next.focus();
  });
  $('#sample-open').addEventListener('click', () => {
    const image = $('#lightbox-img');
    image.src = $('#sample-img').dataset.full || $('#sample-img').src.replace(/-1000\.webp$/, '-2000.webp');
    image.alt = $('#sample-img').alt;
    lightbox.hidden = false;
    $('#lightbox-close').focus();
  });
})();
