"""The residential solar PV & battery storage job as the form sends it."""
from typing import Literal

from pydantic import Field, model_validator

from permit_packets.core.schemas import HomeLoadsRequest, JobRequestBase


class SolarStorageRequest(JobRequestBase):
    home: HomeLoadsRequest
    service_amps: int = Field(ge=60, le=400)
    bus_amps: int = Field(ge=60, le=400)
    open_breaker_spaces: int = Field(ge=0, le=60)
    coupling: Literal["dc_coupled", "ac_coupled", "solar_only"]
    pv_kw_dc: float = Field(ge=0.5, le=40.0)
    pv_breaker_amps: int = Field(ge=15, le=125)
    battery_kwh: float = Field(default=0.0, ge=0.0, le=80.0)
    battery_breaker_amps: int = Field(default=0, ge=0, le=125)
    interconnection: Literal["load_side_120", "supply_side_tap", "main_breaker_derate"] = "load_side_120"
    derated_main_amps: int | None = Field(default=None, ge=60, le=400)
    system_model: str = Field(default="", max_length=120)
    location: Literal["exterior_wall", "garage"] = "exterior_wall"
    wiring: Literal["EMT", "PVC", "RMC"] = "EMT"
    run_ft: int = Field(ge=1, le=500)
    trench_ft: int = Field(default=0, ge=0, le=500)
    rapid_shutdown: bool = True
    ess_disconnect: bool = True
    terminals_75c: bool = True

    @model_validator(mode="after")
    def ac_coupled_requires_battery_breaker(self) -> "SolarStorageRequest":
        if self.coupling == "ac_coupled" and (self.battery_kwh <= 0 or self.battery_breaker_amps < 15):
            raise ValueError("an AC-coupled battery system needs battery kWh and a battery backfeed breaker (15 A or more)")
        if self.coupling == "dc_coupled" and self.battery_kwh <= 0:
            raise ValueError("a DC-coupled solar + storage system needs the battery capacity in kWh")
        return self

    @model_validator(mode="after")
    def derate_needs_smaller_main(self) -> "SolarStorageRequest":
        if self.interconnection == "main_breaker_derate" and (self.derated_main_amps is None or self.derated_main_amps >= self.service_amps):
            raise ValueError("enter a derated main breaker size smaller than the existing main breaker")
        return self

    @model_validator(mode="after")
    def trench_within_run(self) -> "SolarStorageRequest":
        if self.trench_ft > self.run_ft:
            raise ValueError("the underground part can't be longer than the whole run")
        return self

    @model_validator(mode="after")
    def plan_marks_panel_and_inverter(self) -> "SolarStorageRequest":
        if self.plan is not None and not {"panel", "inverter"} <= self.plan.markers.keys():
            raise ValueError("the plan needs a main panel marker and an inverter/ESS marker")
        return self
