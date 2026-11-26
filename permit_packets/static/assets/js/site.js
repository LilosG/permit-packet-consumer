/* Loaded on every page: the header menus, the shared helpers (window.PP) and conversion tracking.
   Analytics only runs when the page loaded gtag (GA4_MEASUREMENT_ID is set); otherwise track() does nothing. */
(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

  /* ---- Landing page: the first page of the session, kept for every event. Order and admin pages hold a secret link, so they are never kept. ---- */
  const LANDING_KEY = 'pp_landing';
  const safely = (fn) => { try { return fn(); } catch { return null; } };
  if (!/^\/(order|admin)(\/|$)/.test(location.pathname)) {
    safely(() => { if (!sessionStorage.getItem(LANDING_KEY)) sessionStorage.setItem(LANDING_KEY, location.pathname); });
  }
  const landingPage = () => safely(() => sessionStorage.getItem(LANDING_KEY)) || '';

  /* ---- Who the visitor is, kept for the session, so a pro who browses on doesn't start the wizard as a homeowner. ---- */
  const ROLE_KEY = 'pp_role';
  const ROLES = ['diy', 'hiring', 'electrician', 'contractor'];
  const PRO_ROLES = ['electrician', 'contractor'];
  const ROLE_PAGES = {
    '/for/electricians/': 'electrician', '/for/contractors/': 'contractor',
    '/for/diy-homeowners/': 'diy', '/for/homeowners-hiring-an-electrician/': 'hiring',
  };
  const savedRole = () => {
    const role = safely(() => sessionStorage.getItem(ROLE_KEY));
    return ROLES.includes(role) ? role : '';
  };
  const saveRole = (role) => { if (ROLES.includes(role)) safely(() => sessionStorage.setItem(ROLE_KEY, role)); };
  /* An explicit ?role= wins over what the page implies. Pro Credits keeps a contractor a contractor. */
  const askedRole = safely(() => new URLSearchParams(location.search).get('role'));
  if (ROLES.includes(askedRole)) saveRole(askedRole);
  else if (ROLE_PAGES[location.pathname]) saveRole(ROLE_PAGES[location.pathname]);
  else if (location.pathname === '/pro-credits/' && savedRole() !== 'contractor') saveRole('electrician');

  /* For a pro, links and forms that go to /start/ without a role of their own carry the saved one. Done in the browser
     only: the HTML the server sends is unchanged. */
  function carryRole() {
    const role = savedRole();
    if (!PRO_ROLES.includes(role)) return;
    const startUrl = (value) => safely(() => {
      const url = new URL(value, location.href);
      return url.origin === location.origin && url.pathname === '/start/' ? url : null;
    });
    $$('a[href]').forEach((link) => {
      const url = startUrl(link.getAttribute('href'));
      if (!url || url.searchParams.has('role')) return;
      url.searchParams.set('role', role);
      link.setAttribute('href', url.pathname + url.search + url.hash);
    });
    $$('form[action]').forEach((form) => {
      const url = startUrl(form.getAttribute('action'));
      if (!url || url.searchParams.has('role') || form.querySelector('[name="role"]')) return;
      const input = document.createElement('input');
      input.type = 'hidden';
      input.name = 'role';
      input.value = role;
      form.append(input);
    });
  }
  carryRole();

  /* Sends a GA4 event with the landing page added. Returns true when it was handed to gtag. */
  function track(name, params = {}) {
    if (typeof window.gtag !== 'function') return false;
    window.gtag('event', name, { landing_page: landingPage(), ...params });
    return true;
  }
  /* For the calculators that come later: one place to report that one was used. */
  function calculatorUsed(params = {}) { return track('calculator_used', params); }

  async function api(path, body) {
    const response = await fetch(path, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    if (response.ok) return response;
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail) ? data.detail[0]?.msg?.replace(/^Value error, /, '') : data.detail;
    throw new Error(detail || `The request failed (${response.status}). Try again.`);
  }

  /* ---- Address suggestions as the visitor types. Typing the whole address still works. ---- */
  const SUGGEST_DELAY_MS = 220;
  function attachSuggest(input, list, onChoose, prefix) {
    let timer = null;
    let requestId = 0;
    let active = -1;
    const items = () => Array.from(list.querySelectorAll('li[role=option]'));
    function close() {
      list.hidden = true;
      list.innerHTML = '';
      active = -1;
      input.setAttribute('aria-expanded', 'false');
      input.removeAttribute('aria-activedescendant');
    }
    function mark() {
      items().forEach((item, index) => item.setAttribute('aria-selected', String(index === active)));
      if (active >= 0) input.setAttribute('aria-activedescendant', `${prefix}-${active}`);
      else input.removeAttribute('aria-activedescendant');
    }
    function choose(text) {
      requestId += 1;
      clearTimeout(timer);
      input.value = text;
      close();
      onChoose();
    }
    async function load(text, request) {
      const response = await api('/api/property/suggest', { text }).catch(() => null);
      const data = response ? await response.json().catch(() => null) : null;
      if (request !== requestId || document.activeElement !== input) return;
      const suggestions = data?.suggestions || [];
      if (!suggestions.length) { close(); return; }
      list.innerHTML = suggestions
        .map((item, index) => `<li role="option" id="${prefix}-${index}" aria-selected="false">${esc(item)}</li>`).join('')
        + '<li class="credit" role="presentation">Suggestions from OpenStreetMap contributors</li>';
      active = -1;
      list.hidden = false;
      input.setAttribute('aria-expanded', 'true');
    }
    input.addEventListener('input', () => {
      clearTimeout(timer);
      requestId += 1;
      const text = input.value.trim();
      if (text.length < 4) { close(); return; }
      const request = requestId;
      timer = setTimeout(() => load(text, request), SUGGEST_DELAY_MS);
    });
    input.addEventListener('keydown', (event) => {
      const options = items();
      if (event.key === 'Escape') { close(); return; }
      if (!options.length) return;
      if (event.key === 'ArrowDown' || event.key === 'ArrowUp') {
        event.preventDefault();
        active = (active + (event.key === 'ArrowDown' ? 1 : -1) + options.length) % options.length;
        mark();
      } else if (event.key === 'Enter' && active >= 0) {
        event.preventDefault();
        choose(options[active].textContent);
      }
    });
    /* mousedown fires before the input loses focus, so the list is still there. */
    list.addEventListener('mousedown', (event) => {
      const item = event.target.closest('li[role=option]');
      event.preventDefault();
      if (item) choose(item.textContent);
    });
    /* Pressing the form's own button must not close the list first: the button would move out from under the
       pointer before the click lands. The submit closes it, and so does focus leaving the form. */
    input.addEventListener('blur', (event) => { if (!(input.form && input.form.contains(event.relatedTarget))) close(); });
    if (input.form) input.form.addEventListener('focusout', (event) => { if (!input.form.contains(event.relatedTarget)) close(); });
    return { cancel() { requestId += 1; clearTimeout(timer); close(); } };
  }

  window.PP = { esc, api, attachSuggest, track, calculatorUsed, landingPage, savedRole, saveRole };

  /* ---- Header: the two dropdowns ---- */
  const dropdowns = $$('.dd');
  function closeDropdowns() {
    dropdowns.forEach((dropdown) => {
      dropdown.classList.remove('open');
      dropdown.querySelector('.dd-toggle').setAttribute('aria-expanded', 'false');
    });
  }
  const hoverable = window.matchMedia('(hover: hover)');
  dropdowns.forEach((dropdown) => {
    const toggle = dropdown.querySelector('.dd-toggle');
    let timer = 0;
    const setOpen = (open) => {
      dropdown.classList.toggle('open', open);
      toggle.setAttribute('aria-expanded', String(open));
    };
    const cancel = () => { clearTimeout(timer); timer = 0; };
    toggle.addEventListener('click', () => {
      const open = !dropdown.classList.contains('open');
      cancel();
      closeDropdowns();
      setOpen(open);
    });
    dropdown.addEventListener('mouseenter', () => {
      if (!hoverable.matches) return;
      cancel();
      closeDropdowns();
      setOpen(true);
    });
    dropdown.addEventListener('mouseleave', () => {
      if (!hoverable.matches) return;
      cancel();
      timer = setTimeout(() => setOpen(false), 150);
    });
    dropdown.addEventListener('focusin', () => {
      if (hoverable.matches && toggle.matches(':focus-visible')) { cancel(); setOpen(true); }
    });
    dropdown.addEventListener('focusout', (event) => {
      if (hoverable.matches && !dropdown.contains(event.relatedTarget)) setOpen(false);
    });
    dropdown.addEventListener('keydown', (event) => {
      if (event.key !== 'Escape') return;
      cancel();
      setOpen(false);
      toggle.focus();
    });
  });
  document.addEventListener('click', (event) => { if (!event.target.closest('.dd')) closeDropdowns(); });

  /* ---- Compact header menu (under 960px) ---- */
  const menuToggle = $('#menu-toggle');
  const mobileMenu = $('#mobile-menu');
  if (menuToggle && mobileMenu) {
    const closeMenu = () => {
      mobileMenu.hidden = true;
      menuToggle.setAttribute('aria-expanded', 'false');
    };
    menuToggle.addEventListener('click', () => {
      const open = mobileMenu.hidden;
      mobileMenu.hidden = !open;
      menuToggle.setAttribute('aria-expanded', String(open));
    });
    mobileMenu.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape' && !mobileMenu.hidden) { closeMenu(); menuToggle.focus(); }
    });
    matchMedia('(min-width: 1081px)').addEventListener('change', (query) => { if (query.matches) closeMenu(); });
  }
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape') closeDropdowns(); });

  /* ---- Launch pricing banner: dismissible, and the dismissal is remembered (storage can be blocked) ---- */
  const banner = $('#launch-banner');
  if (banner) {
    const KEY = 'pp-launch-banner-dismissed';
    let dismissed = false;
    try { dismissed = localStorage.getItem(KEY) === '1'; } catch (error) { /* storage blocked: show it every visit */ }
    if (dismissed) banner.hidden = true;
    const close = $('#launch-banner-close');
    if (close) close.addEventListener('click', () => {
      banner.hidden = true;
      try { localStorage.setItem(KEY, '1'); } catch (error) { /* not remembered */ }
    });
  }
})();
