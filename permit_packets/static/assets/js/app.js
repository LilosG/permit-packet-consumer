/* The core flow: job type, property, details, review, submit. Job types plug in through
   window.PermitJobTypes (see job-types/). Everything type-specific comes from /api/job-types
   and from each packet response, so this file knows nothing about any one permit. */
(() => {
  const $ = (selector) => document.querySelector(selector);
  const $$ = (selector) => [...document.querySelectorAll(selector)];
  const esc = (value) => String(value ?? '')
    .replaceAll('&', '&amp;').replaceAll('<', '&lt;').replaceAll('>', '&gt;')
    .replaceAll('"', '&quot;').replaceAll("'", '&#039;');

  const TICK_MS = matchMedia('(prefers-reduced-motion: reduce)').matches ? 0 : 320;
  /* The address used by "Try with a sample address". */
  // The sample job: the same El Cajon address the sample sheets on the homepage were generated from (tools/make_sample.py).
  const SAMPLE = { address: '453 Brockton St, El Cajon, CA 92020', jurisdiction_key: 'el-cajon-ca', label: 'El Cajon, CA', owner: 'Sample Homeowner', location: 'detached_garage' };
  const TYPE_COPY = {
    ev_charger: ['EV Charger', 'A Level 2 home charger circuit'],
    service_upgrade: ['200A Service Upgrade', 'A new or larger main panel and service'],
    subpanel: ['Subpanel', 'A feeder and a new subpanel'],
    appliance_circuit: ['Hot Tub / 240V Circuit', 'Spa, sauna, heat pump or mini-split'],
  };
  const ICON_ATTRS = 'viewBox="0 0 28 28" width="28" height="28" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"';
  const ICONS = {
    ev: `<svg ${ICON_ATTRS}><rect x="4" y="3" width="12" height="22" rx="2"/><path d="M11 8l-3 5h4l-3 5"/><path d="M16 13h4a3 3 0 0 1 3 3v5"/><rect x="20" y="21" width="6" height="4" rx="1"/></svg>`,
    panel: `<svg ${ICON_ATTRS}><rect x="5" y="3" width="18" height="22" rx="2"/><path d="M9 8h4M15 8h4M9 13h4M15 13h4M9 18h4M15 18h4"/></svg>`,
    subpanel: `<svg ${ICON_ATTRS}><rect x="3" y="3" width="13" height="16" rx="2"/><path d="M6 8h2M11 8h2M6 12h2M11 12h2"/><path d="M16 14h3v4"/><rect x="17" y="18" width="8" height="8" rx="1.5"/></svg>`,
    circuit: `<svg ${ICON_ATTRS}><path d="M10 3v6M18 3v6"/><path d="M7 9h14v4a7 7 0 0 1-14 0z"/><path d="M14 20v3a3 3 0 0 0 3 3h5"/></svg>`,
  };
  const FALLBACK_ICON = `<svg ${ICON_ATTRS}><rect x="5" y="5" width="18" height="18" rx="2"/></svg>`;

  const form = $('#job');
  let jobTypes = [];
  let current = null;
  let property = null;
  let aerial = null;
  let aerialCredit = null;
  let marks = { points: {}, bends: [] };
  let tool = null;
  let picking = false;
  let packetUrl = null;
  let lastJob = null;
  let lastResult = null;
  let lastType = null;
  let lastWasSample = false;

  const emptyMarks = () => ({ points: {}, bends: [] });
  const modules = () => window.PermitJobTypes.modules;
  const typeModule = () => (current && modules()[current.key]) || {};
  const hasMarks = () => marks.bends.length > 0 || Object.keys(marks.points).length > 0;

  /* ---- Focus mode: the studio hides the page sections; "Exit studio" brings them back ---- */
  const PAGE_SECTIONS = '.metrics, #sample, #included, #compare, #pricing, #how, #faq';
  function enterStudio() {
    $$(PAGE_SECTIONS).forEach((el) => { el.hidden = true; });
    document.body.classList.add('studio-mode');
    $('#exit-studio').hidden = false;
    closeMenu();
  }
  function exitStudio() {
    $$(PAGE_SECTIONS).forEach((el) => { el.hidden = false; });
    document.body.classList.remove('studio-mode');
    $('#exit-studio').hidden = true;
  }
  $('#exit-studio').addEventListener('click', (event) => {
    event.preventDefault();
    exitStudio();
    window.scrollTo({ top: 0, behavior: TICK_MS ? 'smooth' : 'auto' });
  });

  /* ---- Compact header menu (under 960px) ---- */
  const menuToggle = $('#menu-toggle');
  const mobileMenu = $('#mobile-menu');
  function closeMenu() {
    mobileMenu.hidden = true;
    menuToggle.setAttribute('aria-expanded', 'false');
  }
  menuToggle.addEventListener('click', () => {
    const open = mobileMenu.hidden;
    mobileMenu.hidden = !open;
    menuToggle.setAttribute('aria-expanded', String(open));
  });
  mobileMenu.addEventListener('click', (event) => { if (event.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !mobileMenu.hidden) { closeMenu(); menuToggle.focus(); } });
  matchMedia('(min-width: 961px)').addEventListener('change', (query) => { if (query.matches) closeMenu(); });

  /* ---- Steps ---- */
  function show(step, scroll = true) {
    $$('[data-panel]').forEach((panel) => { panel.hidden = panel.dataset.panel !== String(step); });
    const now = step === 'building' ? 3 : step;
    $$('ol.steps li').forEach((item) => {
      const number = Number(item.dataset.step);
      item.classList.toggle('done', number < now);
      item.classList.toggle('now', number === now);
    });
    if (scroll) $('#steps').scrollIntoView({ behavior: TICK_MS ? 'smooth' : 'auto', block: 'start' });
  }

  async function api(path, body) {
    const response = await fetch(path, {
      method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body),
    });
    if (response.ok) return response;
    const data = await response.json().catch(() => ({}));
    const detail = Array.isArray(data.detail) ? data.detail[0]?.msg?.replace(/^Value error, /, '') : data.detail;
    throw new Error(detail || `The request failed (${response.status}). Try again.`);
  }

  /* ---- The selected job type ---- */
  function markerKeys() { return current.markers.map((marker) => marker.key); }
  function firstTool() { return current.markers[0]?.key ?? 'bend'; }

  function renderTools() {
    const bend = '<button type="button" class="tool" data-tool="bend"><span class="dot" style="background:#566572">+</span>Add a bend in the route<span class="state" id="state-bend"></span></button>';
    $('#tools').innerHTML = current.markers.map((marker) =>
      `<button type="button" class="tool" data-tool="${esc(marker.key)}"><span class="dot" style="background:${esc(marker.color)}">${esc(marker.letter)}</span>${esc(marker.prompt)}<span class="state" id="state-${esc(marker.key)}"></span></button>`).join('') + bend;
    const names = current.markers.map((marker) => `the ${marker.key}`).join(', ');
    $('#overlay').setAttribute('aria-label', `Plan of the property. Tap to place ${names} and any bends.`);
    $('#tb-route-block').hidden = !current.route_between;
  }

  /* Shows the form sections that belong to this type, and keeps hidden fields out of the payload. */
  function applyType() {
    $$('[data-job-type]').forEach((element) => { element.hidden = element.dataset.jobType !== current.key; });
    $$('[data-uses]').forEach((element) => { element.hidden = !current[`uses_${element.dataset.uses}`]; });
    $$('[data-hide-for]').forEach((element) => { element.hidden = element.dataset.hideFor === current.key; });
    [...form.elements].forEach((field) => { field.disabled = Boolean(field.closest('[data-job-type][hidden], [data-uses][hidden], [data-hide-for][hidden]')); });
    renderTools();
    tool = firstTool();
    if (property) drawPlan();
  }

  function chooseType(key) {
    const next = jobTypes.find((type) => type.key === key);
    if (!next) return;
    const changed = current && current.key !== next.key;
    current = next;
    applyType();
    if (changed && hasMarks()) {
      marks = emptyMarks();
      tool = firstTool();
      if (property) drawPlan();
    }
    $$('.jt-pill').forEach((pill) => pill.setAttribute('aria-checked', String(pill.dataset.type === key)));
    $$('.type-card').forEach((card) => {
      const selected = card.dataset.type === key;
      card.setAttribute('aria-checked', String(selected));
      card.tabIndex = selected ? 0 : -1;
    });
  }

  function renderTypeCards() {
    $('#type-list').innerHTML = jobTypes.map((type, index) =>
      {
      const [title, blurb] = TYPE_COPY[type.key] || [type.label, type.blurb];
      return `<button type="button" class="type-card" role="radio" aria-checked="false" tabindex="${index === 0 ? 0 : -1}" data-type="${esc(type.key)}">${ICONS[type.icon] || FALLBACK_ICON}<span class="type-title">${esc(title)}</span><span class="type-blurb">${esc(blurb)}</span></button>`;
    }).join('');
  }
  $('#type-list').addEventListener('click', (event) => {
    const card = event.target.closest('.type-card');
    if (card) chooseType(card.dataset.type);
  });
  $('#type-list').addEventListener('keydown', (event) => {
    const cards = $$('.type-card');
    const index = cards.indexOf(document.activeElement);
    if (index < 0) return;
    const step = { ArrowRight: 1, ArrowDown: 1, ArrowLeft: -1, ArrowUp: -1 }[event.key];
    if (!step) return;
    event.preventDefault();
    const next = cards[(index + step + cards.length) % cards.length];
    chooseType(next.dataset.type);
    next.focus();
  });

  /* ---- The plan: outlines, lot line and the marked route, in 0-1000 plan units ---- */
  function poly(points, attrs) {
    return `<polygon points="${points.map((p) => p.join(',')).join(' ')}" ${attrs}/>`;
  }
  function routePoints() {
    const between = current.route_between;
    if (!between) return [];
    const [start, end] = between.map((key) => marks.points[key]);
    return start && end ? [start, ...marks.bends, end] : [];
  }
  function measuredFt() {
    const points = routePoints();
    if (!property || !points.length) return null;
    let units = 0;
    for (let i = 1; i < points.length; i += 1) units += Math.hypot(points[i][0] - points[i - 1][0], points[i][1] - points[i - 1][1]);
    return Math.round(units * property.view.feet_per_unit);
  }
  function marker(point, fill, text) {
    return `<g transform="translate(${point[0]} ${point[1]})"><circle r="19" fill="${fill}" stroke="#fff" stroke-width="4"/><text text-anchor="middle" dy="7" font-size="20" font-weight="700" fill="#fff" font-family="IBM Plex Sans, sans-serif">${esc(text)}</text></g>`;
  }
  function drawPlan() {
    /* The photo shows the buildings, and outline data can sit a few feet off. */
    let svg = aerial ? '' : property.buildings.map((building, index) =>
      poly(building, `fill="${index === property.primary_building ? 'rgba(255,255,255,.14)' : 'none'}" stroke="#15212c" stroke-width="${index === property.primary_building ? 4 : 2}"`)).join('');
    if (property.lot.length) {
      svg += poly(property.lot, 'fill="none" stroke="#15212c" stroke-width="7"');
      svg += poly(property.lot, 'fill="none" stroke="#ffd84d" stroke-width="3.5" stroke-dasharray="16 9"');
    }
    const route = routePoints();
    if (route.length) {
      const line = route.map((p) => p.join(',')).join(' ');
      svg += `<polyline points="${line}" fill="none" stroke="#fff" stroke-width="11" stroke-linejoin="round" stroke-linecap="round"/>`;
      svg += `<polyline points="${line}" fill="none" stroke="#c8682a" stroke-width="6" stroke-linejoin="round" stroke-linecap="round"/>`;
    }
    marks.bends.forEach((point) => { svg += `<circle cx="${point[0]}" cy="${point[1]}" r="9" fill="#fff" stroke="#c8682a" stroke-width="5"/>`; });
    current.markers.forEach((spot) => {
      if (marks.points[spot.key]) svg += marker(marks.points[spot.key], spot.color, spot.letter);
    });
    $('#overlay').innerHTML = svg;

    $$('.tool').forEach((button) => button.setAttribute('aria-pressed', String(button.dataset.tool === tool)));
    current.markers.forEach((spot) => { $(`#state-${spot.key}`).textContent = marks.points[spot.key] ? 'Placed' : ''; });
    $('#state-bend').textContent = marks.bends.length ? String(marks.bends.length) : '';
    const feet = measuredFt();
    $('#tb-route').textContent = feet === null ? 'Not marked yet' : `${feet} ft`;
    $('#to-job').disabled = !current.markers.every((spot) => marks.points[spot.key]);
  }

  /* After a marker, the next unplaced one in order, then bends. */
  function nextTool(key) {
    const keys = markerKeys();
    const later = keys.slice(keys.indexOf(key) + 1).find((other) => !marks.points[other]);
    return later || 'bend';
  }

  $('#overlay').addEventListener('click', (event) => {
    const box = event.currentTarget.getBoundingClientRect();
    const point = [
      Math.round((event.clientX - box.left) / box.width * 1000),
      Math.round((event.clientY - box.top) / box.height * 1000),
    ];
    if (picking) { setPicking(false); changeView({ tap: point }); return; }
    if (tool === 'bend') marks.bends.push(point);
    else { marks.points[tool] = point; tool = nextTool(tool); }
    drawPlan();
  });
  $('#tools').addEventListener('click', (event) => {
    const button = event.target.closest('.tool');
    if (!button) return;
    tool = button.dataset.tool;
    drawPlan();
  });
  /* Undo takes back the last bend, then the markers, newest first. */
  $('#undo').addEventListener('click', () => {
    if (marks.bends.length) marks.bends.pop();
    else {
      const last = [...current.markers].reverse().find((spot) => marks.points[spot.key]);
      if (last) { delete marks.points[last.key]; tool = last.key; }
    }
    drawPlan();
  });
  $('#clear').addEventListener('click', () => { marks = emptyMarks(); tool = firstTool(); drawPlan(); });

  async function loadAerial(found) {
    const status = $('#aerial-status');
    status.hidden = false;
    status.textContent = 'Loading the aerial photo, about 15 seconds. You can start marking now.';
    try {
      const response = await api('/api/property/aerial', {
        latitude: found.view.latitude, longitude: found.view.longitude, scale_ft_per_in: found.view.scale_ft_per_in,
      });
      const data = await response.json();
      if (property !== found) return;
      aerial = data.image;
      aerialCredit = data.credit;
      $('#aerial').src = `data:image/jpeg;base64,${aerial}`;
      $('#aerial').hidden = false;
      status.hidden = true;
      drawPlan();
    } catch (error) {
      if (property === found) status.textContent = 'No aerial right now. The plan still works from the outlines.';
    }
  }

  /* ---- Address suggestions as the tech types. Typing the whole address still works. ---- */
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
  const addressInput = $('#address');
  const suggestionList = $('#suggestions');
  const workspaceSuggest = attachSuggest(addressInput, suggestionList, () => $('#find').requestSubmit(), 'suggestion');

  /* ---- The property ---- */
  function locatedNote(found) {
    if (found.address_confirmed === true) return ['good', 'Matched to the county record'];
    if (found.address_confirmed === false) return ['check', `County lists this parcel as number ${found.parcel_house_number}. Check the house.`];
    if (found.located_by === 'map') return ['good', 'Matched to the house on the map'];
    if (found.located_by === 'tap') return ['good', 'House chosen by you'];
    return ['check', 'Estimated from the street. Check this is the right house.'];
  }

  /* Plain text for a city with no checklist of its own. */
  function localName(found) {
    const name = found.city || found.jurisdiction.name;
    return name && name !== 'This area' ? name : 'your city';
  }
  function nationalChecklistNote(found) {
    return `Using the national NEC checklist. Confirm local amendments with ${localName(found)}.`;
  }

  function showProperty(found) {
    property = found;
    aerial = null;
    aerialCredit = null;
    marks = emptyMarks();
    tool = firstTool();
    typeModule().onProperty?.();
    $('#aerial').hidden = true;
    $('#tb-address').textContent = found.address;
    $('#tb-parcel').textContent = found.parcel_number ? `Parcel ${found.parcel_number}` : 'Parcel lines not set up for this county';
    const [tone, note] = locatedNote(found);
    $('#tb-located').className = `located ${tone}`;
    $('#tb-located').textContent = note;
    $('#tb-city').textContent = found.jurisdiction.label;
    const link = $('#tb-checklist');
    const checklistNote = $('#tb-checklist-note');
    const loaded = `${found.jurisdiction.checklist.length}-item checklist loaded`;
    if (found.jurisdiction.known && found.jurisdiction.source_url) {
      link.textContent = loaded;
      link.href = found.jurisdiction.source_url;
      link.hidden = false;
      checklistNote.textContent = '';
    } else {
      link.hidden = true;
      link.removeAttribute('href');
      checklistNote.textContent = found.jurisdiction.known ? loaded : nationalChecklistNote(found);
    }
    $('#tb-scale').textContent = `Plan scale: 1 in = ${found.view.scale_ft_per_in} ft`;
    $('#site').hidden = false;
    enterStudio();
    drawPlan();
    loadAerial(found);
  }

  async function changeView(change) {
    const found = property;
    const status = $('#aerial-status');
    status.hidden = false;
    status.textContent = 'Updating the plan';
    try {
      const response = await api('/api/property/view', {
        address: found.address, city: found.city, state: found.state, county_fips: found.county_fips,
        house_number: found.house_number, located_by: found.located_by,
        latitude: found.view.latitude, longitude: found.view.longitude,
        anchor_latitude: found.anchor.latitude, anchor_longitude: found.anchor.longitude,
        scale_ft_per_in: found.view.scale_ft_per_in, job_type: current.key, ...change,
      });
      showProperty(await response.json());
    } catch (error) {
      status.textContent = error.message;
    }
  }

  function setPicking(on) {
    picking = on;
    $('#pick-note').hidden = !on;
  }
  $('#wrong-house').addEventListener('click', () => setPicking(!picking));
  $('#zoom-out').addEventListener('click', () => changeView({ zoom: 1 }));
  $('#zoom-in').addEventListener('click', () => changeView({ zoom: -1 }));

  $('#find').addEventListener('submit', async (event) => {
    event.preventDefault();
    setPicking(false);
    workspaceSuggest.cancel();
    const button = $('#find-button');
    $('#find-error').hidden = true;
    button.disabled = true;
    button.textContent = 'Finding';
    try {
      await ready;
      if (!current) throw new Error('Something went wrong loading job types. Please refresh.');
      const response = await api('/api/property', { address: $('#address').value, job_type: current.key });
      const found = await response.json();
      showProperty(found);
      $('#site').scrollIntoView({ behavior: TICK_MS ? 'smooth' : 'auto', block: 'start' });
    } catch (error) {
      property = null;
      $('#site').hidden = true;
      $('#find-error').textContent = error.message;
      $('#find-error').hidden = false;
    } finally {
      button.disabled = false;
      button.textContent = 'Find property';
    }
  });

  /* What a job type's script can ask of the page. */
  const context = { form, $, $$, measuredFt };

  $('#to-job').addEventListener('click', () => {
    typeModule().onDetails?.();
    $('#job-lead').textContent = property.jurisdiction.known
      ? `${property.address}, using the ${property.jurisdiction.label} checklist.`
      : `${property.address}. ${nationalChecklistNote(property)}`;
    show(2);
  });
  // The sample runs the real lookup on the sample address, so it shows the same plan as the homepage sample sheets.
  $('#use-sample').addEventListener('click', async () => {
    await ready;
    if (!current) return;
    $('#address').value = SAMPLE.address;
    form.elements.customer.value = SAMPLE.owner;
    const garage = form.querySelector(`input[name=location][value=${SAMPLE.location}]`);
    if (garage) { garage.checked = true; garage.dispatchEvent(new Event('change', { bubbles: true })); }
    show(1, false);
    $('#find').requestSubmit();
  });
  $('#back-property').addEventListener('click', () => show(1));
  $$('#appliances input[data-load]').forEach((box) => box.addEventListener('change', () => {
    form.elements[box.dataset.load].value = box.checked ? box.dataset.va : 0;
  }));

  /* ---- Who is doing the work ---- */
  const OWNER = { contractor: 'Homeowner (Owner-Builder)', license: 'Owner-Builder' };
  const MAX_LOGO_BYTES = 500 * 1024;
  let contractorLogo = null;

  function applyRole() {
    const owner = form.elements.role.value === 'owner';
    $('#contractor-grid').hidden = owner;
    const { contractor, license_number: license } = form.elements;
    if (owner) {
      contractor.value = OWNER.contractor;
      license.value = OWNER.license;
      contractorLogo = null;
      $('#logo-file').value = '';
      $('#logo-note').textContent = '';
    } else {
      if (contractor.value === OWNER.contractor) contractor.value = '';
      if (license.value === OWNER.license) license.value = '';
    }
  }
  $$('input[name="role"]').forEach((radio) => radio.addEventListener('change', applyRole));

  $('#logo-file').addEventListener('change', (event) => {
    const file = event.target.files[0];
    contractorLogo = null;
    $('#logo-note').textContent = '';
    if (!file) return;
    if (!['image/png', 'image/jpeg'].includes(file.type) || file.size > MAX_LOGO_BYTES) {
      event.target.value = '';
      $('#logo-note').textContent = 'Please choose a PNG or JPEG under 500 KB.';
      return;
    }
    const reader = new FileReader();
    reader.onload = () => { contractorLogo = String(reader.result).split(',')[1]; $('#logo-note').textContent = `${file.name} added.`; };
    reader.readAsDataURL(file);
  });

  document.addEventListener('click', (event) => {
    const pill = event.target.closest('[data-fill]');
    if (pill) { form.elements[pill.dataset.fill].value = pill.dataset.value; return; }
    /* A pricing card preselects its own tier. Every other start button goes back to the $89 default. */
    const start = event.target.closest('[data-start]');
    if (start) {
      const radio = document.querySelector(`input[name="tier"][value="${start.dataset.plan || 'instant_packet'}"]`);
      if (radio) radio.checked = true;
    }
  });

  /* ---- The job ---- */
  // "Kitchen counter, 20, 1" per line. Lines that don't parse are skipped.
  function parseCircuits(text) {
    return text.split('\n').map((line) => line.split(',').map((part) => part.trim())).flatMap(([label, amps, poles]) => {
      const breaker = parseInt(amps, 10);
      if (!label || !(breaker >= 15 && breaker <= 200)) return [];
      return [{ label: label.slice(0, 60), amps: breaker, poles: poles === '2' ? 2 : 1 }];
    }).slice(0, 60);
  }

  function jobData() {
    const data = new FormData(form);
    const job = {
      customer: data.get('customer'), contractor: data.get('contractor'), license_number: data.get('license_number'),
      sample_mode: data.has('sample_mode'),
      ...typeModule().jobFields(data),
    };
    if (contractorLogo) job.contractor_logo_base64 = contractorLogo;
    job.existing_circuits = parseCircuits(data.get('existing_circuits') || '');
    if (data.get('sheet_size')) job.sheet_size = data.get('sheet_size');
    if (current.uses_home_loads) {
      job.home = {};
      $$('[data-home]').forEach((input) => { job.home[input.name] = Number(input.value); });
    }
    if (!property) return { ...job, address: SAMPLE.address, jurisdiction_key: SAMPLE.jurisdiction_key };
    const planFields = typeModule().planFields
      ? typeModule().planFields(marks)
      : { markers: marks.points, route: marks.bends };
    return {
      ...job, address: property.address, city: property.city, state: property.state,
      jurisdiction_key: property.jurisdiction.key,
      plan: {
        scale_ft_per_in: property.view.scale_ft_per_in, ...planFields,
        buildings: property.buildings, primary_building: property.primary_building, lot: property.lot,
        parcel_number: property.parcel_number, aerial_base64: aerial,
        credits: [...property.credits.filter((credit) => !aerial || !credit.startsWith('Building')), ...(aerialCredit ? [aerialCredit] : [])],
      },
    };
  }

  const wait = (ms) => new Promise((resolve) => { setTimeout(resolve, ms); });

  async function tickResults(result) {
    $('#build-list').innerHTML = result.build_steps.map((line) => `<li>${esc(line)}</li>`).join('');
    for (const item of $$('#build-list li')) {
      await wait(TICK_MS);
      item.classList.add('done');
    }
    await wait(TICK_MS);
  }

  /* ---- Step 3: the free preview ---- */
  function renderPreview(result) {
    const flags = result.flags || [];
    const card = $('#status');
    card.classList.toggle('warn', !result.ready);
    $('#status-icon').textContent = result.ready ? '✓' : '!';
    $('#status-title').textContent = result.ready ? 'Engineering & NEC 220 check: passed' : 'Almost there: a few items need attention';
    $('#status-note').textContent = result.ready
      ? (flags.length ? 'Every calculation passes. A few items are worth a second look below.' : 'Every calculation passes.')
      : 'See the items marked Fix below. You can add the missing details and preview again, or order as is.';
    $('#stats').innerHTML = result.summary.map((stat) => `<div><dt>${esc(stat.label)}</dt><dd>${esc(stat.value)}</dd></div>`).join('');
    $('#checks').innerHTML = result.checks
      .map((check) => {
        const [tone, label] = check.passed ? ['pass', 'Pass'] : check.neutral ? ['info', 'Note'] : ['fix', 'Fix'];
        return `<li><span class="${tone}">${label}</span> ${esc(check.name)}: ${esc(check.result)}</li>`;
      }).join('');
    $('#flags-wrap').hidden = !flags.length;
    $('#flags').innerHTML = flags.map((flag) => `<li>${esc(flag)}</li>`).join('');
    $('#not-ready').hidden = result.ready;
    const images = result.packet_page_images;
    const feature = result.feature_page;
    const order = [feature, ...images.map((_, index) => index).filter((index) => index !== feature)].filter((index) => index < images.length);
    $('#pages').innerHTML = order.map((index) => {
      const title = result.documents[index]?.title || '';
      return `<button type="button" class="page quiet${index === feature ? ' feature' : ''}" data-page="${index}" aria-label="Zoom packet page ${index + 1}: ${esc(title)}"><img src="data:image/jpeg;base64,${images[index]}" alt="Packet page ${index + 1}: ${esc(title)}"></button>`;
    }).join('');
  }

  /* Zoomable sheets */
  const lightbox = $('#lightbox');
  function closeLightbox() { lightbox.hidden = true; $('#lightbox-img').classList.remove('zoomed'); }
  $('#pages').addEventListener('click', (event) => {
    const page = event.target.closest('button.page');
    if (!page) return;
    const image = $('#lightbox-img');
    image.src = page.querySelector('img').src;
    image.alt = page.querySelector('img').alt;
    lightbox.hidden = false;
    $('#lightbox-close').focus();
  });
  $('#lightbox-img').addEventListener('click', (event) => event.currentTarget.classList.toggle('zoomed'));
  $('#lightbox-close').addEventListener('click', closeLightbox);
  document.addEventListener('keydown', (event) => { if (event.key === 'Escape' && !lightbox.hidden) closeLightbox(); });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    $('#job-error').hidden = true;
    const job = jobData();
    const type = current;
    const sample = !property;
    $('#to-pay').textContent = sample ? 'Enter your address to order' : 'Unlock the clean packet';
    $('#build-list').innerHTML = '';
    show('building');
    try {
      const response = await api(`/api/public/preview/${type.slug}`, job);
      const result = await response.json();
      lastJob = job;
      lastResult = result;
      lastType = type;
      lastWasSample = sample;
      await tickResults(result);
      renderPreview(result);
      show(3);
    } catch (error) {
      show(2);
      $('#job-error').textContent = error.message;
      $('#job-error').hidden = false;
    }
  });
  $('#edit').addEventListener('click', () => show(2));
  $('#back-preview').addEventListener('click', () => show(3));
  $('#to-pay').addEventListener('click', () => {
    $('#pay-error').hidden = true;
    if (lastWasSample) {  // a sample preview can't be ordered: back to step 1, job type kept
      show(1);
      $('#address').focus({ preventScroll: true });
      return;
    }
    show(4);
  });

  /* ---- Step 4: package and payment ---- */
  const EMAIL = /^[^@\s]+@[^@\s]+\.[^@\s]+$/;
  function payError(message) { $('#pay-error').textContent = message; $('#pay-error').hidden = false; }

  $('#checkout').addEventListener('submit', async (event) => {
    event.preventDefault();
    $('#pay-error').hidden = true;
    const email = $('#email').value.trim();
    if (lastWasSample) return payError('This preview uses the sample address. Go back and enter the real job address before ordering.');
    if (!EMAIL.test(email)) return payError('Enter a valid email address so we can find your order.');
    if (!$('#ack').checked) return payError('Please confirm you understand this is a drafting & calculation document, not a PE stamp, and that you agree to the Terms and Refund Policy.');
    const button = $('#pay-button');
    button.disabled = true;
    button.textContent = 'Saving your order…';
    const tab = window.open('', '_blank');  // opened now, while the click still counts, and pointed at Whop below
    try {
      const response = await api('/api/public/orders', {
        job_slug: lastType.slug, customer_email: email, tier: new FormData($('#checkout')).get('tier'), payload: lastJob,
      });
      const order = await response.json();
      if (tab && order.whop_checkout_url) tab.location.href = order.whop_checkout_url;
      else if (tab) tab.close();
      location.assign(order.order_url);
    } catch (error) {
      if (tab) tab.close();
      payError(error.message);
      button.disabled = false;
      button.textContent = 'Continue to Payment';
    }
  });

  /* ---- Landing page: quick start card, sample viewer, start links ---- */
  const goToWorkspace = () => $('#workspace').scrollIntoView({ behavior: TICK_MS ? 'smooth' : 'auto', block: 'start' });

  $$('.jt-pill').forEach((pill) => pill.addEventListener('click', async () => {
    await ready;
    chooseType(pill.dataset.type);
  }));
  const heroInput = $('#hero-address');
  const heroSuggest = attachSuggest(heroInput, $('#hero-suggestions'), () => $('#hero-form').requestSubmit(), 'hero-suggestion');
  $('#hero-form').addEventListener('submit', async (event) => {
    event.preventDefault();
    heroSuggest.cancel();
    await ready;
    if (!current) return;
    $('#address').value = $('#hero-address').value.trim();
    show(1, false);
    goToWorkspace();
    $('#find').requestSubmit();
  });
  $('#hero-sample').addEventListener('click', async () => {
    await ready;
    if (!current) return;
    goToWorkspace();
    $('#use-sample').click();
  });
  document.addEventListener('click', (event) => {
    const start = event.target.closest('[data-start]');
    if (!start) return;
    event.preventDefault();
    heroSuggest.cancel();
    workspaceSuggest.cancel();
    $('#hero-card').scrollIntoView({ behavior: TICK_MS ? 'smooth' : 'auto', block: 'center' });
    setTimeout(() => $('#hero-address').focus({ preventScroll: true }), TICK_MS ? 450 : 0);
  });

  const sampleTabs = $$('.doc-tab');
  function showSample(tab) {
    sampleTabs.forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
    const image = $('#sample-img');
    image.src = `/assets/samples/${tab.dataset.sample}-1000.webp`;
    image.dataset.full = `/assets/samples/${tab.dataset.sample}.png`;
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
    image.src = $('#sample-img').dataset.full || $('#sample-img').src.replace(/-1000\.webp$/, '.png');
    image.alt = $('#sample-img').alt;
    lightbox.hidden = false;
    $('#lightbox-close').focus();
  });

  /* ---- Start ---- */
  async function start() {
    try {
      const response = await fetch('/api/job-types');
      if (!response.ok) throw new Error(`The request failed (${response.status}).`);
      jobTypes = (await response.json()).job_types;
    } catch (error) {
      $('#find-error').textContent = 'Could not load the job types. Reload the page to try again.';
      $('#find-error').hidden = false;
      return;
    }
    jobTypes.forEach((type) => modules()[type.key]?.init?.(context));
    renderTypeCards();
    chooseType(jobTypes.some((type) => type.key === 'ev_charger') ? 'ev_charger' : jobTypes[0].key);
    applyRole();
    show(1, false);
  }
  const ready = start();
})();
