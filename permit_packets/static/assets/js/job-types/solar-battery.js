(() => {
  const RISE_FT = 8;
  let ctx = null;
  let runEdited = false;
  let trenchEdited = false;
  const f = (n) => ctx.form.elements[n];

  function syncFields() {
    const coupling = ctx.form.querySelector('input[name=sb_coupling]:checked').value;
    const inter = f('sb_interconnection').value;
    const batWrap = document.getElementById('sb-bat-fields');
    const batBreakerWrap = document.getElementById('sb-bat-breaker-wrap');
    const derateWrap = document.getElementById('sb-derate-wrap');
    if (batWrap) batWrap.hidden = coupling === 'solar_only';
    if (batBreakerWrap) batBreakerWrap.hidden = coupling !== 'ac_coupled';
    if (derateWrap) derateWrap.hidden = inter !== 'main_breaker_derate';
  }

  function syncRun() {
    const m = ctx.measuredFt();
    if (m === null) return;
    if (!runEdited) f('sb_run_ft').value = m + RISE_FT;
    if (!trenchEdited) f('sb_trench_ft').value = 0;
    const hint = document.getElementById('sb-run-hint');
    if (hint) hint.textContent = `${m} ft measured, plus ${RISE_FT} ft for rises`;
  }

  window.PermitJobTypes.register('solar_storage', {
    init(c) {
      ctx = c;
      ctx.$$('input[name=sb_coupling]').forEach((el) => el.addEventListener('change', syncFields));
      f('sb_interconnection').addEventListener('change', syncFields);
      f('sb_run_ft').addEventListener('input', () => { runEdited = true; });
      f('sb_trench_ft').addEventListener('input', () => { trenchEdited = true; });
      syncFields();
    },
    onProperty() { runEdited = false; trenchEdited = false; },
    onDetails() { syncFields(); syncRun(); },
    onSample() { syncFields(); f('sb_run_ft').value = 30; f('sb_trench_ft').value = 0; },
    jobFields(data) {
      const coupling = data.get('sb_coupling');
      const inter = data.get('sb_interconnection');
      return {
        coupling,
        pv_kw_dc: Number(data.get('sb_pv_kw')),
        pv_breaker_amps: Number(data.get('sb_pv_breaker')),
        battery_kwh: coupling === 'solar_only' ? 0 : Number(data.get('sb_bat_kwh') || 0),
        battery_breaker_amps: coupling === 'ac_coupled' ? Number(data.get('sb_bat_breaker') || 0) : 0,
        interconnection: inter,
        derated_main_amps: inter === 'main_breaker_derate' ? Number(data.get('sb_derated_main')) : null,
        system_model: data.get('sb_model').trim(),
        location: data.get('sb_location'),
        wiring: data.get('sb_wiring'),
        run_ft: Number(data.get('sb_run_ft')),
        trench_ft: Number(data.get('sb_trench_ft')),
        service_amps: Number(data.get('sb_service_amps')),
        bus_amps: Number(data.get('sb_bus_amps')),
        open_breaker_spaces: Number(data.get('sb_spaces')),
        rapid_shutdown: data.has('sb_rapid_shutdown'),
        ess_disconnect: data.has('sb_ess_disconnect'),
        terminals_75c: data.has('sb_75c'),
        ...window.PermitJobTypes.electricalFields(data),
      };
    },
    planFields(marks) {
      return { markers: { panel: marks.points.panel, inverter: marks.points.inverter }, route: marks.bends };
    },
  });
})();
