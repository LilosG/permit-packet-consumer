"""The standby generator interlock / transfer switch job as the form sends it."""
from typing import Literal

from pydantic import Field, model_validator

from permit_packets.core.schemas import HomeLoadsRequest, JobRequestBase


class GeneratorRequest(JobRequestBase):
    home: HomeLoadsRequest
    service_amps: int = Field(ge=60, le=400)
    open_breaker_spaces: int = Field(ge=0, le=60)
    transfer_type: Literal["interlock", "manual_transfer_switch", "automatic_transfer_switch"]
    generator_kw: float = Field(ge=1.0, le=50.0)
    inlet_amps: Literal[30, 50, 100, 150, 200]
    generator_model: str = Field(default="", max_length=120)
    fuel_type: Literal["natural_gas", "propane", "diesel", "gasoline"] | None = None
    neutral_type: Literal["floating", "bonded"] = "floating"
    location: Literal["exterior_wall", "detached_pad"] = "exterior_wall"
    wiring: Literal["PVC", "EMT", "cable"] = "PVC"
    run_ft: int = Field(ge=1, le=500)
    trench_ft: int = Field(default=0, ge=0, le=500)
    terminals_75c: bool = True

    @model_validator(mode="after")
    def trench_is_part_of_the_run(self) -> "GeneratorRequest":
        if self.trench_ft > self.run_ft:
            raise ValueError("the underground part can't be longer than the whole run")
        return self

    @model_validator(mode="after")
    def interlock_inlet_limit(self) -> "GeneratorRequest":
        if self.transfer_type == "interlock" and self.inlet_amps > 50:
            raise ValueError("a main-breaker interlock kit uses a 30 A or 50 A generator inlet breaker")
        return self

    @model_validator(mode="after")
    def plan_marks_the_panel_and_inlet(self) -> "GeneratorRequest":
        if self.plan is not None and not {"panel", "inlet"} <= self.plan.markers.keys():
            raise ValueError("the plan needs a main panel marker and a generator/inlet marker")
        return self
