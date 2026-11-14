/* The service and panel details every job type asks for: the utility's available fault current, the
   equipment's interrupting rating, and (item 5) where the panel is and how it is built.
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
    return fields;
  };
})();
