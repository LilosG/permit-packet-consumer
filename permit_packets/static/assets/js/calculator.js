/* Calculator enhancement. The form works without this script (a plain GET renders the result on the server).
   With it, the form calls /api/calc/{slug} and swaps the result in place, and reports calculator_used to GA4. */
(() => {
  const form = document.getElementById('calc-form');
  const box = document.getElementById('result');
  if (!form || !box) return;
  const slug = form.dataset.calc;
  const esc = (v) => (window.PP ? window.PP.esc(String(v)) : String(v).replace(/[&<>"]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c])));
  const report = () => { if (window.PP) window.PP.calculatorUsed({ calculator: slug }); };

  function render(r) {
    const rows = r.rows.map(([a, b]) => `<tr><th scope="row">${esc(a)}</th><td>${esc(b)}</td></tr>`).join('');
    const nec = r.nec_rows.map(([a, b]) => `<li><b>${esc(a)}</b>: ${esc(b)}</li>`).join('');
    const notes = r.notes.length ? `<ul class="check-list">${r.notes.map((n) => `<li>${esc(n)}</li>`).join('')}</ul>` : '';
    return `<h2>Your result</h2><p class="calc-headline calc-${esc(r.status)}">${esc(r.headline)}</p>`
      + `<div class="table-wrap"><table class="compare"><tbody>${rows}</tbody></table></div>`
      + `<h3>NEC sections applied</h3><ul class="check-list">${nec}</ul>${notes}${form.dataset.reportCta || ''}`;
  }

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    const query = new URLSearchParams(new FormData(form)).toString();
    try {
      const response = await fetch(`/api/calc/${slug}?${query}`);
      const data = await response.json();
      if (!data.ok) {
        box.innerHTML = `<ul class="check-list calc-error">${data.errors.map((e) => `<li>${esc(e)}</li>`).join('')}</ul>`;
        return;
      }
      box.innerHTML = render(data.result);
      document.querySelectorAll('a[href^="/start/"]').forEach((a)=>{const u=new URL(a.getAttribute('href'),location.origin);const s=form.dataset.calc;new FormData(form).forEach((v,k)=>{if(s==='subpanel-feeder-calculator'&&k==='breaker_amps'){u.searchParams.set('sp_breaker_amps',v);u.searchParams.set('sp_subpanel_amps',v);}else if(s==='hot-tub-breaker-wire-size'&&k==='load_amps'){u.searchParams.set('ac_nameplate_amps',v);}else{u.searchParams.set(k,v);}});a.setAttribute('href',u.pathname+u.search);});
    history.replaceState(null, '', `${location.pathname}?${query}`);
      report();
      box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (error) {
      form.submit();  // no script help: fall back to the server-rendered page
    }
  });
  if (box.dataset.used === '1') report();
  /* The Panel Capacity Report link under a result: report which tool sent the click. */
  box.addEventListener('click', (event) => {
    if (event.target.closest('.calc-report-link') && window.PP) window.PP.track('calculator_cta_clicked', { tool: slug });
  });
})();
