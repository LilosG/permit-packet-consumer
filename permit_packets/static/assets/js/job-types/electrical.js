/* The service and panel details every job type asks for: the utility's available fault current, the
   equipment's interrupting rating, and where the panel is, its bus and main, and its existing
   grounding electrode conductor.
   Each job type's jobFields() merges these into its payload. */
(() => {
  const whole = (value) => {
    const number = Math.round(Number(value));
    return Number.isFinite(number) && number > 0 ? number : null;
  };

  window.PermitJobTypes.electricalFields = (data) => {
    const fields = { equipment_aic_ka: whole(data.get('equipment_aic_ka')) || 10 };
    const fault = whole(data.get('available_fault_current_a'));
    if (fault) fields.available_fault_current_a = fault;
    const bus = whole(data.get('panel_bus_amps'));
    if (bus) fields.panel_bus_amps = bus;
    const main = data.get('panel_main');
    if (main) fields.panel_main = main;
    fields.panel_location = (data.get('panel_location') || '').trim();
    fields.gec_size = (data.get('gec_size') || '').trim();
    return fields;
  };
})();
