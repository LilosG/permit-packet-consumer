"""The words on the content pages: the four job hubs, the four audience pages, pricing and about.

Every claim here comes from the existing site copy, /terms/, /refund/, the job-type registry, what the packet
generator prints, the jurisdiction modules or the El Cajon sample. Nothing else goes in: no statistics, no
customer counts, no testimonials, no turnaround claims beyond the three the site already makes.

Text may hold inline HTML (links) and the token {permits}, which pages.py replaces with a link to the city
guides once /permits/ is live, and with plain words until then. The FAQPage structured data gets plain text.
"""
from __future__ import annotations

from dataclasses import dataclass, field

TIERS = (
    ("load_calc", "39", "Load Calc & Panel Audit", "NEC 220 load calculation and a panel capacity audit.", False),
    ("instant_packet", "89", "Instant Permit Packet",
     "The complete clean packet and individual files. Download as soon as payment clears.", True),
    ("city_checked_24h", "169", "24-Hour City-Checked Packet",
     "The complete packet, checked against your city's published requirements within 24 hours.", False),
)


@dataclass(frozen=True)
class Sheet:
    title: str
    text: str
    thumb: str = ""  # a sample file stem in /assets/samples/, where the El Cajon sample has this sheet


@dataclass(frozen=True)
class Hub:
    slug: str  # the job slug in sitedata.JOBS
    type_key: str
    path: str
    h1: str
    crumb: str
    title: str
    description: str
    answer: str
    job_name: str  # "EV charger", used in headings
    sheets_intro: str
    sheets: tuple[Sheet, ...]
    checks_intro: str
    checks: tuple[str, ...]
    steps: tuple[tuple[str, str], ...]
    faqs: tuple[tuple[str, str, str], ...]  # question, answer, one-line summary for /faq/
    extra_title: str = ""
    extra: tuple[str, ...] = ()


STEPS_COMMON = (
    ("Enter the address",
     "Pick the job, drop the pins on the aerial map and answer a few plain questions. The parcel and lot lines come from county GIS."),
    ("Preview every sheet free",
     "See the live NEC check and each sheet of your packet, watermarked, before you pay."),
    ("Pay, download and submit",
     "Unlock the clean PDF and individual files, plus your city's submission steps. You submit to the city yourself."),
)

HUBS: dict[str, Hub] = {}


def _hub(hub: Hub) -> None:
    HUBS[hub.slug] = hub


_hub(Hub(
    slug="ev-charger", type_key="ev_charger", path="/ev-charger-permit/",
    h1="EV Charger Permit Plans & Packet", crumb="EV Charger", job_name="EV charger",
    title="EV Charger Permit Plans, Load Calc & Site Plan Online",
    description="Site plan, single-line diagram and load calc for a Level 2 EV charger permit, built from your address. Free watermarked preview.",
    answer=("An EV charger permit packet is the set of plans and calculations a building department reviews before "
            "you install a Level 2 charger: a site plan, single-line diagram, load calculation, panel schedule and "
            "equipment data. Permit Packets builds yours from one address, typically in under 5 minutes, with a free "
            "watermarked preview."),
    sheets_intro=("The EV charger packet is eight sheets. Each sheet we draw carries a title block with the project address, "
                  "parcel number and sheet number, and the manufacturer's data sheet follows when your charger model is in our library."),
    sheets=(
        Sheet("Checklist and Checks", "Your city's checklist item by item with a status, the engineering checks, and a short list of items flagged for your review.", "01-cover"),
        Sheet("Permit Application Data", "The fields for the city's permit form, the scope of work and the inspections to expect."),
        Sheet("Site Plan", "Your parcel on aerial imagery with lot lines, the panel, charger and disconnect marked, the measured wire route and a scale bar.", "02-site-plan"),
        Sheet("Single-Line Diagram", "Meter, main panel, disconnect and charger with conductor sizes, conduit and breaker, plus a conduit schedule and trench detail.", "03-single-line"),
        Sheet("Load Calculation", "The NEC Article 220 optional dwelling method with the charger added at 100% of nameplate, compared against your service.", "04-load-calc"),
        Sheet("Panel Schedule", "A circuit directory with the new breaker marked, ready to field verify and fill in (NEC 408.4)."),
        Sheet("Equipment Data", "Charger, breaker, disconnect and conduit with their listings. <strong>Manufacturer UL cut sheets attached:</strong> skip the manual search. For charger models in our library, the manufacturer's <a href=\"/guides/what-is-an-appliance-cut-sheet-for-electrical-permit/\">cut sheet</a> and UL spec sheet follow this sheet in your packet automatically.", "05-spec-sheet"),
        Sheet("Pre-Submittal Review", "A final checklist: existing loads, trench route, open panel spaces, HOA approval and the code edition."),
    ),
    checks_intro="These are the checks the generator runs on your job and the notes it prints on the sheets.",
    checks=(
        "Service capacity: the load calculation with the charger at 100%, against your service rating. If you enter a measured peak demand, the check uses NEC 220.87 instead.",
        "Panel spaces: two open breaker spaces are needed for the 2-pole breaker.",
        "Circuit sizing: the breaker is sized at 125% of the continuous charger load, and the conductors must carry it at the 75°C column.",
        "Voltage drop over the measured wire run, flagged when it passes 3%.",
        "Connection type: a charger too large for a receptacle circuit (over a 50 A breaker) must be hardwired.",
        "Disconnect: shown for a detached-garage install or a charger over 60 A, with the NEC 625.43 note printed when none is needed.",
        "Interrupting rating (NEC 110.9 and 110.10): the available fault current compared with the panel and breaker rating.",
        "Temperature correction (NEC 310.15(B)(1)) for runs outdoors or in the sun, where the city's design temperature is set up.",
        "Code notes on the diagram, including NEC 625.54 and 625.22 for a hardwired charger and 625.52 for ventilation.",
    ),
    steps=STEPS_COMMON,
    faqs=(
        ("Do I need a permit to install an EV charger?",
         "That depends on your city and your job, and most cities that publish an EV charger checklist ask for plans. The packet follows the published checklist where we have one. Confirm with your building department before you start.",
         "Rules depend on the city. The EV charger page shows what the packet follows."),
        ("What plans does a city ask for with an EV charger permit?",
         "Cities that publish a checklist commonly list a permit application, the charger's specifications, a load calculation, a site plan drawn to scale and a single-line diagram. El Cajon, CA, for example, lists exactly those, plus the NRTL listing mark on the charger.",
         "Usually a site plan, single-line diagram and load calc. See the EV charger page for El Cajon's list."),
        ("How is the charger counted in the load calculation?",
         "The sample packet adds the charger at 100% of nameplate (48 A at 240 V is 11,520 VA) on the NEC Article 220 optional dwelling method. The breaker is sized separately, at 125% of the continuous load. Confirm the method your city accepts.",
         "At 100% of nameplate in the load calc; the breaker is sized at 125%."),
        ("Does the packet include the charger's data sheet?",
         "Yes for models in our library: the manufacturer's data sheet follows the Equipment Data sheet. For other models, the sheet tells you to attach the manufacturer's data sheet and listing information behind it.",
         "Yes for models in our library, otherwise you attach it."),
        ("What if the charger is in a detached garage?",
         "The packet shows a disconnect for a detached-garage install, adds the trench detail and prints a reminder to confirm grounding at the garage. Cities can add their own rules, such as El Cajon's 50 ft line-of-sight disconnect note.",
         "A disconnect and trench detail are drawn. See the EV charger page."),
        ("Can I see a finished EV charger packet?",
         'Yes. The <a href="/sample-packet/">sample packet</a> is a 48 A charger on a 200 A panel in El Cajon, CA, with every sheet shown full size. It uses a placeholder owner name.',
         "Yes, the sample packet shows a 48 A charger in El Cajon."),
    ),
))

_hub(Hub(
    slug="panel-upgrade", type_key="service_upgrade", path="/panel-upgrade-permit/",
    h1="Panel Upgrade Permit Plans & Load Calculation", crumb="Panel Upgrade", job_name="panel upgrade",
    title="200A Panel Upgrade Permit Plans, Riser & Load Calc",
    description="Riser diagram, site plan and NEC 220 load calc for a residential service or panel upgrade permit, built from your address. Free preview.",
    answer=("A panel upgrade permit packet shows a building department what is changing at your service: a site plan, "
            "riser diagram, NEC Article 220 load calculation, panel schedule and a utility service request page. "
            "Permit Packets builds it from one address, typically in under 5 minutes, with a free watermarked preview."),
    sheets_intro=("The panel upgrade packet is nine sheets. It covers both a larger service (an upgrade) and a like-for-like "
                  "panel replacement, and the manufacturer's data sheet follows when your panel model is in our library."),
    sheets=(
        Sheet("Checklist and Checks", "Your city's checklist item by item with a status, the engineering checks and the items flagged for your review."),
        Sheet("Permit Application Data", "The fields for the city's permit form and a written scope of work for the service."),
        Sheet("Site Plan", "Your parcel on aerial imagery with the meter and main panel marked and the service run measured."),
        Sheet("Riser Diagram", "Utility to meter to main to panel, with service conductors, conduit, the emergency disconnect and the grounding electrodes."),
        Sheet("Load Calculation", "The NEC Article 220 load calculation run against the new service size, with a pass or fail."),
        Sheet("Panel Schedule", "A circuit directory for the new panel, ready to field verify and fill in."),
        Sheet("Utility Service Request", "The data your utility asks for, laid out for transfer: meter number, old and new service size, service type and requested disconnect and reconnect times. It is not the utility's own form."),
        Sheet("Equipment Data", "Panel, main breaker, conductors and grounding with listings, followed by the manufacturer's data sheet."),
        Sheet("Pre-Submittal Review", "A final checklist: loads, the utility request, conductor size, grounding electrodes, water and gas bonds, working space and the code edition."),
    ),
    checks_intro="These are the checks the generator runs on your job and the notes it prints on the sheets.",
    checks=(
        "Service capacity: the computed load against the new service size.",
        "Service conductors: sized for 83% of the service rating at the 75°C column (NEC 310.12), with conduit fill at 40%.",
        "Panel rating: the bus rating must be at least the main breaker rating.",
        "Grounding electrode conductor sized per electrode type (NEC 250.66), with the electrodes listed on the riser.",
        "Emergency disconnect (NEC 230.85): drawn and labeled for either a main breaker outdoors or a meter disconnect.",
        "Surge protection: a Type 1 or Type 2 surge protective device at the service (NEC 230.67).",
        "Solar (the 120% rule), when your home has PV: main breaker plus PV breaker against the bus rating.",
        "Meter socket: checked against the utility's approved list where we have it, and the main-disconnect distance limit where a city sets one.",
        "Temperature correction (NEC 310.15(B)(1)) for conductors exposed to heat, where the city's design temperature is set up.",
    ),
    steps=STEPS_COMMON,
    faqs=(
        ("Do I need a permit to upgrade my electrical panel?",
         "Most cities ask for one when the panel or service changes, and many ask for plans. Confirm with your building department. The packet follows the city's published checklist where we have one.",
         "Most cities ask for one. Confirm locally; see the panel upgrade page."),
        ("Why does a panel upgrade need a load calculation?",
         "The service size has to cover the home's calculated load. The packet runs the NEC Article 220 calculation from your square footage and appliances and compares it to the new service size, with a pass or fail.",
         "To show the new service covers the calculated load."),
        ("Can I check my panel capacity before I buy anything else?",
         "Yes. The $39 Load Calc & Panel Audit delivers the load calculation sheet and the panel schedule and capacity audit sheet, so you know your numbers before you collect quotes.",
         "Yes, the $39 package delivers the load calc and capacity audit."),
        ("What is the utility service request page?",
         "It is your job's data arranged for the utility's service request: utility, meter number, old and new service size, service type, and blank lines for the requested disconnect and reconnect. It is not the utility's form.",
         "Your job data laid out for the utility's request. Not their form."),
        ("Does the packet handle solar and surge protection?",
         "Yes. If you say the home has solar, the 120% rule check runs. A surge protective device is shown on the riser, as NEC 230.67 requires for a replaced or upgraded dwelling service.",
         "Both are checked and shown on the riser."),
        ("What is the difference between an upgrade and a replacement?",
         "An upgrade makes the service larger, for example 100 A to 200 A. A replacement swaps the panel at the same size. The packet's scope of work and checks follow whichever you choose.",
         "Upgrade means a larger service; replacement keeps the size."),
    ),
))

_hub(Hub(
    slug="subpanel", type_key="subpanel", path="/subpanel-permit/",
    h1="Subpanel Permit Plans & Drawings", crumb="Subpanel", job_name="subpanel",
    title="Subpanel Permit Plans, Feeder Schedule & Load Calc",
    description="Feeder schedule, single-line diagram, voltage drop and load calc for a residential subpanel permit, built from your address. Free preview.",
    answer=("A subpanel permit packet shows a building department the new panel and the feeder that serves it: a site plan, "
            "single-line diagram, feeder schedule, load calculation and panel schedule. Permit Packets builds it from one "
            "address, typically in under 5 minutes, with a free watermarked preview."),
    sheets_intro=("The subpanel packet is nine sheets. The feeder schedule is the one that sets it apart from the other jobs, "
                  "and the manufacturer's data sheet follows when your subpanel model is in our library."),
    sheets=(
        Sheet("Checklist and Checks", "Your city's checklist item by item with a status, the engineering checks and the items flagged for your review."),
        Sheet("Permit Application Data", "The fields for the city's permit form, the scope of work and the inspections to expect."),
        Sheet("Site Plan", "Your parcel on aerial imagery with the main panel and subpanel marked and the feeder run measured."),
        Sheet("Single-Line Diagram", "Main panel, feeder breaker, feeder conductors and conduit, and the subpanel, with a grounding electrode shown for a detached building."),
        Sheet("Feeder Schedule", "Phase conductors, neutral, equipment ground, conduit and fill, run length, trench cover and voltage drop for the feeder."),
        Sheet("Load Calculation", "The NEC Article 220 load calculation for the service the subpanel hangs on."),
        Sheet("Panel Schedule", "A circuit directory for the subpanel, ready to field verify and fill in."),
        Sheet("Equipment Data", "Subpanel, feeder breaker and conductors with listings, followed by the manufacturer's data sheet."),
        Sheet("Pre-Submittal Review", "A final checklist: loads, open spaces, feeder route and trench depth, terminal ratings and the code edition."),
    ),
    checks_intro="These are the checks the generator runs on your job and the notes it prints on the sheets.",
    checks=(
        "Service capacity: the computed load against your existing service.",
        "Panel spaces: two open breaker spaces in the main panel for the feeder breaker.",
        "Feeder breaker: it may not exceed the subpanel's rating.",
        "Feeder conductors: phase, neutral and equipment ground sized, with the feeder load checked against the breaker.",
        "Voltage drop: the feeder is checked against a 3% limit and upsized when it passes.",
        "Conduit fill at 40% for the four feeder wires (Chapter 9, Table 4).",
        "Grounding for a detached building: a new grounding electrode (NEC 250.32(A)) and the equipment ground (NEC 250.122).",
        "Terminal ratings at 75°C (NEC 110.14(C)), and trench cover for PVC (NEC 300.5).",
        "Interrupting rating (NEC 110.9 and 110.10) and the panel schedule check (NEC 408.4).",
    ),
    steps=STEPS_COMMON,
    faqs=(
        ("Do I need a permit to add a subpanel?",
         "Most cities ask for one when you add a panel or a feeder, and some ask for plans with it. Confirm with your building department. The packet follows the published checklist where we have one.",
         "Most cities ask for one. See the subpanel page for what the packet covers."),
        ("What is a feeder schedule?",
         "It is the sheet that lists the feeder's conductors, conduit, run length, trench cover and voltage drop, each with its code basis, so a plan reviewer can check the feeder in one place.",
         "The one-page feeder sheet: conductors, conduit, cover, voltage drop."),
        ("How is the feeder sized?",
         "From the feeder breaker you choose. The packet sizes the conductors for that breaker, adds a neutral and an equipment ground, and upsizes the wire if the voltage drop passes 3%.",
         "From the feeder breaker, upsized if voltage drop passes 3%."),
        ("Can the subpanel be in a detached building?",
         "Yes. The packet adds the grounding electrode at the building to the diagram and puts it on the pre-submittal checklist, along with the disconnect at the building.",
         "Yes. A grounding electrode is drawn and checked."),
        ("Why does a subpanel packet have a load calculation?",
         "The new panel's feeder draws from your existing service. The NEC Article 220 calculation shows whether that service still has capacity, with a pass or fail.",
         "To show the existing service still has capacity."),
        ("Where do I enter the subpanel's size and location?",
         "In the wizard's job step you give the subpanel and feeder breaker sizes, the run, wiring method and location, and you tap the main panel and subpanel on the aerial map.",
         "In the job step of the wizard."),
    ),
))

_hub(Hub(
    slug="hot-tub-240v", type_key="appliance_circuit", path="/hot-tub-240v-permit/",
    h1="Hot Tub & 240V Circuit Permit Plans", crumb="Hot Tub / 240V", job_name="hot tub or 240V circuit",
    title="Hot Tub & 240V Circuit Permit Plans & Load Calc",
    description="Site plan, single-line diagram and load calc for a hot tub, sauna, heat pump or mini-split circuit permit. Free watermarked preview.",
    answer=("A hot tub or 240V circuit permit packet shows a building department the new circuit and the appliance on it: a "
            "site plan, single-line diagram, load calculation and panel schedule. Permit Packets builds it from one "
            "address for a hot tub, sauna, heat pump or mini-split, typically in under 5 minutes."),
    sheets_intro=("The 240V circuit packet is eight sheets. You choose the appliance in the wizard: a hot tub, sauna, heat pump, "
                  "mini-split or another 240 V appliance. The manufacturer's data sheet follows when your model is in our library."),
    sheets=(
        Sheet("Checklist and Checks", "Your city's checklist item by item with a status, the engineering checks and the items flagged for your review."),
        Sheet("Permit Application Data", "The fields for the city's permit form, the scope of work and the inspections to expect."),
        Sheet("Site Plan", "Your parcel on aerial imagery with the main panel and appliance marked and the circuit run measured."),
        Sheet("Single-Line Diagram", "Main panel, breaker, disconnect, conductors and the appliance, with conduit sizes."),
        Sheet("Load Calculation", "The NEC Article 220 load calculation with the new appliance added, against your service."),
        Sheet("Panel Schedule", "A circuit directory with the new 2-pole breaker marked, ready to field verify and fill in."),
        Sheet("Equipment Data", "Appliance, breaker and conductors with their listings, followed by the manufacturer's data sheet."),
        Sheet("Pre-Submittal Review", "A final checklist that changes with the appliance, for example spa bonding, GFCI protection and disconnect distance for a hot tub."),
    ),
    checks_intro="These are the checks the generator runs on your job and the notes it prints on the sheets.",
    checks=(
        "Service capacity: the computed load, with the appliance added, against your service.",
        "Panel spaces: two open breaker spaces for the 2-pole breaker.",
        "Breaker: for a heat pump or mini-split, between the nameplate MCA and the maximum breaker (NEC 440.22); for other appliances, sized for the load, continuous where it applies.",
        "Conductors sized at the 75°C or 60°C column, matching the equipment's terminal rating (NEC 110.14(C)), and a voltage drop check against 3%.",
        "Conduit fill at 40%, and trench cover for PVC (NEC 300.5).",
        "Hot tub GFCI protection (NEC 680.44): a GFCI breaker or a listed spa pack, and a failing check if none is chosen.",
        "Hot tub disconnect (NEC 680.13): it must be at least 5 ft from the spa, and the packet checks the distance you enter.",
        "Interrupting rating (NEC 110.9 and 110.10) and the panel schedule check (NEC 408.4).",
        "Sauna and heat pump notes: following the heater's instructions, including no receptacles in the sauna room.",
    ),
    steps=STEPS_COMMON,
    faqs=(
        ("Do I need a permit for a hot tub circuit?",
         "Most cities ask for an electrical permit for a new 240 V circuit, and some ask for plans. Confirm with your building department. The packet follows the published checklist where we have one.",
         "Most cities ask for one. See the hot tub page for what the packet covers."),
        ("Which 240V appliances does the packet cover?",
         "Hot tubs, saunas, heat pumps and mini-splits, plus an Other option where you enter the nameplate amps. Each uses the data that appliance needs, such as MCA and maximum breaker for a heat pump.",
         "Hot tubs, saunas, heat pumps, mini-splits and others."),
        ("What does the packet check for a hot tub?",
         "GFCI protection under NEC 680.44 and the disconnect distance under NEC 680.13, on top of the service, breaker, conductor and voltage drop checks every circuit gets.",
         "GFCI protection and the 5 ft disconnect distance."),
        ("How far must the disconnect be from the spa?",
         "At least 5 ft, as NEC 680.13 is checked in the packet. You enter your distance and the check passes or fails against it.",
         "At least 5 ft; the packet checks your distance."),
        ("How is a heat pump or mini-split breaker sized?",
         "From the nameplate. You enter the MCA and the maximum breaker (MOCP), and the packet checks the breaker falls between them (NEC 440.22).",
         "From the nameplate MCA and MOCP."),
        ("Can I use the packet for a sauna?",
         "Yes. You enter the heater size in kW, and the pre-submittal checklist reminds you to follow the heater instructions, including wire type and no receptacles in the room.",
         "Yes, using the heater's kW."),
    ),
))


# ---- Audience pages ----

@dataclass(frozen=True)
class Audience:
    slug: str
    role: str
    path: str
    h1: str
    crumb: str
    title: str
    description: str
    answer: str
    benefit: str  # the homepage card line
    cta_params: str
    tier_key: str
    sections: tuple[tuple[str, tuple[str, ...]], ...]  # H2 question, paragraphs
    steps: tuple[tuple[str, str], ...]
    tier_why: str
    faqs: tuple[tuple[str, str, str], ...]


AUDIENCES: dict[str, Audience] = {}


def _aud(a: Audience) -> None:
    AUDIENCES[a.slug] = a


_aud(Audience(
    slug="diy-homeowners", role="diy", path="/for/diy-homeowners/",
    h1="Electrical Permit Plans for DIY Homeowners", crumb="DIY Homeowners",
    title="Electrical Permit Plans for DIY Homeowners | Permit Packets",
    description="Pull your own electrical permit with the plans your city asks for: site plan, single-line diagram and load calc. Free watermarked preview.",
    benefit="Pull your own permit with the plans your city asks for",
    answer=("If you are doing electrical work on your own home, your city may let you pull an owner-builder permit, and "
            "the permit office will want plans. Permit Packets drafts the site plan, single-line diagram and load "
            "calculation from your address, prints your name as owner-builder, and previews it free."),
    cta_params="?role=diy", tier_key="instant_packet",
    sections=(
        ("Can a homeowner pull their own electrical permit?",
         ("Many cities allow an owner-builder permit for a home you live in, and the rules vary by city and state. Who may do the work depends on where you are. Confirm with {permits}.",
          "When you choose \"I'm a homeowner doing the work myself\" in the wizard, the packet prints your name as the owner-builder and no contractor license number.")),
        ("What does the packet print for an owner-builder?",
         ("Every drawing sheet carries a title block with the project address and parcel number. For an owner-builder it reads \"Prepared by\" with your name and \"(Owner-Builder)\", and it adds an owner signature line with a date line for you to sign.",
          "A packet for a contractor prints the contractor's name and license number in that spot instead.")),
        ("What plans will the permit office want?",
         ("It depends on the city and the job. Cities that publish a checklist commonly ask for a permit application, a site plan to scale, a single-line diagram and a load calculation. The first sheet of your packet lists your city's items and marks each one Ready, Open or Check.",
          "The sheets are the same ones described on each job page: <a href=\"/ev-charger-permit/\">EV charger</a>, <a href=\"/panel-upgrade-permit/\">panel upgrade</a>, <a href=\"/subpanel-permit/\">subpanel</a> and <a href=\"/hot-tub-240v-permit/\">hot tub and 240V circuit</a>.")),
        ("How do I submit an owner-builder permit packet?",
         ("You submit it yourself; Permit Packets does not file anything for you. After you pay, your order page gives you the clean PDF, the individual files, your city's submission steps and copy-paste fields for the permit form.",
          "Where a city asks for sheets uploaded separately, download the ZIP of individual files. Otherwise use the single PDF.")),
        ("What if my city does not allow owner-builder permits?",
         ("Then the permit has to be pulled by a licensed contractor, and the packet still helps: it gives them the site plan, diagram and load calculation to work from. See <a href=\"/for/homeowners-hiring-an-electrician/\">getting your plans ready before you hire an electrician</a>.",
          "Because the rules differ by city and state, check before you buy anything. The free preview costs nothing, so you can build the packet first and read the checklist on its first sheet.")),
        ("Which package should a DIY homeowner choose?",
         ("The $89 Instant Permit Packet. It is the complete clean packet and the individual files, and you can download it as soon as payment clears. If you want it checked against your city's published requirements first, the $169 package does that within 24 hours.",)),
    ),
    steps=(
        ("Choose \"I'm a homeowner doing the work myself\"", "Then enter the job address and pick the job."),
        ("Preview the free watermarked packet", "Check each sheet, then adjust anything that looks off."),
        ("Pay, download and submit", "Sign the owner line, then submit through your city's portal or office."),
    ),
    tier_why="The complete clean packet, ready to submit. It is the package most homeowners choose.",
    faqs=(
        ("Does the packet make my permit application for me?",
         "It prepares the plans and the fields for the city's form. You enter them and submit the application yourself.",
         "It prepares the plans and form fields. You submit."),
        ("Is the packet stamped by an engineer?",
         "No. It is an automated drafting and NEC calculation tool, so it is not PE-stamped. Some cities or jobs need a stamp or a licensed electrician's review.",
         "No. Some cities or jobs need a stamp or an electrician's review."),
        ("Will my permit be approved?",
         "We cannot promise approval. The packet follows the city's published checklist where we have one, and your building department decides.",
         "We cannot guarantee approval."),
        ("What if my city is not one with a built-in checklist?",
         "Any U.S. address works. Elsewhere the packet uses a general NEC checklist and says so, and you confirm local requirements with your building department.",
         "A general NEC checklist is used and labeled."),
        ("Can I change something after the preview?",
         "Yes. The preview is free and you can go back, edit your answers and preview again before you pay.",
         "Yes, edit and preview again before paying."),
    ),
))

_aud(Audience(
    slug="homeowners-hiring-an-electrician", role="hiring", path="/for/homeowners-hiring-an-electrician/",
    h1="Get Your Permit Plans Ready Before You Hire an Electrician", crumb="Hiring an Electrician",
    title="Permit Plans Before You Hire an Electrician | Permit Packets",
    description="Know your panel capacity before you get quotes. Run the NEC 220 load calc for $39, then hand the packet to your electrician.",
    benefit="Know your panel capacity before you get quotes",
    answer=("Before you hire an electrician, find out whether your panel has room for the job. Permit Packets runs the "
            "NEC Article 220 load calculation from your address and home details, so every quote starts from the same "
            "numbers, and you can hand the finished packet to the electrician you choose."),
    cta_params="?role=hiring&tier=39", tier_key="load_calc",
    sections=(
        ("Why check my panel capacity before getting quotes?",
         ("A panel that is near its limit can change the job: it may need a service upgrade before a charger or a hot tub can go in. The load calculation shows the computed load against your service rating, with a pass or fail.",
          "The sample packet's load calculation, for instance, shows 162.3 A computed on a 200 A service. You see the same kind of result before anyone quotes.")),
        ("How do I compare electrician quotes fairly?",
         ("Give each electrician the same scope: the job, the panel and equipment locations, the run length and the service size. The packet sets these out on the site plan, single-line diagram and load calculation, so quotes answer the same question.",
          "If one quote includes a service upgrade and another does not, the load calculation shows which assumption the numbers support.")),
        ("How do I hand the packet to my electrician?",
         ("Your order page has a \"Send to your electrician\" button. It opens an email in your mail program with your order link ready to send, so the electrician can download the packet.",
          "Choose \"I'm a homeowner hiring an electrician\" in the wizard and the packet prints you as the owner. Who may pull the permit depends on your city and state; confirm with {permits}.")),
        ("What should I ask each electrician?",
         ("Ask whether the quote includes a service upgrade, who pulls the permit and who submits it. Put your load calculation next to each answer: if your service already has spare capacity, an upgrade line on a quote is worth a question.",
          "The packet's first sheet also lists items flagged for review, such as existing loads and open panel spaces. Share those with the electrician so they can field verify them.")),
        ("Which package should I start with?",
         ("Start with the $39 Load Calc & Panel Audit. It delivers the load calculation sheet and the panel schedule and capacity audit sheet, which is what you need to compare quotes.",
          "When you are ready for the plans, choose the $89 Instant Permit Packet for the complete clean packet. Your preview is free either way.")),
    ),
    steps=(
        ("Choose \"I'm a homeowner hiring an electrician\"", "Enter the address and the job you are considering."),
        ("Preview the load calc free", "See your panel's computed load against its rating before you spend anything."),
        ("Pay, then send it to your electrician", "Use the Send to your electrician button on your order page."),
    ),
    tier_why="Just the load calculation and panel capacity audit, so you know your numbers before the quotes come in.",
    faqs=(
        ("What do I get for $39?",
         "The NEC 220 load calculation sheet and the panel schedule and capacity audit sheet. The full plans are in the $89 packet.",
         "The load calc sheet and the panel capacity audit sheet."),
        ("Can I upgrade from $39 to the full packet later?",
         "You can run the wizard again and choose a larger package.",
         "Run the wizard again and choose a larger package."),
        ("Do I still need an electrician?",
         "That depends on the job, your city and your state. Confirm who may do the work with {permits}.",
         "It depends on the city and state."),
        ("Will the electrician accept my packet?",
         "Ask them. The packet is a drafting and NEC calculation tool, not a stamped document, and an electrician may want to review or change it.",
         "Ask them; they may want to review it."),
        ("Is my panel's load calculation exact?",
         "It uses the home's size and the appliances you enter, on the NEC Article 220 method. Field verify the existing loads, since they drive the result.",
         "It follows your inputs. Field verify the existing loads."),
    ),
))

_aud(Audience(
    slug="electricians", role="electrician", path="/for/electricians/",
    h1="Permit Packets for Electricians: Plans, Load Calcs & Single-Line Diagrams", crumb="Electricians",
    title="Permit Packets for Electricians | Permit Packets",
    description="Hand off permit drafting: site plan, single-line diagram and NEC 220 load calc with your license number in the title block.",
    benefit="Hand off the permit paperwork on every job",
    answer=("Permit Packets drafts the permit paperwork for your residential jobs: the site plan on parcel aerial, "
            "single-line or riser diagram, NEC Article 220 load calculation and panel schedule, with your license "
            "number in the title block. A packet is typically generated in under 5 minutes."),
    cta_params="?role=electrician", tier_key="instant_packet",
    sections=(
        ("Can I hand off permit drafting to Permit Packets?",
         ("Yes. You enter the address, the equipment and the run, tap the panel and equipment on the aerial map, and the tool draws the site plan, diagram and schedules and runs the NEC Article 220 calculation.",
          "A packet is typically generated in under 5 minutes, compared with 3–7 business days and $300–$500+ for a CAD drafter.")),
        ("What shows in the title block?",
         ("Choose \"I'm an electrician\" and enter your name and license number. Both print in the title block of every drawing sheet, with the project address and parcel number.",
          "Owner-builder packets print the owner and a signature line instead.")),
        ("Which jobs does it cover?",
         ("<a href=\"/ev-charger-permit/\">EV chargers</a>, <a href=\"/panel-upgrade-permit/\">panel and service upgrades</a>, <a href=\"/subpanel-permit/\">subpanels</a> and <a href=\"/hot-tub-240v-permit/\">hot tub and 240V circuits</a>. Each packet follows the city's published checklist where we have one and a general NEC checklist elsewhere.",)),
        ("What does the load calculation cover?",
         ("The NEC Article 220 calculation runs on every job, with the sizing checks that go with it: service capacity, open panel spaces, breaker and conductor sizes and voltage drop. The first sheet shows each check with a result and a status of Pass, Fix or Note.",
          "Cities we have set up use their published checklist; any other address uses a general NEC checklist that the packet labels. Check each job page for the details: <a href=\"/panel-upgrade-permit/\">panel upgrade</a> and <a href=\"/subpanel-permit/\">subpanel</a> add a riser diagram or a feeder schedule.")),
        ("What if I want a second check before I submit?",
         ("The $169 24-Hour City-Checked Packet adds a check against your city's published requirements. It is reviewed and released within 24 hours of payment, and you get an email when it is released.",
          "The $89 Instant Permit Packet is available to download as soon as payment clears.")),
        ("How do I upload to a city portal?",
         ("You get one combined PDF, or a ZIP of each sheet as its own file for portals that want separate uploads. Your order page also lists the city's submission steps and copy-paste fields for the portal.",
          "You submit to the city yourself. The packet is not PE-stamped, and approval is not guaranteed.")),
    ),
    steps=(
        ("Choose \"I'm an electrician\"", "Enter your name, license number and the job address."),
        ("Preview free", "Check every sheet and the live NEC check, then adjust."),
        ("Pay, download, submit", "Take the PDF or the split ZIP to the city's portal."),
    ),
    tier_why="The complete clean packet with your license in the title block, ready as soon as payment clears.",
    faqs=(
        ("Is the packet PE-stamped?",
         "No. It is an automated drafting and NEC calculation tool. Some cities or jobs need a stamp, and you remain responsible for confirming the city's requirements.",
         "No. Confirm whether the city needs a stamp."),
        ("Can I customize the packet?",
         "You control the inputs: equipment, run, service size, existing loads and your contractor details. The sheets are generated from them, so edit the inputs and preview again.",
         "You edit the inputs, not the drawings."),
        ("Does it work in my city?",
         "Any U.S. address works. Cities we have set up use their published checklist; everywhere else uses a general checklist, so confirm local requirements.",
         "Any address; built-in checklists for set-up cities."),
        ("Do I pay per job?",
         "Yes. Each packet is one purchase at $39, $89 or $169, and the preview is free.",
         "Yes, per packet."),
        ("Does the $169 package guarantee approval?",
         "No. It adds a check against your city's published requirements. The building department makes the decision.",
         "No. It adds a requirements check."),
    ),
))

_aud(Audience(
    slug="contractors", role="contractor", path="/for/contractors/",
    h1="Electrical Permit Plans for Contractors & Handymen", crumb="Contractors",
    title="Electrical Permit Plans for Contractors | Permit Packets",
    description="Prepare the electrical scope permit-ready for your licensed electrician: site plan, single-line diagram and load calc, free to preview.",
    benefit="Get the electrical scope permit-ready for your licensed partner",
    answer=("If you run a remodel, handyman or general contracting job that includes electrical work, Permit Packets "
            "can prepare the electrical scope as plans: site plan, single-line diagram and NEC Article 220 load "
            "calculation. Your licensed electrician reviews it, signs and pulls the permit."),
    cta_params="?role=contractor", tier_key="instant_packet",
    sections=(
        ("Who pulls the electrical permit on a contractor's job?",
         ("Who may do electrical work and pull the permit depends on your city and state, and on your license. In many places that is a licensed electrician. Confirm with {permits}.",
          "Permit Packets does not file anything, and it cannot replace the licensed electrician where one is required.")),
        ("How does the packet help me prepare the scope?",
         ("You enter the address, the equipment and the run. The packet draws the site plan on parcel aerial, the single-line or riser diagram, the load calculation and the panel schedule, so the electrician receives a defined scope.",
          "The first sheet lists the city's checklist items with a status, so open items are visible before anyone submits.")),
        ("What do I give the licensed electrician?",
         ("The clean PDF and the individual files from your order page. The electrician can review the numbers, change the inputs and enter their license number and name for the title block.",
          "If you want the electrician to enter their own details, they can choose \"I'm an electrician\" and run the wizard themselves.")),
        ("What does the licensed electrician still do?",
         ("The electrician reviews the plans against the job, field verifies the existing panel and loads, and signs and pulls the permit where the rules call for a licensed electrician. The packet marks what needs that check: existing loads, open panel spaces, the trench route and the code edition.",
          "It is a drafting and NEC calculation tool. It is not PE-stamped, and it does not replace anyone's review.")),
        ("Why prepare the scope before the electrician arrives?",
         ("The panel and equipment locations, the measured run, the service size and the load calculation are on one set of sheets, so the electrician starts from a defined scope rather than a description.",
          "A CAD drafter costs $300–$500+ and takes 3–7 business days. A packet is $89 and typically generated in under 5 minutes.")),
        ("Which package should a contractor choose?",
         ("The $89 Instant Permit Packet, the complete clean packet. Start with the $39 Load Calc & Panel Audit if you only need to confirm the panel can take the job.",)),
    ),
    steps=(
        ("Choose \"I'm a contractor or handyman\"", "Enter the address and the job's equipment and run."),
        ("Preview free", "Check the scope on each sheet and the live NEC check."),
        ("Pay and hand off", "Send the packet to the licensed electrician who signs and pulls the permit."),
    ),
    tier_why="The complete clean packet, so the licensed electrician starts from defined plans.",
    faqs=(
        ("Can a handyman pull an electrical permit?",
         "That depends on your city and state. Confirm with {permits}.",
         "It depends on the city and state."),
        ("Does the packet replace the electrician's review?",
         "No. It is a drafting and NEC calculation tool, not a stamped document, and the licensed electrician reviews the work.",
         "No. The electrician reviews it."),
        ("What goes in the contractor title block?",
         "The contractor name and license number you enter. If you do not hold the license, enter the electrician's details, or have them run the wizard.",
         "The name and license number you enter."),
        ("Which jobs can I prepare?",
         "EV chargers, panel upgrades, subpanels and hot tub or 240V circuits, each with its own sheets.",
         "The four job types."),
        ("Is there a free way to look first?",
         "Yes. Every packet has a free watermarked preview, and the sample packet shows a finished one.",
         "Yes, a free watermarked preview."),
    ),
))


# ---- Sample packet ----

SAMPLE_SHEETS = (
    ("01-cover", "E-1", "Checklist and Checks", "1000 x 1294", (
        "The city's checklist with the sample's items marked Ready, Open or Check.",
        "Engineering checks with a result and a status: service capacity (162.3 A on a 200 A service), panel spaces, circuit, conductors and voltage drop.",
        "A \"Flagged for your review\" list of items to confirm, including the city's disconnect and trench notes.",
        "The owner-builder title block with a signature line.")),
    ("02-site-plan", "E-3", "Site Plan", "", (
        "Lot lines from San Diego County GIS over the County of San Diego aerial, with each lot line dimensioned.",
        "The main panel (P), the new charger (EV) and the new disconnect (D) marked, with the 21 ft measured route.",
        "A north arrow and a scale bar at 1 in = 30 ft, with the note that it is not a survey.",
        "A legend with the wire run with rises (31 ft) and the charger's distance to the nearest lot line.")),
    ("03-single-line", "E-4", "Single-Line Diagram", "", (
        "Utility meter, main panel, disconnect and EV charger drawn in line, with the new 60 A 2-pole breaker.",
        "A conductor and conduit schedule for the underground and above-ground runs.",
        "A fault-current and panel data box, and a code note for a hardwired charger.",
        "A trench detail with the minimum cover.")),
    ("04-load-calc", "E-5", "Load Calculation", "", (
        "General lighting, small appliance and laundry circuits and the appliances, each with its basis and VA.",
        "The optional dwelling method with the first 10,000 VA at 100% and the remainder at 40%.",
        "The EV charger added at 48 A x 240 V, 100% (11,520 VA).",
        "A computed load of 162.3 A against the 200 A service, with 37.7 A of spare capacity.")),
    ("05-spec-sheet", "", "Manufacturer Data Sheet (Product Overview)", "", (
        "The charger manufacturer's own data sheet, attached behind the Equipment Data sheet.",
        "Voltage, current output range, terminal and conduit sizes, enclosure rating and agency approvals.")),
)


# ---- About and pricing ----

PRICING_FAQS = (
    ("How much does a permit packet cost?",
     "There are three packages: $39 for the Load Calc & Panel Audit, $89 for the Instant Permit Packet and $169 for the 24-Hour City-Checked Packet. The preview is free.",
     "$39, $89 or $169. The preview is free."),
    ("What does the free preview include?",
     "Every sheet of your exact packet, watermarked, and the live NEC check. You pay only to download the clean version.",
     "Every sheet, watermarked."),
    ("What is the difference between the $89 and $169 packages?",
     "Both are the complete packet. The $169 package is also checked against your city's published requirements, then reviewed and released within 24 hours of payment.",
     "$169 adds a city-requirements check, released within 24 hours."),
    ("When can I download?",
     "Your order unlocks automatically once the payment goes through, and the $89 packet is available to download as soon as payment clears. The $169 order is held for the city-requirements review, and you get an email when it is released.",
     "On payment for $39 and $89; $169 after review."),
    ("Who processes the payment?",
     "Whop. Payments are processed securely by Whop, and we do not see or store your card details.",
     "Whop, securely."),
    ("What is the refund policy?",
     'You can get a full refund if you ask before downloading your clean packet. $169 orders can be refunded any time before release. Read the <a href="/refund/">Refund Policy</a>.',
     "Full refund before you download the clean packet."),
)

ABOUT_STEPS = (
    ("Your address", "You enter the job address and pick the job."),
    ("County GIS parcel and aerial", "The packet pulls the parcel and imagery for that address from county GIS and public map services, where available."),
    ("Your inputs", "You tap the panel and equipment on the aerial and answer questions about the home and the equipment."),
    ("NEC Article 220 load calculation", "The load calculation and the sizing checks run on your inputs."),
    ("Drawn sheets", "The site plan, diagram, schedules and calculation sheets are drawn and combined into one PDF, or a ZIP of individual files."),
)
