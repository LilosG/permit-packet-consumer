(() => {
  const RISE_FT = 6;
  let ctx = null;
  let runEdited = false;
  let trenchEdited = false;
  const f = (n) => ctx.form.elements[n];

  function syncRun() {
    const m = ctx.measuredFt();
    if (m === null) return;
    if (!runEdited) f('gen_run_ft').value = m + RISE_FT;
    if (!trenchEdited) f('gen_trench_ft').value = 0;
    const hint = document.getElementById('gen-run-hint');
    if (hint) hint.textContent = `${m} ft measured, plus ${RISE_FT} ft for rises`;
  }

  window.PermitJobTypes.register('generator', {
    init(c) {
      ctx = c;
      f('gen_run_ft').addEventListener('input', () => { runEdited = true; });
      f('gen_trench_ft').addEventListener('input', () => { trenchEdited = true; });
    },
    onProperty() { runEdited = false; trenchEdited = false; },
    onDetails() { syncRun(); },
    onSample() { f('gen_run_ft').value = 25; f('gen_trench_ft').value = 0; },
    jobFields(data) {
      return {
        transfer_type: data.get('gen_transfer_type'),
        fuel_type: data.get('gen_fuel') || null,
        generator_kw: Number(data.get('gen_kw')),
        inlet_amps: Number(data.get('gen_inlet_amps')),
        generator_model: data.get('gen_model').trim(),
        neutral_type: data.get('gen_neutral'),
        location: data.get('gen_location'),
        wiring: data.get('gen_wiring'),
        run_ft: Number(data.get('gen_run_ft')),
        trench_ft: Number(data.get('gen_trench_ft')),
        service_amps: Number(data.get('gen_service_amps')),
        open_breaker_spaces: Number(data.get('gen_spaces')),
        terminals_75c: data.has('gen_75c'),
        ...window.PermitJobTypes.electricalFields(data),
      };
    },
    planFields(marks) {
      return { markers: { panel: marks.points.panel, inlet: marks.points.inlet }, route: marks.bends };
    },
  });
})();
