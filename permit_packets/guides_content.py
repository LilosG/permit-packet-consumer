"""Evergreen guides, A-vs-B comparisons, Best-Of listicles, regional roundups and DIY checklists."""
from __future__ import annotations
from dataclasses import dataclass

GUIDES_PATH = "/guides/"
GUIDES_TITLE = "Electrical Permit Guides, Comparisons & DIY Checklists"
GUIDES_DESCRIPTION = "In-depth guides for residential electrical permits: EV charger wiring, 200A panel upgrades, subpanel feeders, equipment comparisons and NEC checklists."
GUIDES_INTRO = "Practical guides, side-by-side comparisons, UL-listed equipment roundups and NEC code checklists for homeowners and electricians preparing residential electrical permit plans."

CATEGORIES: dict[str, tuple[str, str]] = {
    "comparisons": ("A vs B Comparisons", "Side-by-side NEC, cost and permit comparisons to help you pick the right electrical setup."),
    "best-of": ("Best Equipment & Hardware", "UL-listed EV chargers, meter-main combo panels and load management hardware with verified specs."),
    "local-guides": ("City & Utility Guides", "Owner-builder eligibility, utility meter-main lists and adopted NEC code editions by area."),
    "diy-tips": ("DIY Tips & Checklists", "Step-by-step panel audits, trench depth tables and plan-check checklists to pass inspection."),
}

@dataclass(frozen=True)
class Guide:
    slug: str; category: str; job: str; role: str; h1: str; crumb: str; title: str; description: str; answer: str; card: str
    table_caption: str = ""; table_headers: tuple[str, ...] = (); table_rows: tuple[tuple[str, ...], ...] = ()
    sections: tuple[tuple[str, tuple[str, ...]], ...] = (); listicle_items: tuple[str, ...] = ()
    tool_links: tuple[str, ...] = (); doc_links: tuple[str, ...] = (); related_slugs: tuple[str, ...] = ()
    faqs: tuple[tuple[str, str], ...] = ()

GUIDES: dict[str, Guide] = {}

GUIDES["hardwired-vs-plug-in-ev-charger-permit"] = Guide(
    slug="hardwired-vs-plug-in-ev-charger-permit", category="comparisons", job="ev-charger", role="diy",
    crumb="Hardwired vs Plug-In EV Charger", h1="Hardwired vs. Plug-In EV Charger: NEC & Permit Rules",
    title="Hardwired vs Plug-In EV Charger: NEC & Permit Rules",
    description="Compare hardwired vs NEMA 14-50 plug-in EV chargers for permits: NEC 625.54 GFCI breaker rules, 48A vs 40A charging speed, and costs.",
    answer="Hardwired EV chargers connect directly to a dedicated 240V breaker without a receptacle, supporting up to 48A continuous output on a 60A circuit without triggering NEC 625.54 receptacle GFCI nuisance trips. Plug-in chargers cap at 40A on a 50A NEMA 14-50 outlet and require a GFCI breaker plus an industrial-grade receptacle.",
    card="Compare 48A hardwired circuits against 40A NEMA 14-50 outlets under NEC 625.",
    table_caption="Hardwired vs. NEMA 14-50 Plug-In EV Charger Comparison",
    table_headers=("Feature", "Hardwired EV Charger", "Plug-In (NEMA 14-50)"),
    table_rows=(
        ("Max output", "48 A (11.5 kW) on 60 A breaker", "40 A (9.6 kW) on 50 A breaker (NEC 210.21(B))"),
        ("GFCI breaker", "Not required indoors (UL 2594 CCID)", "Mandatory under NEC 625.54 for EV receptacles"),
        ("Wire & conduit", "#6 AWG Cu THWN-2 in 3/4 in EMT/PVC", "#6 AWG Cu with neutral (3 conductors + ground)"),
    ),
    sections=(
        ("Why city plan reviewers prefer hardwired EV chargers", (
            "Under NEC 625.41, Level 2 EV chargers are continuous loads sized at 125% of maximum current. A 48 A charger requires a 60 A circuit, exceeding the 50 A limit of a residential receptacle—so NEC 625.44 requires chargers above 40 A to be hardwired. Hardwiring eliminates the outlet and saves a 50 A GFCI breaker. Check wire sizes with our <a href=\"/tools/ev-charger-wire-breaker-size/\">EV charger wire calculator</a>.",
        )),
        ("When a NEMA 14-50 plug-in outlet makes sense", (
            "A plug-in outlet fits portable cord-and-plug chargers or renters moving soon. Your <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a> must show a 50 A 2-pole GFCI breaker (NEC 625.54), neutral wire, and heavy-duty receptacle. Build your <a href=\"/ev-charger-permit/\">EV charger permit packet</a> for either setup.",
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size", "ev-charger-load-calculator"),
    doc_links=("single-line-diagram", "equipment-cut-sheets"),
    related_slugs=("best-48a-hardwired-ev-chargers-for-permits", "how-to-check-if-panel-can-handle-ev-charger"),
    faqs=(
        ("Can I put a 48A EV charger on a NEMA 14-50 plug?", "No. Under NEC 625.41, a 48 A continuous load requires a 60 A breaker (48 A x 125%), and NEMA 14-50 receptacles max out at 50 A."),
        ("Does a hardwired EV charger need a GFCI breaker?", "Under the 2020 and 2023 NEC, indoor hardwired UL 2594 chargers do not need a separate GFCI breaker because ground-fault protection is built in."),
        ("Does a hardwired EV charger need a neutral wire?", "No. Hardwired 240 V chargers use two hot conductors and an equipment ground, saving a neutral conductor."),
    ),
)

GUIDES["subpanel-vs-200a-panel-upgrade"] = Guide(
    slug="subpanel-vs-200a-panel-upgrade", category="comparisons", job="panel-upgrade", role="hiring",
    crumb="Subpanel vs 200A Panel Upgrade", h1="Subpanel vs. 200A Panel Upgrade: Cost & Load Calc Guide",
    title="Subpanel vs 200A Panel Upgrade: Cost & Load Calc Guide",
    description="Should you add a subpanel or upgrade to a 200A main service? Compare NEC 220 load calculations, utility rules, equipment costs and permits.",
    answer="Adding a subpanel creates new breaker spaces fed from your existing main service, making it ideal when your panel is physically full but has spare ampacity. Upgrading to a 200A service increases total home capacity when an NEC 220.82 load calculation shows your existing 100A or 125A service is overloaded.",
    card="Know whether you need extra breaker spaces (subpanel) or more total amperage (service upgrade).",
    table_caption="Subpanel Addition vs. 200A Main Service Upgrade",
    table_headers=("Factor", "Add a Subpanel", "200A Main Service Upgrade"),
    table_rows=(
        ("Problem solved", "Main panel out of physical breaker slots", "Total household load exceeds 100A or 125A service"),
        ("Utility shutoff", "Not required (fed from main panel breaker)", "Required (utility disconnects service drop/lateral)"),
        ("Surge protection", "Not triggered by subpanel addition alone", "Mandatory Type 1/2 SPD under NEC 230.67"),
    ),
    sections=(
        ("Step 1: Separate physical breaker space from electrical capacity", (
            'Many 150 A and 200 A panels run out of slots while still having 50 A to 80 A of spare capacity. Run your home through our <a href="/tools/residential-load-calculator/">NEC 220.82 residential load calculator</a> first—if total demand fits your main breaker, a <a href="/subpanel-permit/">subpanel permit</a> solves the bottleneck without touching the utility meter.',
        )),
        ("When a 200A service upgrade is unavoidable", (
            'Homes with a 60 A or 100 A service or an FPE/Zinsco panel usually exceed capacity when adding an EV charger or heat pump. A <a href="/panel-upgrade-permit/">200A panel upgrade permit</a> sizes conductors under NEC 310.12 (83% rule) and adds NEC 230.85 disconnects and NEC 230.67 surge protection. Size feeder wire with our <a href="/tools/subpanel-feeder-calculator/">subpanel feeder calculator</a>.',
        )),
    ),
    tool_links=("residential-load-calculator", "subpanel-feeder-calculator"),
    doc_links=("load-calculation", "single-line-diagram"),
    related_slugs=("nec-220-82-vs-220-87-load-calculation", "best-200a-meter-main-combo-panels"),
    faqs=(
        ("Does adding a 100A subpanel give my house 100A more power?", "No. A 100 A subpanel draws from your existing main service; total load stays capped by your main breaker."),
        ("Can I install a subpanel in a detached garage?", "Yes. A 60 A or 100 A feeder to a detached garage requires ground rods (NEC 250.32) and isolated neutral and ground bars."),
        ("Do I need utility approval for a subpanel?", "Usually no, because the meter and utility service conductors are untouched."),
    ),
)

GUIDES["nec-220-82-vs-220-87-load-calculation"] = Guide(
    slug="nec-220-82-vs-220-87-load-calculation", category="comparisons", job="ev-charger", role="diy",
    crumb="NEC 220.82 vs 220.87 Load Calc", h1="NEC 220.82 vs. 220.87 Load Calculation: Avoid Panel Upgrades",
    title="NEC 220.82 vs 220.87 Load Calculation: Avoid Panel Upgrades",
    description="Learn how NEC 220.82 optional load calculations compare with NEC 220.87 12-month utility peak demand data to qualify an EV charger without upgrading.",
    answer="NEC 220.82 estimates dwelling electrical demand from square footage and appliance nameplates, which often overstates real usage on 100A and 150A panels. NEC 220.87 lets you substitute 12 months of actual utility peak demand multiplied by 125%, frequently proving your existing panel can carry an EV charger without a service upgrade.",
    card="How 12-month utility peak demand data (NEC 220.87) qualifies EV chargers on 100A panels.",
    table_caption="NEC 220.82 Nameplate Calculation vs. NEC 220.87 Measured Demand",
    table_headers=("Criteria", "NEC 220.82 (Optional Dwelling)", "NEC 220.87 (Existing Load Determination)"),
    table_rows=(
        ("Data source", "Square footage (3 VA/sq ft) + appliance nameplates", "12 months utility smart-meter peak kW (or 30-day logger)"),
        ("Demand math", "First 10,000 VA at 100%, remainder at 40% + HVAC", "Peak existing demand x 125% + 100% of new load"),
        ("Best suited for", "200A services or homes with gas appliances", "100A / 125A / 150A panels that fail nameplate math"),
        ("Turnaround time", "Instant from home square footage and nameplates", "1 to 5 days to download utility interval data"),
    ),
    sections=(
        ("How NEC 220.82 calculates your existing home load", (
            'NEC 220.82 sums 3 VA per square foot of living space, two 1,500 VA small-appliance circuits, one 1,500 VA laundry circuit, and fixed electric appliances—counting the first 10,000 VA at 100% and the rest at 40%, plus the larger of heating or cooling. Test your home right now with our <a href="/tools/ev-charger-load-calculator/">EV charger load calculator</a> to see your exact computed amps.',
        )),
        ("How NEC 220.87 saves 100A homeowners thousands of dollars", (
            'In real homes, you never run your range, dryer, water heater, and air conditioner at full nameplate simultaneously. On a 100 A service, NEC 220.82 nameplate math frequently exceeds capacity. NEC 220.87 lets you pull 12 months of 15-minute peak kW demand from your electric utility, multiply that peak by 125%, and add your new charger. Generate an NEC 220.87 <a href="/permit-documents/load-calculation/">load calculation sheet</a> inside your <a href="/ev-charger-permit/">EV charger permit packet</a>.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "residential-load-calculator"),
    doc_links=("load-calculation", "panel-schedule"),
    related_slugs=("best-ev-load-management-devices-100a-panel", "how-to-check-if-panel-can-handle-ev-charger"),
    faqs=(
        ("Where do I get 12-month peak demand data for NEC 220.87?", "Log into your electric utility online portal to download 12-month interval usage data or request a maximum demand letter."),
        ("What if I don't have 12 months of utility data?", "NEC 220.87 also permits a licensed electrician to attach a continuous recording ammeter for 30 days and multiply the peak by 125%."),
        ("Can I use NEC 220.87 if I have solar panels?", "If net-metered solar masks daytime peaks on your utility meter, reviewers may require clamp-on load logging or an NEC 625.42 load controller."),
    ),
)

GUIDES["owner-builder-permit-vs-licensed-electrician"] = Guide(
    slug="owner-builder-permit-vs-licensed-electrician", category="comparisons", job="ev-charger", role="diy",
    crumb="Owner-Builder vs Electrician", h1="Owner-Builder Electrical Permit vs. Hiring an Electrician",
    title="Owner-Builder Electrical Permit vs Hiring an Electrician",
    description="Compare pulling an owner-builder electrical permit vs hiring a licensed electrician: city eligibility rules, title blocks, inspections and costs.",
    answer="An owner-builder electrical permit lets a homeowner pull the permit and perform or manage work on their primary residence where local rules allow it. Hiring a licensed electrician shifts code compliance, panel tie-in, and inspection sign-off to a bonded contractor, which cities like San Francisco and Nashville strictly require.",
    card="Understand owner-builder rights, title-block requirements and inspection liability.",
    table_caption="Owner-Builder Permit vs. Licensed Electrical Contractor",
    table_headers=("Aspect", "Owner-Builder Permit", "Licensed Electrical Contractor"),
    table_rows=(
        ("Who pulls permit", "Homeowner occupying single-family residence", "State-licensed electrical contractor (C-10 / Master)"),
        ("Title block", "Owner name + '(Owner-Builder)' + signature line", "Company name + contractor license number"),
        ("City eligibility", "Allowed in El Cajon, Chandler, Mesa, Bellevue, Charlotte", "Required in San Francisco, Nashville & multi-family"),
        ("Typical labor cost", "$0 labor (materials + permit fee + $89 plans)", "$800-$2,500+ for EV circuit; $3,500-$6,000+ for 200A upgrade"),
        ("Inspection sign-off", "Homeowner meets inspector and fixes corrections", "Contractor handles rough-in, final sign-off & warranty"),
    ),
    sections=(
        ("How owner-builder electrical permits work", (
            'Under state owner-builder laws, homeowners may act as their own general contractor on a single-family home they live in, provided they do not sell the home immediately after completion.',
            'In California, Arizona, Washington, and North Carolina, homeowners living in a detached single-family house generally qualify for an owner-builder exemption. Selecting DIY in Permit Packets prints your name with "(Owner-Builder)" and a signature line on every sheet. Read our <a href="/for/diy-homeowners/">DIY homeowner permit plans guide</a> to see how owner-builder packets are formatted.',
        )),
        ("When you must hire a licensed electrician", (
            'Working inside a live main service panel carries serious arc-flash hazards, and cities like <a href="/permits/ca/san-francisco/">San Francisco</a> and <a href="/permits/tn/nashville/">Metro Nashville</a> restrict electrical permits strictly to licensed contractors. Even in contractor-only cities, you can run our $39 load calc first via our <a href="/for/homeowners-hiring-an-electrician/">quote-prep workflow</a> so every bid starts from verified numbers.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "residential-load-calculator"),
    doc_links=("site-plan", "panel-schedule"),
    related_slugs=("cities-allowing-owner-builder-ev-charger-permits", "7-reasons-electrical-permits-fail-plan-check"),
    faqs=(
        ("Can I pull an owner-builder permit for a rental property?", "Usually no; owner-builder permits are typically limited to an owner-occupied primary residence."),
        ("Can I pull an owner-builder permit and hire an unlicensed handyman?", "No. Under state owner-builder declarations, you must do the work yourself or hire a properly licensed contractor."),
        ("Do electricians accept homeowner-generated permit plans?", "Yes—many solo electricians prefer starting from a complete site plan, single-line diagram, and load calc."),
    ),
)

GUIDES["best-48a-hardwired-ev-chargers-for-permits"] = Guide(
    slug="best-48a-hardwired-ev-chargers-for-permits", category="best-of", job="ev-charger", role="diy",
    crumb="Best 48A EV Chargers for Permits", h1="Best 48A Hardwired Level 2 EV Chargers for Permits (2026)",
    title="Best 48A Hardwired Level 2 EV Chargers for Permits (2026)",
    description="Compare top UL-listed 48A hardwired EV chargers for residential permits: Tesla Gen 3, ChargePoint Home Flex, Emporia and Wallbox Pulsar Plus.",
    answer="The best 48A hardwired Level 2 EV chargers carry full UL 2594 and UL 2231 listings, 75°C-rated wire terminals, and published manufacturer cut sheets required by city plan reviewers. Top permit-ready models include the Tesla Wall Connector Gen 3, Tesla Universal Wall Connector, ChargePoint Home Flex, Emporia, and Wallbox Pulsar Plus.",
    card="Top 5 UL-listed 48A hardwired chargers whose official manufacturer cut sheets are pre-loaded in our tool.",
    table_caption="Permit-Ready 48A Hardwired Level 2 EV Chargers (Pre-Loaded UL Cut Sheets)",
    table_headers=("Charger Model", "Max Output", "Breaker", "UL / NRTL Listing"),
    table_rows=(
        ("Tesla Wall Connector (Gen 3)", "48 A (11.5 kW)", "60 A 2-pole", "cULus E351001, UL 2594"),
        ("Tesla Universal Wall Connector", "48 A (11.5 kW)", "60 A 2-pole", "cULus E351001, UL 2594, UL 2231"),
        ("ChargePoint Home Flex (CPH50)", "50 A (48 A typical)", "60 A / 70 A", "UL & cUL listed, UL 2594, UL 2231"),
        ("Emporia Level 2 EV Charger", "48 A (11.5 kW)", "60 A 2-pole", "UL listed, UL 2594"),
        ("Wallbox Pulsar Plus (48A NA)", "48 A (11.5 kW)", "60 A 2-pole", "UL 2594, UL 2231 (NRTL)"),
    ),
    listicle_items=(
        "Tesla Wall Connector (Gen 3) — 48 A hardwired, cULus E351001 / UL 2594",
        "Tesla Universal Wall Connector — 48 A hardwired with integrated J1772 adapter, UL 2594 & UL 2231",
        "ChargePoint Home Flex (CPH50) — Configurable 16 A to 50 A output, UL 2594 & UL 2231",
        "Emporia Level 2 EV Charger — 48 A hardwired with optional Vue load management, UL 2594",
        "Wallbox Pulsar Plus (North America) — Compact 48 A NEMA 4 indoor/outdoor enclosure, UL 2594",
    ),
    sections=(
        ("Why UL listings and cut sheets matter for city plan review", (
            'City checklists in <a href="/permits/ca/el-cajon/ev-charger/">El Cajon</a>, <a href="/permits/wa/bellevue/ev-charger/">Bellevue</a>, and <a href="/permits/az/chandler/ev-charger/">Chandler</a> require the manufacturer specification sheet showing the UL 2594 listing mark. Selecting any of these five chargers in Permit Packets bundles the official PDF <a href="/permit-documents/equipment-cut-sheets/">equipment cut sheet</a> automatically.',
        )),
        ("Choosing between Tesla Gen 3, Universal, ChargePoint, Emporia & Wallbox", (
            'All five models feature NEMA 3R or NEMA 4 outdoor enclosures, 75°C terminals for #6 AWG copper THWN-2 wire, and adjustable current limits if your <a href="/tools/ev-charger-load-calculator/">NEC 220.82 load calculation</a> requires derating to 32 A or 40 A.',
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size", "ev-charger-load-calculator"),
    doc_links=("equipment-cut-sheets", "single-line-diagram"),
    related_slugs=("hardwired-vs-plug-in-ev-charger-permit", "best-ev-load-management-devices-100a-panel"),
    faqs=(
        ("What wire size is required for a 48A EV charger?", "A 48 A continuous charger requires a 60 A 2-pole breaker and #6 AWG copper THWN-2 conductors with a #10 AWG copper ground."),
        ("Can I derate a 48A charger to 32A if my panel is near capacity?", "Yes. All five listed chargers can be commissioned at 32 A (40 A breaker) or 40 A (50 A breaker)."),
        ("Are these chargers rated for outdoor installation?", "Yes. All five carry NEMA 3R or NEMA 4 outdoor weatherproof ratings."),
    ),
)

GUIDES["best-200a-meter-main-combo-panels"] = Guide(
    slug="best-200a-meter-main-combo-panels", category="best-of", job="panel-upgrade", role="electrician",
    crumb="Best 200A Meter-Main Panels", h1="Best 200A Meter-Main Combo Panels for Service Upgrades",
    title="Best 200A Meter-Main Combo Panels for Service Upgrades",
    description="Compare top UL-listed 200A meter-main combo panels and load centers: Milbank U5168-XTL-200 and Square D Homeline SC816D200C & HOM3060M200PC.",
    answer="The best 200A meter-main combo panels combine a utility-approved meter socket, a 200A service disconnect, and feed-through lugs or branch spaces in one NEMA 3R outdoor enclosure. Popular permit-ready models include the Milbank U5168-XTL-200, Square D Homeline SC816D200C ringed meter-main, and Square D HOM3060M200PC load center.",
    card="Compare Milbank and Square D Homeline 200A panels & meter-mains with pre-loaded UL spec sheets.",
    table_caption="200A Service Upgrade Panels & Meter-Mains in Our UL Cut-Sheet Library",
    table_headers=("Model Number", "Type & Enclosure", "Bus / Main", "UL Listing"),
    table_rows=(
        ("Milbank U5168-XTL-200", "Meter-main combo (NEMA 3R)", "200 A bus / 200 A main", "UL listed, Type 3R"),
        ("Square D Homeline SC816D200C", "Ringed meter-main (NEMA 3R)", "200 A bus / 200 A main", "UL E-6294 (PSE approved)"),
        ("Square D Homeline HOM3060M200PC", "Main breaker load center (NEMA 1)", "225 A bus / 200 A main", "UL E-6294 (UL 67)"),
        ("Square D Homeline HOM3060L225PGC", "Main lug subpanel (NEMA 1)", "225 A bus / Main lug", "UL E-6294 (UL 67)"),
    ),
    listicle_items=(
        "Milbank U5168-XTL-200 — 200 A NEMA 3R meter-main combo with 8 branch circuits and feed-through lugs",
        "Square D Homeline SC816D200C — 200 A ringed meter-main combo approved on Puget Sound Energy Form 7517",
        "Square D Homeline HOM3060M200PC — 200 A main breaker load center with 225 A busbar for solar 120% rule headroom",
        "Square D Homeline HOM3060L225PGC — 225 A main lug load center for whole-home subpanel conversions",
    ),
    sections=(
        ("Why an outdoor meter-main combo satisfies NEC 230.85", (
            'Under NEC 230.85, every dwelling service replacement or upgrade must include an outdoor emergency disconnect. Installing a NEMA 3R meter-main combo like the Milbank U5168-XTL-200 or Square D SC816D200C satisfies both utility metering and NEC 230.85 in one enclosure. Check solar headroom on a 225 A bus with our <a href="/tools/solar-120-percent-rule-calculator/">solar 120% rule calculator</a>.',
        )),
        ("Check utility meter socket lists before ordering", (
            'Utilities like <a href="/permits/wa/bellevue/panel-upgrade/">Puget Sound Energy (Bellevue)</a> and <a href="/permits/ca/san-francisco/panel-upgrade/">PG&E (San Francisco)</a> enforce strict rules on ringed vs. ringless meter sockets. Always verify your utility list before buying.',
        )),
    ),
    tool_links=("residential-load-calculator", "solar-120-percent-rule-calculator"),
    doc_links=("single-line-diagram", "equipment-cut-sheets"),
    related_slugs=("subpanel-vs-200a-panel-upgrade", "utility-service-upgrade-rules-pge-srp-aps-duke-pse"),
    faqs=(
        ("What is the difference between a ringed and ringless meter socket?", "A ringed socket uses a utility sealing ring around the glass meter cover (required by PG&E, SDG&E, and PSE), whereas ringless secures with the cover latch."),
        ("Do I need surge protection when upgrading to a 200A panel?", "Yes. NEC 230.67 requires a Type 1 or Type 2 Surge Protective Device on every replaced or upgraded dwelling service."),
        ("What size wire is required for a 200A residential service?", "Under NEC 310.12 (83% rule), a 200 A single-phase dwelling service requires #2/0 AWG copper or #4/0 AWG aluminum conductors."),
    ),
)

GUIDES["best-ev-load-management-devices-100a-panel"] = Guide(
    slug="best-ev-load-management-devices-100a-panel", category="best-of", job="ev-charger", role="diy",
    crumb="Best EV Load Management (100A)", h1="Best EV Load Management Devices (NEC 625.42) for 100A Panels",
    title="Best EV Load Management Devices (NEC 625.42) for 100A Panels",
    description="Avoid a $4,000 service upgrade on a 100A panel. Compare UL-listed EV Energy Management Systems (EVEMS) like DCC-12, SimpleSwitch and Span.",
    answer="EV Energy Management Systems (EVEMS) listed under UL 916 and permitted under NEC 625.42 monitor main service current and automatically pause or throttle EV charging when household demand peaks. Installing a load controller such as a DCC-12, SimpleSwitch, or smart load center lets 100A homes add a 48A charger without a utility service upgrade.",
    card="Compare UL 916 load-shedding controllers (DCC-12, SimpleSwitch, Span) to fit an EV charger on 100A.",
    table_caption="UL-Listed EV Energy Management Systems (NEC 625.42)",
    table_headers=("Device / System", "Control Method", "Listing Standard", "Best Application"),
    table_rows=(
        ("Thermolec DCC-12 / DCC-9", "CT sensors + contactor load shed", "UL 916 / CSA C22.2", "Dedicated EV circuit on a full 100A/125A panel"),
        ("SimpleSwitch 240M", "CT monitoring + automatic load shed", "UL 916 listed", "Sharing capacity between EV charger and range/dryer"),
        ("Emporia Vue + EV Charger", "Dynamic amperage throttling (6A-48A)", "UL 916 / UL 2594", "Throttles charge rate smoothly instead of shutoff"),
        ("Wallbox Pulsar Plus + Power Boost", "Dynamic CT current modulation", "UL 916 / UL 2594", "Wallbox owners with 100A service needing modulation"),
        ("SPAN Smart Electrical Panel", "Whole-panel circuit load management", "UL 67 / UL 916", "Full panel replacement where upgrade is impractical"),
    ),
    listicle_items=(
        "Thermolec DCC-12 — Dedicated UL 916 EV energy management controller with main-feeder CTs",
        "SimpleSwitch 240M — UL 916 load management switch for EV chargers and 240V appliances",
        "Emporia Pro / Vue Load Management — Dynamic current throttling listed for NEC 625.42",
        "Wallbox Power Boost — Real-time current modulation paired with Wallbox Pulsar Plus",
        "SPAN Panel — Circuit-level smart load center for 100A-200A services",
    ),
    sections=(
        ("How NEC 625.42 lets you exclude the EV charger from peak load", (
            'Normally, an <a href="/tools/ev-charger-load-calculator/">NEC 220.82 load calculation</a> adds 100% of your charger nameplate on top of existing home demand. Under NEC 625.42 and NEC 750.30, when a UL 916 Energy Management System monitors main feeders with CTs and restricts total demand below 80% of the service rating, the charger does not overload the service.',
        )),
        ("What plan reviewers ask for when using an EVEMS", (
            'Include the EVEMS manufacturer UL 916 cut sheet in your <a href="/permit-documents/equipment-cut-sheets/">equipment cut sheets</a> and show the CT sensors on the main service conductors in your <a href="/permit-documents/single-line-diagram/">single-line diagram</a>.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "ev-charger-wire-breaker-size"),
    doc_links=("load-calculation", "single-line-diagram"),
    related_slugs=("nec-220-82-vs-220-87-load-calculation", "best-48a-hardwired-ev-chargers-for-permits"),
    faqs=(
        ("Does NEC 625.42 require utility approval?", "No. An EVEMS installs on the load side of your main breaker inside your home."),
        ("Can I use a dryer splitter instead of a UL 916 EVEMS?", "No; plug-in dryer splitters do not qualify under NEC 625.42 for hardwired 48 A circuits."),
        ("What happens to my EV when the DCC-12 sheds load?", "The charger pauses while major appliances run, then automatically resumes charging overnight."),
    ),
)

GUIDES["cities-allowing-owner-builder-ev-charger-permits"] = Guide(
    slug="cities-allowing-owner-builder-ev-charger-permits", category="local-guides", job="ev-charger", role="diy",
    crumb="Owner-Builder EV Permit Cities", h1="Top Cities Allowing Owner-Builder EV Charger Permits",
    title="Top Cities Allowing Owner-Builder EV Charger Permits",
    description="See which US cities allow homeowner owner-builder EV charger permits vs contractor-only rules, including El Cajon, Chandler, Mesa and Bellevue.",
    answer="Many US cities allow homeowners to pull an owner-builder electrical permit for an EV charger on a single-family home they occupy, including El Cajon, Chandler, Mesa, Bellevue, Charlotte, and Oro Valley. By contrast, jurisdictions like San Francisco and Metro Nashville restrict electrical permits to licensed electrical contractors.",
    card="City-by-city breakdown of owner-builder EV charger permit rules, portals and NEC editions.",
    table_caption="Owner-Builder Eligibility & Code Editions Across Verified Cities",
    table_headers=("City", "Owner-Builder Allowed?", "Code Edition", "Submittal Method"),
    table_rows=(
        ("El Cajon, CA", "Yes (occupant homeowner)", "2025 CEC (2023 NEC base)", "Building Safety application + parcel site plan"),
        ("Chandler, AZ", "Yes (occupant homeowner)", "2023 NEC", "Online portal + single combined PDF"),
        ("Mesa, AZ", "Yes (occupant homeowner)", "2023 NEC + Mesa amendments", "DIMES online portal + load calc & 1-line"),
        ("Oro Valley, AZ", "Yes (occupant homeowner)", "2023 NEC", "Email PDFs or 2 hard-copy sets"),
        ("Bellevue, WA", "Yes (owner-occupied dwelling)", "2023 NEC + WA amendments", "MyBuildingPermit.com online portal"),
        ("Charlotte, NC", "Yes (owner-occupied home)", "2023 NC Electrical Code", "Mecklenburg County online portal"),
        ("San Francisco, CA", "No (licensed C-10 only)", "2025 SF Electrical Code", "DBI online submittal + E-02 form"),
        ("Nashville, TN", "No (licensed contractor only)", "2023 NEC + Metro amendments", "Metro Codes ePermits portal"),
    ),
    listicle_items=(
        "El Cajon, CA — Allows owner-builder EV charger permits with parcel site plan and single-line diagram",
        "Chandler, AZ — Accepts owner-builder online EV charger submittals as one combined PDF",
        "Mesa, AZ — Allows owner-builder permits under the 2023 NEC with Mesa local amendments",
        "Bellevue, WA — Processes owner-builder EV charger permits online via MyBuildingPermit.com",
        "Charlotte / Mecklenburg County, NC — Allows owner-builder permits for owner-occupied homes",
        "Oro Valley, AZ — Accepts owner-builder EV charger applications by email or in person",
    ),
    sections=(
        ("How owner-builder rules differ across states", (
            'Homeowners living in a single-family house generally qualify for an owner-builder exemption in CA, AZ, WA, and NC. Explore our <a href="/permits/">city electrical permit database</a>—including <a href="/permits/ca/el-cajon/ev-charger/">El Cajon</a>, <a href="/permits/az/chandler/ev-charger/">Chandler</a>, and <a href="/permits/wa/bellevue/ev-charger/">Bellevue</a>—for each city checklist.',
        )),
        ("Cities that require a licensed electrical contractor", (
            '<a href="/permits/ca/san-francisco/ev-charger/">San Francisco DBI</a> and <a href="/permits/tn/nashville/ev-charger/">Metro Nashville Codes</a> restrict electrical permits to licensed contractors. You can still generate your <a href="/ev-charger-permit/">EV charger permit plans</a> and hand them to your electrician.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "ev-charger-wire-breaker-size"),
    doc_links=("site-plan", "load-calculation"),
    related_slugs=("owner-builder-permit-vs-licensed-electrician", "2023-nec-and-california-electrical-code-permit-guide"),
    faqs=(
        ("Does an owner-builder permit cost less than a contractor permit?", "City permit fees are usually the same, while you save installation labor markup."),
        ("What if my city isn't listed in your city directory?", "Any US property address works in Permit Packets using a general NEC checklist."),
        ("Do owner-builder permits get inspected more strictly?", "Inspectors enforce the same NEC standards for homeowners and contractors alike."),
    ),
)

GUIDES["utility-service-upgrade-rules-pge-srp-aps-duke-pse"] = Guide(
    slug="utility-service-upgrade-rules-pge-srp-aps-duke-pse", category="local-guides", job="panel-upgrade", role="electrician",
    crumb="Utility Panel Upgrade Rules", h1="Utility Panel Upgrade Rules: PG&E, SRP, APS, Duke & PSE",
    title="Utility Panel Upgrade Rules: PG&E, SRP, APS & Duke",
    description="Compare electric utility requirements for 200A panel upgrades across PG&E, SRP, APS, Duke Energy, NES and Puget Sound Energy (PSE).",
    answer="Upgrading a residential electrical service requires coordinating with both your city building department and your electric utility. Utilities such as PG&E, SRP, APS, Duke Energy, Nashville Electric Service, and Puget Sound Energy enforce distinct rules on meter-main catalog approvals, overhead versus underground service drops, and disconnect clearances.",
    card="Utility-specific meter-main approvals, disconnect limits and service rules across 6 major utilities.",
    table_caption="Service Upgrade Requirements Across Major Electric Utilities",
    table_headers=("Utility", "Service Area", "Key Meter & Service Rules on File"),
    table_rows=(
        ("PG&E", "San Francisco & Northern CA", "EUSERC ringed meter socket; RMC/IMC min 1-1/4 in service raceway"),
        ("SRP / APS", "Mesa & Chandler, AZ", "109°F ASHRAE outdoor ambient derating; EUSERC approved meter-main"),
        ("Puget Sound Energy (PSE)", "Bellevue & King County, WA", "Must use PSE Form 7517 pre-approved meter socket (e.g. Square D SC816D200C)"),
        ("Nashville Electric (NES)", "Nashville / Davidson County, TN", "Main service disconnect required within 5 ft of point of entrance"),
        ("Duke Energy", "Charlotte / Mecklenburg County, NC", "Ringless meter socket standard; work-order coordination for cutover"),
    ),
    sections=(
        ("Why utility rules matter just as much as the NEC", (
            'Every residential service upgrade involves two separate approvals: your municipal building department enforces the NEC, while your electric utility governs the meter socket, service drop, and disconnect clearances.',
            'If you install a meter-main panel not on your utility approved list, the utility will not set the meter even after city inspection. In <a href="/permits/wa/bellevue/panel-upgrade/">Bellevue</a>, PSE requires a Form 7517 socket, while <a href="/permits/ca/san-francisco/panel-upgrade/">San Francisco</a> enforces RMC/IMC metallic raceway rules for PG&E.',
        )),
        ("High-temperature conductor derating in Arizona & Tennessee", (
            'In <a href="/permits/az/mesa/panel-upgrade/">Mesa</a> and <a href="/permits/az/chandler/panel-upgrade/">Chandler</a> (109°F ASHRAE) or <a href="/permits/tn/nashville/panel-upgrade/">Nashville</a> (92°F), outdoor service raceways require NEC 310.15(B)(1) ambient correction. Our <a href="/panel-upgrade-permit/">panel upgrade permit packet</a> applies this automatically.',
        )),
    ),
    tool_links=("residential-load-calculator", "solar-120-percent-rule-calculator"),
    doc_links=("single-line-diagram", "equipment-cut-sheets"),
    related_slugs=("best-200a-meter-main-combo-panels", "subpanel-vs-200a-panel-upgrade"),
    faqs=(
        ("How long does a utility service disconnect and reconnect take?", "Typically same-day: disconnected in the morning and reconnected in the afternoon after city green-tag approval."),
        ("Does a panel upgrade require a new grounding electrode?", "Yes. NEC 250.50 requires bonding ground rods, Ufer electrode, and water pipe with a GEC sized per Table 250.66."),
        ("What if I relocate my new 200A panel?", "Relocating triggers updated utility clearances (gas meter, windows) and may require underground conversion."),
    ),
)

GUIDES["2023-nec-and-california-electrical-code-permit-guide"] = Guide(
    slug="2023-nec-and-california-electrical-code-permit-guide", category="local-guides", job="panel-upgrade", role="diy",
    crumb="2023 NEC & 2025 CEC Rules", h1="2023 NEC & 2025 California Electrical Code Permit Guide",
    title="2023 NEC & 2025 California Electrical Code Permit Guide",
    description="Understand key 2023 NEC and 2025 California Electrical Code (CEC) rules for residential permits: GFCI expansion, surge protection and outdoor disconnects.",
    answer="The 2023 National Electrical Code and the 2025 California Electrical Code require Type 1 or Type 2 surge protective devices on replaced dwelling services (NEC 230.67), emergency disconnects outdoors (NEC 230.85), and expanded GFCI protection for 240V receptacles including EV charger outlets (NEC 625.54).",
    card="Major 2023 NEC and 2025 CEC rules that impact EV chargers, service upgrades and 240V circuits.",
    table_caption="Key 2023 NEC & 2025 CEC Code Rules Checked in Permit Packets",
    table_headers=("Code Section", "Requirement", "Affected Permit Types"),
    table_rows=(
        ("NEC 230.67", "Type 1 or Type 2 Surge Protective Device (SPD) at service", "Panel & service upgrades / replacements"),
        ("NEC 230.85", "Emergency disconnect in readily accessible outdoor location", "Service upgrades & exterior meter-mains"),
        ("NEC 625.54", "GFCI protection for all EV charging receptacles (NEMA 14-50)", "Plug-in EV charger circuits"),
        ("NEC 210.8(F)", "GFCI protection for outdoor HVAC / mini-split outlets", "Heat pump & mini-split circuits"),
        ("NEC 680.44 & 680.13", "GFCI protection + disconnect >= 5 ft from spa water", "Hot tub & spa 240V circuits"),
    ),
    sections=(
        ("Why code edition matters on your permit title block", (
            'The National Electrical Code is updated every three years, and each state or municipality adopts a specific edition with local amendments.',
            'Building departments review plans against the adopted edition—2023 NEC in AZ, WA, NC, and TN, or the 2025 California Electrical Code (effective January 1, 2026) in CA. Omitting NEC 230.67 surge protection or NEC 230.85 disconnects causes immediate plan-check corrections.',
        )),
        ("How Permit Packets applies state and local code rules automatically", (
            'Every <a href="/panel-upgrade-permit/">panel upgrade</a>, <a href="/ev-charger-permit/">EV charger</a>, <a href="/subpanel-permit/">subpanel</a>, and <a href="/hot-tub-240v-permit/">hot tub permit packet</a> prints the adopted code edition and verifies surge protection, disconnects, and heat derating.',
        )),
    ),
    tool_links=("residential-load-calculator", "hot-tub-breaker-wire-size"),
    doc_links=("single-line-diagram", "load-calculation"),
    related_slugs=("7-reasons-electrical-permits-fail-plan-check", "cities-allowing-owner-builder-ev-charger-permits"),
    faqs=(
        ("When did the 2025 California Electrical Code take effect?", "The 2025 California Electrical Code (based on the 2023 NEC) took effect January 1, 2026."),
        ("Do I have to upgrade existing house breakers to AFCI during a panel swap?", "Replacing a panel alone generally does not require rewiring undamaged existing branch circuits unless extended over 6 ft."),
        ("Is a surge protector required on a subpanel?", "NEC 230.67 applies to dwelling unit services; an SPD on a subpanel is optional unless locally amended."),
    ),
)

GUIDES["how-to-check-if-panel-can-handle-ev-charger"] = Guide(
    slug="how-to-check-if-panel-can-handle-ev-charger", category="diy-tips", job="ev-charger", role="diy",
    crumb="Can My Panel Handle an EV Charger?", h1="How to Check If Your Panel Can Handle an EV Charger",
    title="How to Check If Your Panel Can Handle an EV Charger",
    description="Follow 4 steps to check if your 100A or 200A electrical panel can support a Level 2 EV charger: main breaker, open spaces, bus rating and NEC 220 calc.",
    answer="To check if your electrical panel can handle a Level 2 EV charger, verify four items: your main breaker amperage, two adjacent open breaker spaces for a 240V two-pole breaker, your panel busbar rating, and an NEC Article 220.82 load calculation confirming total demand stays within your service rating.",
    card="4-step homeowner audit to check breaker spaces, main rating and NEC 220 spare capacity.",
    table_caption="4-Step Electrical Panel Readiness Check for Level 2 EV Charging",
    table_headers=("Panel Check", "What to Look For", "Action If It Fails"),
    table_rows=(
        ("1. Main Breaker Rating", "100A, 125A, 150A, or 200A stamped on handle", "Use NEC 220.87 demand data, EVEMS, or 200A upgrade"),
        ("2. Open Breaker Slots", "Two adjacent vertical spaces for a 2-pole breaker", "Consolidate with UL-listed tandems or add a subpanel"),
        ("3. NEC 220.82 Load Calc", "Computed service current below main breaker amps", "Derate charger to 32A/40A or install load management"),
        ("4. Wire Run & Terminals", "Run length under 100 ft and 75°C rated terminals", "Upsize copper wire to #4 AWG for voltage drop"),
    ),
    sections=(
        ("Step 1: Read your main breaker amperage & check two open spaces", (
            'Before buying a Level 2 charger or scheduling an electrician, spend five minutes inspecting your main service panel and measuring the distance to your parking spot.',
            'Open your main panel door and read the main breaker handle (typically 100 A, 150 A, or 200 A). A 240 V charger requires a 2-pole breaker spanning two adjacent spaces. If every slot is full, you can add a <a href="/subpanel-permit/">subpanel</a> or use an <a href="/guides/best-ev-load-management-devices-100a-panel/">NEC 625.42 load management device</a> on 100 A panels.',
        )),
        ("Step 2: Run an NEC Article 220.82 load calculation & check wire length", (
            'Empty breaker slots do not guarantee spare electrical capacity. Run your living area and electric appliances through our <a href="/tools/ev-charger-load-calculator/">free EV charger load calculator</a>, then check voltage drop for your exact run length with our <a href="/tools/ev-charger-wire-breaker-size/">wire and breaker calculator</a>.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "ev-charger-wire-breaker-size"),
    doc_links=("panel-schedule", "load-calculation"),
    related_slugs=("how-to-read-electrical-panel-label-aic-bus-rating", "nec-220-82-vs-220-87-load-calculation"),
    faqs=(
        ("Can a 100A panel support a 48A EV charger?", "Usually only if major appliances are gas, or with a UL 916 load controller (NEC 625.42) or NEC 220.87 utility demand data."),
        ("What if my panel is a Federal Pacific (FPE) or Zinsco brand?", "FPE Stab-Lok and Zinsco panels have documented breaker failure issues and should be replaced before adding EV loads."),
        ("How many amps does a Level 2 charger actually pull?", "Most hardwired chargers draw 32 A, 40 A, or 48 A continuously on 40 A, 50 A, or 60 A breakers."),
    ),
)

GUIDES["how-to-read-electrical-panel-label-aic-bus-rating"] = Guide(
    slug="how-to-read-electrical-panel-label-aic-bus-rating", category="diy-tips", job="panel-upgrade", role="diy",
    crumb="How to Read Your Panel Label", h1="How to Read Your Electrical Panel Label: Bus & AIC Rating",
    title="How to Read Your Electrical Panel Label: Bus and AIC Rating",
    description="Learn how to read the UL sticker inside your electrical panel: busbar rating, main breaker amps, 10kA vs 22kA AIC rating and 75°C terminal markings.",
    answer="The UL specification label inside your electrical panel door lists four numbers every permit application needs: the maximum busbar ampacity, the main overcurrent device rating, the short-circuit interrupting rating (typically 10 kA or 22 kA AIC), and the enclosure type (NEMA 1 indoor or NEMA 3R outdoor).",
    card="Decode busbar amps, AIC interrupting ratings, tandem limits and 75°C terminal labels for your permit.",
    table_caption="Key Specifications on a Residential Electrical Panel UL Label",
    table_headers=("Label Field", "Typical Values", "Why Permit Reviewers Check It"),
    table_rows=(
        ("Busbar Rating", "100A, 125A, 200A, or 225A", "Busbar must equal or exceed main breaker; governs solar 120% rule"),
        ("Interrupting Rating (AIC)", "10,000 A (10 kA) or 22,000 A (22 kA)", "Must exceed utility available fault current (NEC 110.9)"),
        ("Spaces / Circuits", "20/40, 30/60, 40/80", "Determines whether tandem breakers are UL-listed"),
        ("Enclosure Type", "Type 1 (Indoor) or Type 3R (Rainproof)", "Outdoor panels must be NEMA 3R rated (NEC 312.2)"),
    ),
    sections=(
        ("Busbar rating vs. main breaker & solar 120% headroom", (
            'Inside every load center door, the UL specification sticker lists the exact busbar ampacity, maximum main breaker rating, and compatible branch breaker types.',
            'Many 200 A panels actually carry a 225 A busbar rating, which allows up to a 70 A solar backfeed breaker under the <a href="/tools/solar-120-percent-rule-calculator/">NEC 705.12 120% rule</a>. Always read the busbar rating printed on the inside door sticker rather than assuming it matches the main breaker.',
        )),
        ("AIC interrupting rating & panel schedule documentation", (
            'Under NEC 110.9, your panel AIC rating (10 kA or 22 kA) must meet or exceed available utility fault current. Pair your panel label data with a clear circuit directory using our <a href="/permit-documents/panel-schedule/">panel schedule guide</a> or build a complete <a href="/panel-upgrade-permit/">panel upgrade packet</a>.',
        )),
    ),
    tool_links=("solar-120-percent-rule-calculator", "residential-load-calculator"),
    doc_links=("panel-schedule", "equipment-cut-sheets"),
    related_slugs=("how-to-check-if-panel-can-handle-ev-charger", "ev-charger-trench-depth-conduit-rules-nec-300-5"),
    faqs=(
        ("What if the sticker inside my panel door is missing?", "Check the metal nameplate stamped near the main breaker or read the breaker series (e.g., Square D HOM, Eaton BR) to verify ratings."),
        ("What does '30 spaces / 60 circuits' mean?", "The panel has 30 full-size slots and is UL-listed to accept tandem breakers in all 30 slots."),
        ("Why does 75°C terminal rating matter?", "75°C terminals allow #6 AWG copper (65 A) instead of #4 AWG copper (55 A at 60°C) on a 60 A EV circuit."),
    ),
)

GUIDES["ev-charger-trench-depth-conduit-rules-nec-300-5"] = Guide(
    slug="ev-charger-trench-depth-conduit-rules-nec-300-5", category="diy-tips", job="subpanel", role="diy",
    crumb="Trench Depth & Conduit Rules", h1="Detached Garage Trench Depth & Conduit Rules (NEC 300.5)",
    title="Detached Garage Trench Depth & Conduit Rules (NEC 300.5)",
    description="NEC Table 300.5 burial depth rules for running EV charger or subpanel power to a detached garage: 18 in PVC vs 6 in RMC vs 24 in UF-B cable.",
    answer="Under NEC Table 300.5, underground residential electrical runs to a detached garage require 18 inches of cover for Schedule 40 or 80 PVC conduit, 6 inches for rigid metal conduit (RMC), and 24 inches for direct-burial UF-B cable. Always call 811 before digging and include a trench cross-section detail on your site plan.",
    card="NEC Table 300.5 minimum burial depths for PVC, RMC, EMT and UF-B cable to detached garages.",
    table_caption="NEC Table 300.5 Minimum Underground Cover Requirements (Residential)",
    table_headers=("Wiring Method", "Standard Trench", "Under Driveway", "Notes & Restrictions"),
    table_rows=(
        ("Schedule 40 / 80 PVC", "18 inches cover", "18 inches cover", "Use Schedule 80 PVC where emerging above grade"),
        ("Rigid Metal Conduit (RMC)", "6 inches cover", "6 inches cover", "Useful across rocky soil or shallow concrete"),
        ("Direct-Burial UF-B Cable", "24 inches cover", "24 inches cover", "Requires conduit risers; restricted in some cities"),
    ),
    sections=(
        ("Cover depth means soil above the top of the conduit", (
            'A frequent DIY inspection failure is digging an 18-inch trench and laying 1-inch PVC inside, leaving less than 17 inches of soil above the pipe.',
            'NEC Table 300.5 measures cover from finished grade down to the top surface of the pipe, so dig a 20 to 21 inch trench to achieve 18 inches of cover over 1-inch PVC. Call 811 before digging and pull wet-rated THWN-2 wire sized with our <a href="/tools/subpanel-feeder-calculator/">subpanel feeder calculator</a>.',
        )),
        ("Detached garage disconnect and grounding rules", (
            'Detached structures require a local disconnect (NEC 225.31) and ground rods for a <a href="/subpanel-permit/">subpanel feeder</a> (NEC 250.32). Dimension the trench route on your <a href="/permit-documents/site-plan/">site plan</a> and include a trench cross-section on your <a href="/permit-documents/single-line-diagram/">single-line diagram</a>.',
        )),
    ),
    tool_links=("subpanel-feeder-calculator", "ev-charger-wire-breaker-size"),
    doc_links=("site-plan", "single-line-diagram"),
    related_slugs=("subpanel-vs-200a-panel-upgrade", "7-reasons-electrical-permits-fail-plan-check"),
    faqs=(
        ("Can I run EMT conduit underground?", "Standard steel EMT corrodes in direct soil; use Schedule 40/80 PVC underground and transition to Schedule 80 PVC or EMT above grade."),
        ("Do I need a trench inspection before backfilling?", "Yes. Leave the trench open until the inspector verifies depth and conduit during underground inspection."),
        ("What size PVC conduit do I need for a detached garage?", "A 60 A EV circuit (#6 Cu) uses 3/4 in PVC; a 100 A subpanel feeder (#1 Al) uses 1-1/4 in PVC."),
    ),
)

GUIDES["7-reasons-electrical-permits-fail-plan-check"] = Guide(
    slug="7-reasons-electrical-permits-fail-plan-check", category="diy-tips", job="ev-charger", role="diy",
    crumb="7 Plan-Check Rejection Fixes", h1="7 Reasons Residential Electrical Permits Fail Plan Check",
    title="7 Reasons Residential Electrical Permits Fail Plan Check",
    description="Avoid costly plan-check rejections on EV charger, panel upgrade and subpanel permits. Fix these 7 common NEC load calc, single-line and site plan errors.",
    answer="Residential electrical permits most often fail city plan check due to missing NEC Article 220 load calculations, sizing EV charger wire at 100% instead of 125% continuous load, omitting manufacturer UL cut sheets, lacking a scaled parcel site plan, or forgetting NEC 230.67 surge protection on service upgrades.",
    card="The 7 most common plan-review correction items—and how to clear every one before submitting.",
    listicle_items=(
        "1. Missing or incomplete NEC Article 220 load calculation",
        "2. Sizing EV charger or hot tub wire at 100% instead of 125% continuous load",
        "3. Submitting a site plan without lot lines, scale bar, or measured wire route",
        "4. Omitting manufacturer UL specification cut sheets for chargers or panels",
        "5. Leaving out NEC 230.67 surge protection or NEC 230.85 outdoor disconnects on service upgrades",
        "6. Ignoring voltage drop or equipment grounding conductor upsizing on long runs (NEC 250.122(B))",
        "7. Citing an outdated NEC code edition or missing city-specific amendments",
    ),
    sections=(
        ("1. Missing NEC 220 load calculation & 125% continuous sizing", (
            'Plan reviewers immediately flag applications that omit an NEC Article 220 dwelling load calculation or size continuous loads at 100% rather than 125%. For example, a 48 A EV charger requires a 60 A breaker and #6 AWG copper conductors.',
            'Reviewers reject applications lacking an <a href="/permit-documents/load-calculation/">NEC 220.82 load calculation</a> or sizing continuous loads (EV chargers, hot tubs) at 100% instead of 125%. Check exact sizing with our <a href="/tools/ev-charger-wire-breaker-size/">EV wire calculator</a> and <a href="/tools/hot-tub-breaker-wire-size/">hot tub calculator</a>.',
        )),
        ("2. Unscaled site plans, missing UL cut sheets & surge protection", (
            'Include a scaled <a href="/permit-documents/site-plan/">parcel site plan</a> (see our <a href="/sample-packet/">El Cajon sample packet</a>), attach manufacturer <a href="/permit-documents/equipment-cut-sheets/">UL cut sheets</a>, and show NEC 230.67 surge protection on <a href="/panel-upgrade-permit/">panel upgrades</a>.',
        )),
    ),
    tool_links=("ev-charger-load-calculator", "residential-load-calculator"),
    doc_links=("site-plan", "single-line-diagram", "load-calculation"),
    related_slugs=("how-to-check-if-panel-can-handle-ev-charger", "2023-nec-and-california-electrical-code-permit-guide"),
    faqs=(
        ("How long does city electrical plan check usually take?", "Complete residential packets often clear in 1 to 5 business days, while incomplete submittals stall for weeks."),
        ("What does the $169 24-Hour City-Checked package do?", "We review your generated sheets against your city's published checklist within 24 hours before releasing the packet."),
        ("Can I preview my packet before paying?", "Yes. Every packet generates a free watermarked preview with engineering checks before payment."),
    ),
)


from dataclasses import replace as _rep

_EXTRA_SEC = (
    "Pre-submittal NEC & field inspection checklist",
    (
        "Before uploading your electrical permit packet to your city building portal, verify four core items that plan reviewers check on every residential submittal: first, confirm your parcel boundary, structure footprint, and measured conduit run are drawn to scale on the site plan; second, verify continuous loads (such as EV chargers, hot tubs, and electric heaters) are sized at 125% of nameplate current for both the breaker and conductors under NEC Article 210 and Article 625.",
        "Third, confirm the equipment grounding conductor matches NEC Table 250.122 (including proportional upsizing under NEC 250.122(B) whenever phase conductors are upsized for voltage drop over long runs) and attach the manufacturer's UL listing cut sheet behind your Equipment Data page. Running a free watermarked preview in Permit Packets checks each of these rules automatically against your city's adopted NEC edition before you pay or submit, ensuring your site plan, single-line diagram, load calculation, and UL equipment cut sheets align with local plan-review checklists on the first submission.",
    ),
)

for _s, _g in list(GUIDES.items()):
    GUIDES[_s] = _rep(_g, sections=_g.sections + (_EXTRA_SEC,))
