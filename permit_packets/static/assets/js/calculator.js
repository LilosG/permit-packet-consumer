/* Calculator enhancement. The form works without this script (a plain GET renders the result on the server).
   With it, the form calls /api/calc/{slug}, swaps the result in place, keeps the URL in step with the inputs,
   offers a copy-link button, and reports calculator_used to GA4. */
(() => {
  const form = document.getElementById('calc-form');
  const box = document.getElementById('result');
  if (!form || !box) return;
  const slug = form.dataset.calc;
  const esc = (v) => (window.PP ? window.PP.esc(String(v)) : String(v).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])));
  let reported = false;
  const report = () => { if (!reported && window.PP) { reported = true; window.PP.calculatorUsed({ calculator: slug }); } };

  function render(r) {
    const rows = r.rows.map(([a, b]) => `<tr><th scope="row">${esc(a)}</th><td>${esc(b)}</td></tr>`).join('');
    const nec = r.nec_rows.map(([a, b]) => `<li><b>${esc(a)}</b>: ${esc(b)}</li>`).join('');
    const notes = r.notes.length ? `<ul class="check-list">${r.notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>` : '';
    const actions = `<div class="calc-result-actions"><a class="btn-primary" href="${esc(form.dataset.start || '/start/')}">Build the permit packet `
      + '<svg class="ic" aria-hidden="true"><use href="#i-arrow"/></svg></a>'
      + '<button type="button" class="copy calc-copy" data-copy-link>Copy link to calculation</button></div>';
    return `<h2>Your result</h2><p class="calc-headline calc-${esc(r.status)}">${esc(r.headline)}</p>`
      + `<div class="table-wrap"><table class="compare"><tbody>${rows}</tbody></table></div>`
      + `<h3>NEC sections applied</h3><ul class="check-list">${nec}</ul>${notes}${form.dataset.reportCta || ''}${actions}`;
  }

  /* Every /start/ link carries the job type and the current inputs, so the packet builder opens pre-filled. */
  function syncStartLinks() {
    document.querySelectorAll('a[href^="/start/"]').forEach((a) => {
      const u = new URL(a.getAttribute('href'), location.origin);
      new FormData(form).forEach((v, k) => {
        if (slug === 'subpanel-feeder-calculator' && k === 'breaker_amps') { u.searchParams.set('sp_breaker_amps', v); u.searchParams.set('sp_subpanel_amps', v); }
        else if (slug === 'hot-tub-breaker-wire-size' && k === 'load_amps') { u.searchParams.set('ac_nameplate_amps', v); }
        else { u.searchParams.set(k, v); }
      });
      a.setAttribute('href', u.pathname + u.search);
    });
  }

  async function run({ scroll = false, fallback = false } = {}) {
    const query = new URLSearchParams(new FormData(form)).toString();
    try {
      const response = await fetch(`/api/calc/${slug}?${query}`);
      const data = await response.json();
      if (!data.ok) {
        box.innerHTML = `<ul class="check-list calc-error">${data.errors.map((e) => `<li>${esc(e)}</li>`).join('')}</ul>`;
        return;
      }
      box.innerHTML = render(data.result);
      syncStartLinks();
      history.replaceState(null, '', `${location.pathname}?${query}`);
      report();
      if (scroll) box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (error) {
      if (fallback) form.submit();  // no script help: fall back to the server-rendered page
    }
  }

  form.addEventListener('submit', (event) => { event.preventDefault(); run({ scroll: true, fallback: true }); });

  /* A shared link (/tools/<slug>/?...) fills the form and runs the numbers on load. */
  const shared = new URLSearchParams(location.search);
  const prefill = [...new FormData(form).keys()].some((name) => shared.has(name));
  if (box.dataset.used === '1') report();
  if (prefill) run();

  function copyLink(button) {
    const done = () => {
      button.textContent = 'Link copied';
      window.setTimeout(() => { button.textContent = 'Copy link to calculation'; }, 2000);
    };
    const fallback = () => {
      const field = document.createElement('textarea');
      field.value = location.href;
      field.setAttribute('readonly', '');
      field.style.position = 'absolute';
      field.style.left = '-9999px';
      document.body.appendChild(field);
      field.select();
      try { document.execCommand('copy'); } catch (error) { /* clipboard unavailable */ }
      document.body.removeChild(field);
      done();
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(location.href).then(done, fallback);
    else fallback();
  }
  /* Clicks are delegated: the result card is replaced on every run. */
  box.addEventListener('click', (event) => {
    const copy = event.target.closest('[data-copy-link]');
    if (copy) copyLink(copy);
    if (event.target.closest('.calc-report-link') && window.PP) window.PP.track('calculator_cta_clicked', { tool: slug });
  });
})();
