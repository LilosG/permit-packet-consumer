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
      + `<h3>NEC sections applied</h3><ul class="check-list">${nec}</ul>${notes}`;
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
      history.replaceState(null, '', `${location.pathname}?${query}`);
      report();
      box.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
    } catch (error) {
      form.submit();  // no script help: fall back to the server-rendered page
    }
  });
  if (box.dataset.used === '1') report();
})();
