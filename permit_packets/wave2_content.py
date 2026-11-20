"""Wave 2 copy: calculators, permit-document guides and comparisons. Data only; wave2.py renders it with one
template per page type. Claims here come from the packet generator, the NEC sections it applies and the site's
own pages. Competitor statements are limited to what their public page said on the date checked."""
from __future__ import annotations

from dataclasses import dataclass

DISCLAIMER = "Estimate for planning. Your local authority and a licensed electrician make the final call."


@dataclass(frozen=True)
class Calc:
    slug: str
    h1: str
    crumb: str
    title: str
    description: str
    job: str  # the /start/ job slug
    answer: str
    sections: tuple[tuple[str, tuple[str, ...]], ...]
    example_label: str
    faqs: tuple[tuple[str, str], ...]
    card: str


CALCS: dict[str, Calc] = {c.slug: c for c in (
    Calc(
        slug="ev-charger-load-calculator", job="ev-charger", crumb="EV Charger Load Calculator",
        h1="EV Charger Load Calculator",
        title="EV Charger Load Calculator (NEC 220.82) | Permit Packets",
        description="Will your panel handle a Level 2 EV charger? Free NEC 220.82 load calculation, the same one used in our permit packets.",
        card="Check whether your service can carry a Level 2 charger.",
        answer=("Enter your home's size, main service and appliances, pick a charger, and see whether the service has room. "
                "It runs the same NEC 220.82 calculation that our EV charger permit packet prints, with the charger counted at 100%."),
        sections=(
            ("How does the EV charger load calculation work?", (
                "A building department reviewing an EV charger permit wants to know the existing home plus the new charger does not exceed the main service. "
                "This calculator uses the optional dwelling method in NEC 220.82. It adds 3 VA per square foot of living area, two small appliance circuits and a laundry circuit at 1,500 VA each, and the nameplate of each fixed appliance you enter.",
                "The first 10,000 VA of that total counts at 100% and the rest at 40%. Heating and air conditioning do not run together, so only the larger one is added. The charger is then added at its full rating: amps times 240 V. The total divided by 240 V is the computed service current, which is compared to your main breaker.")),
            ("Which NEC sections does it apply?", (
                "NEC 220.82 sets the calculation. NEC 625.41 treats EV charging as a continuous load, which matters when you size the circuit (see the wire and breaker calculator). "
                "If the result is over capacity, NEC 220.87 allows 12 months of utility demand data, at 125%, to stand in for the calculated existing load. That is the usual route for homes that look full on paper.",)),
            ("What do I do with the result?", (
                "If the service fits, the permit packet carries the same numbers on its load calculation sheet. If it does not, the tool names the largest common charger size that does fit. "
                "Load management, a smaller charger, a service upgrade or measured demand are the usual options. Confirm any of them with your building department.",)),
        ),
        example_label="Worked example",
        faqs=(
            ("Is this the same calculation used in a permit packet?", "Yes. It calls the same load calculation function as our EV charger packet generator, with the same charger-at-100% rule."),
            ("Does a 48 A charger need a 48 A spare on my panel?", "Not exactly. The calculation compares total computed demand to the service rating, so the spare capacity is what matters, not the free breaker slots. A panel also needs two open spaces for the charger breaker."),
            ("Why does the calculator say over capacity when my panel has spaces?", "Open spaces and load capacity are separate checks. A full-looking calculated load can sometimes be supported with 12 months of utility demand data (NEC 220.87). Ask your building department whether it accepts that."),
            ("What if I do not know my appliance VA?", "Use the nameplate on the appliance. Typical electric ranges are 8,000 to 12,000 VA and dryers 5,000 VA. Enter 0 for gas appliances."),
        )),
    Calc(
        slug="residential-load-calculator", job="panel-upgrade", crumb="Residential Load Calculator",
        h1="Residential Load Calculator (NEC 220.82)",
        title="Residential Load Calculator (NEC 220.82) | Permit Packets",
        description="Free home electrical load calculator using the NEC 220.82 optional method. See computed amps against your main service.",
        card="Compute your home's service load with the NEC 220.82 optional method.",
        answer=("Enter square footage, appliances and your main service size to get the computed load in amps. "
                "This is the NEC 220.82 optional method, the same calculation our panel upgrade, subpanel and hot tub packets use."),
        sections=(
            ("What is a residential load calculation?", (
                "A load calculation estimates the electrical demand of a home so the service, feeders and panels can be sized to carry it. "
                "Permit reviewers ask for one with panel upgrades, subpanels and any new large circuit. For an existing dwelling, NEC 220.82 gives an optional method that is shorter than the standard Article 220 calculation.",)),
            ("How does the calculation work?", (
                "General lighting is 3 VA per square foot. Two small appliance circuits and one laundry circuit are 1,500 VA each. Fixed appliances such as a range, dryer, water heater, dishwasher and hot tub are added at nameplate VA. "
                "The first 10,000 VA of the subtotal counts at 100% and the remainder at 40%. Then the larger of heating or air conditioning is added in full. The total divided by 240 V is the computed amps.",)),
            ("When is the result not enough?", (
                "The method is for dwelling units. It does not replace an engineer's calculation for unusual loads, and some cities want additional items such as a load management device or measured demand. "
                "When the answer comes out over your service rating, NEC 220.87 lets you use 12 months of utility maximum demand at 125% for the existing load. Confirm with your building department which approach it accepts.",)),
        ),
        example_label="Worked example",
        faqs=(
            ("Which NEC section is the optional method?", "NEC 220.82 covers the optional calculation for a dwelling unit with a single-phase 120/240 V service."),
            ("Do I enter gas appliances?", "Enter 0 for them. They do not add electrical load."),
            ("What service size do I need?", "Compare the computed amps to standard sizes such as 100, 150, 200 and 400 A. A result above about 80% of a service is worth a closer look before adding load."),
            ("Is this the same math as the packet?", "Yes. It calls the same load calculation function that builds the load sheet in our permit packets."),
        )),
    Calc(
        slug="ev-charger-wire-breaker-size", job="ev-charger", crumb="EV Charger Wire & Breaker Size",
        h1="EV Charger Wire and Breaker Size Calculator",
        title="EV Charger Wire & Breaker Size Calculator | Permit Packets",
        description="Find the breaker, copper wire size, ground and conduit for a Level 2 EV charger, with voltage drop. Same sizing as our packets.",
        card="Breaker, wire, ground, conduit and voltage drop for a Level 2 charger.",
        answer=("Pick the charger amps and the one-way wire run to get the breaker, copper wire gauge, ground, conduit size and voltage drop. "
                "It uses the same circuit sizing our EV charger permit packet prints on the single-line diagram."),
        sections=(
            ("How is an EV charger circuit sized?", (
                "EV charging is a continuous load, so the circuit must carry 125% of the charger's current (NEC 625.41 and 210.19(A)(1)). A 48 A charger needs 60 A of capacity, which means a 60 A breaker. "
                "The breaker comes from the next standard size at or above that value, and the wire must be rated for the breaker at its terminal temperature.",)),
            ("How is the wire size chosen?", (
                "The tool picks the smallest listed copper conductor whose 75°C ampacity (NEC 310.16) covers the breaker, then checks voltage drop over your run. If drop is above 3%, it steps up the wire size. "
                "When the hot wire is upsized, the equipment ground is upsized in proportion (NEC 250.122(B)). Small conductors also have a breaker limit under NEC 240.4(D).",)),
            ("What about conduit and a disconnect?", (
                "Conduit is the smallest EMT trade size whose 40% fill area holds two hots and the ground. A disconnect is flagged for a detached garage or a breaker over 60 A, as in the packet. "
                "Outdoor runs in hot climates may need extra temperature correction, which the packet applies for your city. This estimate does not.",)),
        ),
        example_label="Worked example",
        faqs=(
            ("What breaker does a 48 A charger need?", "A 60 A, 2-pole breaker: 48 A x 125% = 60 A."),
            ("Can I use aluminum wire?", "This calculator sizes copper at the 75°C column. Aluminum needs larger sizes and its own check."),
            ("Why did the wire size go up with a long run?", "Voltage drop grows with distance. The tool upsizes the wire to hold drop to 3% or less, as our packets do."),
            ("Does a plug-in charger change the answer?", "A receptacle adds rules, such as GFCI protection and a 50 A receptacle limit. Larger chargers are hardwired. The packet checks this when you pick the connection type."),
        )),
)}

from dataclasses import replace as _replace
CALCS["subpanel-feeder-calculator"] = Calc(
    slug="subpanel-feeder-calculator", job="subpanel", crumb="Subpanel Feeder Calculator",
    h1="Subpanel Feeder & Wire Size Calculator",
    title="Subpanel Feeder & Wire Size Calculator | Permit Packets",
    description="Size subpanel feeder wire, ground, conduit and voltage drop under NEC 310.16 and 250.122. Free calculator matching our permit packets.",
    card="Aluminum or copper feeder wire, EGC, conduit and voltage drop for a subpanel.",
    answer="Pick your subpanel feeder breaker, conductor material, conduit type and one-way run length to size the phase conductors, neutral, equipment ground and conduit. It runs the same NEC 310.16 and 250.122 sizing logic our subpanel permit packet prints on the feeder schedule.",
    sections=(
        ("How is a residential subpanel feeder sized?", ("A subpanel feeder carries power from a 2-pole breaker in your main panel to the subpanel using four conductors: two hots, an insulated neutral, and an equipment ground. Under NEC 310.16 at the 75°C terminal column, a 100 A feeder uses #1 AWG aluminum or #3 AWG copper conductors, while a 60 A feeder uses #4 AWG aluminum or #6 AWG copper.",)),
        ("When does a feeder wire need to be upsized?", ("Long runs to a detached garage, workshop, or ADU lose voltage over distance. If voltage drop exceeds 3% over the one-way run, this calculator steps up the hot and neutral wire gauges and proportionally upsizes the equipment grounding conductor under NEC 250.122(B).",)),
    ),
    example_label="Worked example", faqs=(),
)

_sp = CALCS["subpanel-feeder-calculator"]
CALCS["subpanel-feeder-calculator"] = _replace(
    _sp,
    sections=_sp.sections + (
        ("What extra rules apply to a detached building?", ("In every subpanel, the neutral bus and ground bus must stay isolated by removing the green bonding screw (NEC 250.24(A)(5)). If the subpanel is in a detached garage or shed, NEC 250.32 also requires a local grounding electrode system (such as two ground rods) and a main disconnect at the detached structure.",)),
    ),
    faqs=(
        ("Should I use aluminum or copper wire for a subpanel feeder?", "Aluminum (such as XHHW-2 or SER) is standard for 60 A to 200 A feeders because panel lugs are rated for both Cu/Al and aluminum costs significantly less. Copper uses smaller conduit."),
        ("Why does a subpanel need 4 wires instead of 3?", "Under NEC 250.24(A)(5), neutral and ground may only be bonded at the main service disconnect. Downstream subpanels require separate neutral and equipment grounding conductors."),
        ("What size conduit fits a 100 A subpanel feeder?", "Three #1 AWG aluminum THWN-2 conductors plus a #6 AWG aluminum ground fit inside 1-1/4 inch PVC or EMT at the 40% NEC Chapter 9 fill limit."),
        ("Does a detached garage subpanel need ground rods?", "Yes. NEC 250.32(A) requires a grounding electrode system at any detached building supplied by a feeder."),
    ),
)

CALCS["solar-120-percent-rule-calculator"] = Calc(
    slug="solar-120-percent-rule-calculator", job="panel-upgrade", crumb="Solar 120% Rule Calculator",
    h1="Solar 120% Rule Calculator (NEC 705.12)",
    title="Solar 120% Rule Calculator (NEC 705.12) | Permit Packets",
    description="Check if your main electrical panel passes the NEC 705.12(B)(3)(2) 120% backfeed rule for solar PV breakers. Instant free calculation.",
    card="Verify main breaker plus solar PV breaker capacity against your panel busbar.",
    answer="Enter your panel busbar rating, main breaker amps and solar PV breaker size to check compliance with the NEC 705.12(B)(3)(2) 120% rule. It runs the exact busbar backfeed check included in our residential panel upgrade permit packets.",
    sections=(
        ("What is the NEC 120% rule for solar?", ("When solar PV backfeeds into a main breaker panel, current enters from the utility main at one end and the solar breaker at the other. NEC 705.12(B)(3)(2) limits the sum of the main and solar breakers to 120% of the busbar rating when the PV breaker sits at the opposite end of the bus.",)),
        ("How do you pass if your 200A panel fails the 120% rule?", ("A 200 A panel with a 200 A busbar allows 240 A total (40 A max solar breaker). To fit a larger PV breaker, downsize the main breaker to 175 A or 150 A (if your NEC 220 load calc allows), upgrade to a 225 A bus panel, or use a line-side tap under NEC 705.11.",)),
    ),
    example_label="Worked example", faqs=(),
)

_sol = CALCS["solar-120-percent-rule-calculator"]
CALCS["solar-120-percent-rule-calculator"] = _replace(
    _sol,
    sections=_sol.sections + (
        ("Where do I find my panel's busbar rating?", ("Open the panel door and read the UL specification label inside the cabinet. Many modern 200 A panels actually have a 225 A rated busbar, which allows up to 270 A total—enough for a 200 A main plus a 70 A solar breaker.",)),
    ),
    faqs=(
        ("How much solar can I put on a 200A panel?", "With a 200 A busbar and 200 A main breaker, the 120% rule allows up to a 40 A solar backfeed breaker (200 + 40 = 240 A). With a 225 A busbar, up to 70 A is allowed."),
        ("Where must the solar breaker be installed?", "NEC 705.12(B)(3)(2) requires the solar PV backfeed breaker to be positioned at the opposite (far) end of the busbar from the main service breaker."),
        ("Can I downsize my main breaker to fit more solar?", "Yes, if an NEC Article 220 load calculation shows your home's calculated demand is below the smaller main breaker rating (for example 150 A or 175 A)."),
        ("What if my panel is a center-fed main breaker panel?", "Center-fed panels cannot use the opposite-end 120% rule and are typically limited to 100% of the busbar rating unless engineered otherwise."),
    ),
)

CALCS["hot-tub-breaker-wire-size"] = Calc(
    slug="hot-tub-breaker-wire-size", job="hot-tub-240v", crumb="Hot Tub Wire & GFCI Calculator",
    h1="Hot Tub & Sauna Breaker, GFCI & Wire Size Calculator",
    title="Hot Tub & Sauna Breaker, GFCI & Wire Size Calculator",
    description="Calculate hot tub or sauna breaker size, copper wire gauge, GFCI protection, conduit and 5 ft disconnect clearance under NEC 680.",
    card="GFCI breaker, copper conductors, insulated ground and PVC conduit for a spa or sauna.",
    answer="Select your hot tub or sauna nameplate amps, wire run length and terminal temperature rating to get the GFCI breaker size, copper wire gauge, insulated ground and PVC conduit size. It uses the same NEC Article 680 sizing logic as our 240V appliance circuit permit packets.",
    sections=(
        ("How are hot tub and sauna circuits sized?", ("Hot tubs and electric sauna heaters operate as continuous loads (3 hours or more), so the breaker and conductors must be sized at 125% of the nameplate current under NEC 680 and 424.4(B). A 36 A to 40 A spa requires a 50 A, 2-pole GFCI breaker and #6 AWG copper (or #8 AWG THWN-2 at 75°C).",)),
        ("What GFCI and disconnect rules apply to hot tubs?", ("NEC 680.44 requires Class A GFCI protection for all residential hot tubs and spas. Under NEC 680.13, the maintenance disconnect must be within sight of the spa and at least 5 feet horizontally from the inside wall of the water.",)),
    ),
    example_label="Worked example", faqs=(),
)

_ht = CALCS["hot-tub-breaker-wire-size"]
CALCS["hot-tub-breaker-wire-size"] = _replace(
    _ht,
    sections=_ht.sections + (
        ("Why does an outdoor hot tub need an insulated ground wire?", ("Unlike indoor branch circuits that allow bare copper grounds, NEC 680.42(A)(1) requires an insulated green copper equipment grounding conductor inside the raceway for outdoor spas to resist corrosion.",)),
    ),
    faqs=(
        ("What size wire and breaker does a 50A hot tub need?", "A 50 A 2-pole GFCI breaker requires #6 AWG copper with NM-B/UF-B or 60°C terminals, or #8 AWG copper THWN-2 in conduit at 75°C."),
        ("How far must the hot tub disconnect be from the water?", "At least 5 feet horizontally from the inside wall of the spa and within sight, per NEC 680.13."),
        ("Can I run Romex (NM-B) underground to a hot tub?", "No. Underground runs require Schedule 40/80 PVC conduit (18 in cover per NEC 300.5) with wet-rated THWN-2 conductors."),
    ),
)

TOOLS_PATH = "/tools/"
TOOLS_TITLE = "Free Electrical Permit Calculators | Permit Packets"
TOOLS_DESCRIPTION = "Free NEC load, EV charger wire and breaker calculators that use the same math as our permit packets."
TOOLS_INTRO = ("Three free calculators for residential electrical permits. Each runs the same functions the Permit Packets generator uses "
               "to build a packet, so the numbers match what a packet prints.")


@dataclass(frozen=True)
class Doc:
    slug: str
    name: str
    h1: str
    title: str
    description: str
    sample: str  # sample file stem for the thumbnail
    card: str
    what: tuple[str, ...]
    when: tuple[str, ...]
    contains: tuple[str, ...]
    faqs: tuple[tuple[str, str], ...]


DOCS: dict[str, Doc] = {d.slug: d for d in (
    Doc(
        slug="site-plan", name="Site Plan", h1="Site Plan for an Electrical Permit",
        title="Site Plan for an Electrical Permit | Permit Packets",
        description="What an electrical permit site plan is, when a building department asks for one, and what a good one shows.",
        sample="02-site-plan", card="Lot lines, equipment locations and the wire route.",
        what=("A site plan is a scaled top-down drawing of the property. For an electrical permit it shows the lot lines, the house, and where the electrical equipment sits: the main panel, the meter, and the new equipment such as an EV charger or subpanel.",
              "It is not a survey. It shows reviewers and inspectors where the work will happen and how far it is from the property lines and the house."),
        when=("Building departments ask for a site plan with EV charger permits, detached garage or shed feeders, subpanels, and any work that runs wire outdoors or underground.",
              "Some cities ask for one on every electrical permit and some only when the equipment is outdoors. Your city's checklist says which."),
        contains=("Lot lines with dimensions and a north arrow",
                  "The structure outline and the address or parcel number",
                  "Main panel, meter, disconnect and new equipment marked and labeled",
                  "The wire route, with its length, and trench or conduit notes",
                  "A scale, such as 1 in = 30 ft, and a note that it is not a survey",
                  "A legend so the symbols read without explanation"),
        faqs=(("Does an electrical permit site plan need to be a survey?", "Usually not. Most cities accept a scaled plan that is labeled as not a survey. Your building department sets the rule."),
              ("Where does the lot line data come from?", "Permit Packets draws lot lines from county GIS parcel data over an aerial image, where the county publishes it."),
              ("Can I draw one by hand?", "Many cities accept a clean hand sketch to scale. A drawn plan with dimensions and labels is faster to review."))),
    Doc(
        slug="single-line-diagram", name="Single-Line Diagram", h1="Single-Line Diagram for an Electrical Permit",
        title="Single-Line Diagram for an Electrical Permit | Permit Packets",
        description="What a single-line diagram is, when a building department asks for one and what a clear one shows.",
        sample="03-single-line", card="Utility to equipment in one clean drawing.",
        what=("A single-line diagram, also called a one-line or riser diagram, draws the electrical path from the utility to the equipment using one line for each circuit instead of every wire. It shows the meter, main panel, breakers, disconnects, feeders and the new load.",
              "Reviewers use it to check that the equipment, breaker, wire and conduit are sized to match."),
        when=("Most departments ask for one with panel upgrades, subpanels and EV chargers, and often with hot tub circuits. Smaller like-for-like swaps may not need one.",
              "If the job adds a feeder or changes the service, plan on needing it."),
        contains=("Utility service, meter and main breaker rating",
                  "Each breaker or disconnect with its amp rating",
                  "Wire size and type and conduit size for every run",
                  "The new equipment and its nameplate rating",
                  "Grounding electrode conductor and available fault current",
                  "A schedule that matches the numbers on the load calculation"),
        faqs=(("Is a single-line diagram the same as a wiring diagram?", "No. A wiring diagram shows every conductor and terminal. A single-line diagram shows the path and sizes with one line per circuit."),
              ("Does the diagram need to match the load calculation?", "Yes. Reviewers compare the breaker and wire sizes on the diagram to the calculated load."),
              ("Who can draw it?", "Anyone, if your city accepts owner-prepared plans. Some jobs require a licensed electrician or engineer. Check your city's rules."))),
    Doc(
        slug="load-calculation", name="Load Calculation", h1="Load Calculation for an Electrical Permit",
        title="Load Calculation for an Electrical Permit | Permit Packets",
        description="What an NEC load calculation is, when permits require one and what reviewers look for in it.",
        sample="04-load-calc", card="Proof the service can carry the new load.",
        what=("A load calculation adds up the electrical demand of a home under NEC Article 220 and compares it to the service rating. It answers one question: can this service safely carry the existing home plus the new load.",
              "For homes, most packets use the optional method in NEC 220.82, with the new load added at 100%."),
        when=("Departments ask for it with panel and service upgrades, subpanels, EV chargers, hot tubs and any large new 240 V circuit. A short statement may be enough for a small circuit, while a service upgrade almost always needs a full calculation.",),
        contains=("Living area and the 3 VA per square foot general lighting load",
                  "Small appliance and laundry circuits",
                  "Each fixed appliance at its nameplate VA",
                  "The 100% and 40% demand steps",
                  "Heating or cooling, whichever is larger",
                  "The new load, the total in VA and amps, and the service rating"),
        faqs=(("Which NEC method do permit packets use?", "The optional dwelling method in NEC 220.82, with 220.87 measured demand available when the calculated result runs over."),
              ("Can I try one first?", "Yes. The free residential load calculator runs the same math."),
              ("What if my result is over the service rating?", "Options include a service upgrade, load management, a smaller load, or measured demand under NEC 220.87."))),
    Doc(
        slug="panel-schedule", name="Panel Schedule", h1="Panel Schedule for an Electrical Permit",
        title="Panel Schedule for an Electrical Permit | Permit Packets",
        description="What a panel schedule is, when a building department asks for one and what it must list.",
        sample="01-cover", card="Every breaker, its load and its open spaces.",
        what=("A panel schedule is the circuit directory for a panel in table form. It lists each breaker position, its amp rating, what it feeds, and the load on it. It also shows which spaces are open.",
              "Reviewers use it to confirm the new breaker has room and that the panel is not overloaded or overfilled."),
        when=("Expect to provide one with panel upgrades, subpanels and any permit that adds a breaker to an existing panel, such as an EV charger or hot tub.",
              "Some cities ask for it only when the panel is being changed. Others want it for every new circuit."),
        contains=("Panel name, location, bus rating and main breaker",
                  "Every position with its breaker size, poles and circuit description",
                  "Existing circuits and the new circuit clearly marked",
                  "Open spaces, so reviewers see room for the new breaker",
                  "Loads in VA for each circuit where the city asks for them",
                  "Panel manufacturer and model for the cut sheet"),
        faqs=(("What if I do not know what each breaker feeds?", "Label what you can identify and flag the rest. Packets mark missing existing-circuit data for your review."),
              ("How many open spaces does an EV charger need?", "A 240 V breaker is 2-pole, so it needs two adjacent open spaces."),
              ("Is the panel directory on the door enough?", "Not usually. Reviewers want a schedule in the plan set."))),
    Doc(
        slug="equipment-cut-sheets", name="Equipment Cut Sheets", h1="Equipment Cut Sheets for an Electrical Permit",
        title="Equipment Cut Sheets for an Electrical Permit | Permit Packets",
        description="What equipment cut sheets are, when a building department asks for them and what to attach.",
        sample="05-spec-sheet", card="Manufacturer data for the charger, panel or breaker.",
        what=("A cut sheet, also called a data sheet or spec sheet, is the manufacturer's page that lists the equipment's ratings and listing marks. For a charger it shows the amp rating, voltage, enclosure and certification, such as a UL listing.",
              "It lets the reviewer verify the equipment against the plans without having to look it up."),
        when=("Departments commonly ask for cut sheets for EV chargers, new panels and subpanels, disconnects and breakers, and for equipment with a hot tub or heat pump.",
              "The model on the cut sheet should match the model on the plans."),
        contains=("Manufacturer, model number and the exact variant you are installing",
                  "Voltage, amps, phase and breaker size",
                  "A listing mark, such as UL or ETL",
                  "Enclosure type for outdoor installs",
                  "Interrupting rating for panels and breakers",
                  "Terminal temperature rating for wire sizing"),
        faqs=(("Where do I get the cut sheet?", "From the manufacturer's website. Permit Packets attaches the data sheet when your model is in its equipment library."),
              ("Do I attach the full manual?", "No. One or two pages that show the ratings and listing are enough."),
              ("What if the model is not in the library?", "The packet flags it so you can attach the data sheet yourself."))),
)}
DOCS_PATH = "/permit-documents/"
DOCS_TITLE = "Electrical Permit Documents Explained | Permit Packets"
DOCS_DESCRIPTION = "What each document in an electrical permit set is, when cities ask for it and what a good one contains."
DOCS_INTRO = "Building departments ask for a handful of documents with residential electrical permits. Each guide explains one: what it is, when it is required and what a good one contains."


@dataclass(frozen=True)
class Compare:
    slug: str
    name: str
    h1: str
    title: str
    description: str
    checked: str  # ISO date the source page was read
    source: str  # the one page fetched, or "" for a category comparison
    intro: str
    rows: tuple[tuple[str, str, str], ...]  # aspect, them, us
    better: tuple[str, ...]  # when they are the better choice
    caveat: str
    faqs: tuple[tuple[str, str]]
    card: str


US = {
    "scope": "Residential electrical permit packet: site plan, single-line diagram, load calculation, panel schedule and equipment data sheets.",
    "how": "Built from one address, with parcel data from county GIS where available and your answers about the equipment.",
    "price": "Three packages: $39, $89 and $169, with a free watermarked preview first.",
    "stamp": "Not PE-stamped. You submit the application to your city yourself.",
}

COMPARES: dict[str, Compare] = {c.slug: c for c in (
    Compare(
        slug="mysiteplan", name="MySitePlan", h1="Permit Packets vs MySitePlan",
        title="Permit Packets vs MySitePlan | Permit Packets",
        description="How Permit Packets compares with MySitePlan: electrical permit packets versus site plans. Based on MySitePlan's public page.",
        checked="2026-11-17", source="https://www.mysiteplan.com/",
        card="Electrical permit packets versus site plans, side by side.",
        intro=("MySitePlan makes site plans for permits. Permit Packets makes electrical permit packets, which include a site plan along with the electrical sheets. "
               "This page compares them using what MySitePlan's public page said on November 17, 2026."),
        rows=(
            ("What it produces", "Site plans in several levels, from a basic plot plan to detailed residential and commercial plans. The page also links to 3D and 2D renderings.", US["scope"]),
            ("Typical uses listed", "Fence, deck, shed, garage, driveway, pool, sign and remodeling permits, plus HOA and other permits.", "Electrical permits for EV chargers, panel upgrades, subpanels and 240 V circuits such as hot tubs."),
            ("How plans are made", "Remotely from satellite imagery, GIS data and county parcel information, with no site visit, plus customer-provided material.", US["how"]),
            ("Prices on the page", "Basic Plot Plan $99, Medium Site Plan $119, Detailed Site Plan (residential) $159.", US["price"]),
            ("Turnaround stated", "Accepted site plans in under 24 hours.", "Download as soon as payment clears on the $89 package; the $169 package is checked against your city's requirements within 24 hours."),
            ("Revisions and refunds", "Unlimited revisions and a money-back guarantee, with conditions shown on the page.", "Full refund before you download your clean packet."),
            ("Stamp or certification", "Plans are non-certified and not a survey.", US["stamp"]),
        ),
        better=("You need only a site plan for a fence, deck, shed or similar permit that has no electrical plans.",
                "You need a commercial site plan or a 3D rendering.",
                "You want a person to draft the plan and revise it for you."),
        caveat="MySitePlan's details may have changed since the date checked. Read their page before deciding.",
        faqs=(("Does Permit Packets include a site plan?", "Yes. Every electrical packet includes a site plan with the equipment and wire route marked."),
              ("Is Permit Packets a replacement for MySitePlan?", "Only for electrical permits. For non-electrical permits that need a site plan, a site plan service fits better."))),
    Compare(
        slug="fiverr-drafters", name="Fiverr drafters", h1="Permit Packets vs Fiverr Drafters",
        title="Permit Packets vs Fiverr Drafters | Permit Packets",
        description="Automated electrical permit packets compared with hiring a freelance drafter on Fiverr. Where each one fits.",
        checked="2026-11-17", source="", card="Automated packets compared with freelance drafters.",
        intro=("Freelance marketplaces such as Fiverr list independent drafters who make plans on request. This is a category comparison based on how that model generally works. "
               "No single seller is described, and quality, price and speed vary by seller."),
        rows=(
            ("How you buy", "You browse sellers, compare listings and reviews, and send a brief.", "You enter an address and see a free watermarked preview."),
            ("What you get", "Varies by seller and package. Confirm which sheets are included.", US["scope"]),
            ("Price", "Set by each seller and often changes with scope and add-ons.", US["price"]),
            ("Speed", "Set by each seller and depends on their workload and your replies.", "Packet preview in minutes; download after payment."),
            ("Local knowledge", "Depends on the individual. Some know your city's rules well.", "Built-in checklists for the cities listed on our permits pages, and a general NEC checklist elsewhere."),
            ("Custom work", "A person can handle unusual layouts and special requests.", "Standard residential jobs only."),
            ("Stamp", "Depends on the seller. Check whether they are licensed.", US["stamp"]),
        ),
        better=("Your job is unusual, such as a complex multi-building site or a custom layout.",
                "You want one person to talk to and revise the drawings with you.",
                "You need a licensed professional to prepare or stamp the plans."),
        caveat="This compares a category, not any one seller. Read the listing, reviews and delivery terms for the seller you pick.",
        faqs=(("Is a freelance drafter safer?", "Neither is automatically safer. Ask any provider which sheets you get, whether the load calculation shows its NEC basis, and whether your city accepts the result."),
              ("Can I use both?", "Yes. Some people use a packet as a starting draft and have a licensed electrician review it."))),
    Compare(
        slug="cad-drafter", name="a CAD drafter", h1="Permit Packets vs a CAD Drafter",
        title="Permit Packets vs a CAD Drafter | Permit Packets",
        description="Automated electrical permit packets compared with hiring a local CAD drafter or design firm. Where each fits.",
        checked="2026-11-17", source="", card="Automated packets compared with hiring a CAD drafter.",
        intro=("A CAD drafter or small design firm prepares plans in drafting software, often for contractors. This is a category comparison based on how that service generally works, "
               "not a statement about any firm."),
        rows=(
            ("How you buy", "You contact a drafter or firm, share details and agree on scope and a quote.", "You enter an address and see a free watermarked preview."),
            ("What you get", "Drawings made to your scope, often as editable CAD files.", US["scope"] + " Delivered as a PDF packet or a ZIP of individual files."),
            ("Price", "Quoted per project or hourly.", US["price"]),
            ("Speed", "Depends on the drafter's schedule and revision rounds.", "Preview in minutes; download after payment."),
            ("Custom and complex jobs", "Well suited to commercial, multi-family and unusual sites.", "Standard residential jobs."),
            ("Revisions", "Handled by a person in conversation.", "Preview before you pay; see the refund policy for what happens after."),
            ("Stamp", "A drafter is not automatically a licensed engineer. Ask.", US["stamp"]),
        ),
        better=("The project is commercial, multi-family or otherwise outside a standard home.",
                "You need editable CAD files for your own workflow.",
                "You want an engineer's stamp or a firm already working with your city."),
        caveat="Scope, price and turnaround vary by firm. Ask for a written scope before you commit.",
        faqs=(("Do I get CAD files with Permit Packets?", "You get a PDF packet or a ZIP of individual files. We do not advertise editable CAD files."),
              ("When does a drafter make sense?", "When the job falls outside standard residential electrical work or you need editable drawings."))),
)}
