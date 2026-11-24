/* Load letter enhancement. The form works without this script (a plain GET renders the letter on the server).
   With it, the form calls /api/load-letter and swaps the letter in place. Everything is written with textContent. */
(() => {
  const form = document.getElementById('letter-form');
  const pre = document.getElementById('letter-preview');
  const errors = document.getElementById('letter-errors');
  const status = document.getElementById('letter-status');
  const copyButton = document.getElementById('letter-copy');
  const printButton = document.getElementById('letter-print');
  if (!form || !pre) return;

  const say = (message) => { if (status) status.textContent = message; };
  const showErrors = (messages) => {
    errors.textContent = '';
    if (!messages.length) return;
    const list = document.createElement('ul');
    list.className = 'check-list calc-error';
    messages.forEach((message) => { const item = document.createElement('li'); item.textContent = message; list.appendChild(item); });
    errors.appendChild(list);
  };

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    try {
      const response = await fetch(`/api/load-letter?${new URLSearchParams(new FormData(form))}`);
      const data = await response.json();
      if (!data.ok) { showErrors(data.errors || ['Check the form and try again.']); say(''); return; }
      showErrors([]);
      pre.textContent = data.letter;
      const heading = document.getElementById('letter-heading');
      if (heading) heading.textContent = 'Your letter';
      say('Letter updated.');
    } catch (error) {
      form.submit();  // no script help: fall back to the server-rendered page
    }
  });

  if (copyButton) {
    copyButton.hidden = false;
    copyButton.addEventListener('click', async () => {
      const text = pre.textContent;
      try {
        await navigator.clipboard.writeText(text);
        say('Copied to clipboard.');
      } catch (error) {
        const range = document.createRange();  // clipboard blocked: select the text so Ctrl/Cmd+C works
        range.selectNodeContents(pre);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
        say('Press Ctrl+C (Cmd+C on Mac) to copy.');
      }
    });
  }
  if (printButton) {
    printButton.hidden = false;
    printButton.addEventListener('click', () => window.print());
  }
})();
