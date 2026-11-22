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
    "concepts": ("Permit Concepts Explained", "Plain-English explanations of the documents and code terms plan reviewers ask for."),
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
    related_slugs=("hardwired-vs-plug-in-ev-charger-permit", "what-is-an-appliance-cut-sheet-for-electrical-permit"),
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


# ---- Stage 4: Internal links & comparison rows for all 26 verified cities ----

GUIDES["cities-allowing-owner-builder-ev-charger-permits"] = _rep(
    GUIDES["cities-allowing-owner-builder-ev-charger-permits"],
    table_rows=GUIDES["cities-allowing-owner-builder-ev-charger-permits"].table_rows + (
        ("San Diego, CA", "Yes (occupant homeowner)", "2025 CEC (2023 NEC base)", "OpenDSD online portal + PDF plan set"),
        ("Los Angeles, CA", "Yes (single-family R-3)", "2026 LA Electrical Code", "LADBS ePlanLA online submittal"),
        ("Seattle, WA", "Yes (owner-occupant)", "2023 NEC + Seattle amendments", "Seattle Services Portal online PDF"),
        ("Portland, OR", "Yes (resident homeowner)", "2023 Oregon Electrical Code", "DevelopmentHub PDX online portal"),
        ("Austin, TX", "Yes (homestead owner)", "2023 NEC + Austin amendments", "Austin Build + Connect (AB+C)"),
        ("Phoenix, AZ", "Yes (occupant homeowner)", "2023 NEC + Phoenix amendments", "SHAPE PHX combined PDF upload"),
        ("Denver, CO", "Yes (owner-occupant)", "2023 NEC + Denver amendments", "Denver e-permits online submittal"),
        ("Raleigh, NC", "Yes (owner-occupant)", "2023 NC Electrical Code", "Raleigh Permit Portal online"),
    ),
    sections=GUIDES["cities-allowing-owner-builder-ev-charger-permits"].sections + (
        ("Expanded 2026 metro coverage: CA, WA, OR, TX, AZ, CO & NC", (
            'Homeowners and contractors can also generate city-specific EV charger permit packets for <a href="/permits/ca/san-diego/ev-charger/">San Diego</a>, <a href="/permits/ca/los-angeles/ev-charger/">Los Angeles</a>, <a href="/permits/wa/seattle/ev-charger/">Seattle</a>, <a href="/permits/or/portland/ev-charger/">Portland</a>, <a href="/permits/tx/austin/ev-charger/">Austin</a>, <a href="/permits/az/phoenix/ev-charger/">Phoenix</a>, <a href="/permits/co/denver/ev-charger/">Denver</a>, and <a href="/permits/nc/raleigh/ev-charger/">Raleigh</a>—each pre-loaded with local code editions, portal steps, and ASHRAE ambient derating.',
        )),
    ),
)

GUIDES["utility-service-upgrade-rules-pge-srp-aps-duke-pse"] = _rep(
    GUIDES["utility-service-upgrade-rules-pge-srp-aps-duke-pse"],
    table_rows=GUIDES["utility-service-upgrade-rules-pge-srp-aps-duke-pse"].table_rows + (
        ("SDG&E", "San Diego, CA", "EUSERC ringed meter socket; Information Bulletin 501 service rules"),
        ("LADWP", "Los Angeles, CA", "LADWP Electric Service Requirements; EUSERC meter-main combo"),
        ("SMUD", "Sacramento, CA", "SMUD service clearance + green-tag release before cutover"),
        ("Seattle City Light", "Seattle, WA", "SCL service entrance standards; plan review on large upgrades"),
        ("Austin Energy", "Austin, TX", "Austin Energy Design Criteria; AB+C work-order coordination"),
        ("Oncor / CenterPoint", "Dallas & Houston, TX", "100-101°F ASHRAE outdoor derating; utility meter-release hold"),
        ("Xcel Energy", "Denver & Aurora, CO", "Xcel Standard for Electric Installation; NEC 230.85 disconnect"),
    ),
    sections=GUIDES["utility-service-upgrade-rules-pge-srp-aps-duke-pse"].sections + (
        ("Meter-main & disconnect rules in CA, WA, TX & CO metros", (
            'Check local utility and municipal panel upgrade checklists for <a href="/permits/ca/san-diego/panel-upgrade/">San Diego (SDG&E)</a>, <a href="/permits/ca/los-angeles/panel-upgrade/">Los Angeles (LADWP)</a>, <a href="/permits/ca/sacramento/panel-upgrade/">Sacramento (SMUD)</a>, <a href="/permits/wa/seattle/panel-upgrade/">Seattle (SCL)</a>, <a href="/permits/tx/austin/panel-upgrade/">Austin (Austin Energy)</a>, <a href="/permits/tx/houston/panel-upgrade/">Houston (CenterPoint)</a>, and <a href="/permits/co/denver/panel-upgrade/">Denver (Xcel Energy)</a>.',
        )),
    ),
)

GUIDES["2023-nec-and-california-electrical-code-permit-guide"] = _rep(
    GUIDES["2023-nec-and-california-electrical-code-permit-guide"],
    sections=GUIDES["2023-nec-and-california-electrical-code-permit-guide"].sections + (
        ("State-by-state adoption across our 26 verified cities", (
            'Whether you are filing under the 2025 California Electrical Code in <a href="/permits/ca/san-jose/">San Jose</a> and <a href="/permits/ca/oakland/">Oakland</a>, the 2023 NEC in <a href="/permits/az/scottsdale/">Scottsdale</a>, <a href="/permits/tx/dallas/">Dallas</a>, <a href="/permits/tx/san-antonio/">San Antonio</a>, <a href="/permits/wa/tacoma/">Tacoma</a>, and <a href="/permits/co/aurora/">Aurora</a>, or the Florida Building Code (2020 NEC base) in <a href="/permits/fl/tampa/">Tampa</a>, Permit Packets applies your jurisdiction code edition automatically.',
        )),
    ),
)

GUIDES["best-48a-hardwired-ev-chargers-for-permits"] = _rep(
    GUIDES["best-48a-hardwired-ev-chargers-for-permits"],
    sections=GUIDES["best-48a-hardwired-ev-chargers-for-permits"].sections + (
        ("Streamlined online EV charger permitting in major metros", (
            'Jurisdictions such as <a href="/permits/ca/san-diego/ev-charger/">San Diego</a>, <a href="/permits/tx/austin/ev-charger/">Austin</a>, and <a href="/permits/wa/seattle/ev-charger/">Seattle</a> offer streamlined online permitting for UL 2594 hardwired chargers when accompanied by a complete single-line diagram, load calc, and cut sheet.',
        )),
    ),
)

GUIDES["best-200a-meter-main-combo-panels"] = _rep(
    GUIDES["best-200a-meter-main-combo-panels"],
    sections=GUIDES["best-200a-meter-main-combo-panels"].sections + (
        ("Matching meter-main combos to local utility manuals", (
            'Before ordering hardware for a service upgrade in <a href="/permits/ca/los-angeles/panel-upgrade/">Los Angeles</a>, <a href="/permits/az/phoenix/panel-upgrade/">Phoenix</a>, or <a href="/permits/co/denver/panel-upgrade/">Denver</a>, confirm overhead versus underground feed requirements and ringed versus ringless socket rules on your city permit checklist.',
        )),
    ),
)

GUIDES["owner-builder-permit-vs-licensed-electrician"] = _rep(
    GUIDES["owner-builder-permit-vs-licensed-electrician"],
    sections=GUIDES["owner-builder-permit-vs-licensed-electrician"].sections + (
        ("Homestead & resident-owner rules in OR, NC & FL", (
            'States like Oregon, North Carolina, and Florida allow resident homeowners to pull electrical permits on single-family homes they occupy—see local rules for <a href="/permits/or/portland/">Portland</a>, <a href="/permits/nc/raleigh/">Raleigh</a>, and <a href="/permits/fl/tampa/">Tampa</a>.',
        )),
    ),
)

GUIDES["what-is-an-appliance-cut-sheet-for-electrical-permit"] = Guide(
    slug="what-is-an-appliance-cut-sheet-for-electrical-permit", category="concepts", job="ev-charger", role="diy",
    crumb="Appliance Cut Sheets", h1="What is an Equipment Cut Sheet for an Electrical Permit?",
    title="Appliance & Equipment Cut Sheets for Electrical Permits",
    description="What an appliance or equipment cut sheet is, why building departments require it for electrical permits, and what plan reviewers check on it.",
    answer="An appliance cut sheet is the manufacturer's specification sheet for a charger, panel or appliance, listing its model number, electrical ratings and safety listings. City building departments require it for an electrical permit to verify NEC 220 load calculations, UL or CSA safety listings, and ampacity ratings against your plans.",
    card="What a cut sheet is, why cities require one, and what plan reviewers look for on it.",
    sections=(
        ("What a cut sheet shows", (
            "A cut sheet, also called a spec sheet or data sheet, is a one- or two-page document published by the manufacturer. It lists the model number, input voltage, amperage, wattage, wire terminal ratings, enclosure type and the testing-lab listing (such as UL 2594 for EV chargers). It is the evidence that the equipment on your plans is the equipment you will install.",
        )),
        ("What plan reviewers check on an equipment cut sheet for an electrical permit", (
            "Reviewers compare the cut sheet to your <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a> and load calculation. They look for three things: the model number matches the plans; the continuous load (amps and volts) matches the load calculation and the breaker size at 125% of continuous load; and the terminal temperature rating (commonly 75°C) supports the conductor ampacity you drew.",
        )),
        ("Why cities ask for it", (
            "The NEC Article 220 load calculation only works if the nameplate numbers are right. The cut sheet lets the reviewer confirm those numbers and the UL or CSA listing without a field visit, so a missing or mismatched sheet is a common reason for a correction notice. See the <a href=\"/guides/7-reasons-electrical-permits-fail-plan-check/\">common plan-check failures</a>.",
        )),
        ("How Permit Packets handles cut sheets", (
            "When your charger model is in our library, the manufacturer's cut sheet and UL spec sheet follow the Equipment Data sheet in your packet automatically. For other models, the sheet tells you to attach the manufacturer's data sheet behind it. Read more on the <a href=\"/permit-documents/equipment-cut-sheets/\">equipment cut sheets</a> page, or <a href=\"/ev-charger-permit/\">build your EV charger permit packet</a> and preview it free.",
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size",),
    doc_links=("equipment-cut-sheets", "single-line-diagram"),
    related_slugs=("tesla-wall-connector-gen-3-cut-sheet-permit", "emporia-classic-ev-charger-cut-sheet-permit", "wallbox-pulsar-plus-cut-sheet-permit"),
    faqs=(
        ("What is an appliance cut sheet?", "An appliance cut sheet is the manufacturer's specification sheet for a device. It gives the model number, electrical ratings and safety listings that a plan reviewer uses to verify your permit plans."),
        ("Do I need an equipment cut sheet for an electrical permit?", "Most cities that publish an electrical checklist ask for the manufacturer's specification sheet for major equipment such as an EV charger. Confirm with your building department."),
        ("Where do I find the cut sheet for my charger or appliance?", "Look on the manufacturer's product page under downloads, specifications or documents, or search the model number plus 'spec sheet'. Use the sheet for your exact model."),
        ("Is a cut sheet the same as a UL listing?", "No. The UL or CSA listing is a safety certification. The cut sheet is the document that shows the listing along with the ratings, and the reviewer reads both from it."),
    ),
)

GUIDES["tesla-wall-connector-gen-3-cut-sheet-permit"] = Guide(
    slug="tesla-wall-connector-gen-3-cut-sheet-permit", category="concepts", job="ev-charger", role="diy",
    crumb="Tesla Wall Connector Gen 3 Cut Sheet", h1="Tesla Wall Connector Gen 3 Cut Sheet & Specs for Permits",
    title="Tesla Wall Connector Gen 3 Cut Sheet & Specs for Permits",
    description="Tesla Wall Connector Gen 3 cut sheet specs for an electrical permit: 48A on a 60A breaker, 11.5 kW, cULus E351001, and #6 AWG copper wire.",
    answer="The Tesla Wall Connector Gen 3 delivers up to 48A (11.5 kW at 240V) on a 60A double-pole breaker. Its cut sheet lists cULus listing E351001, an integrated CCID20 ground-fault interrupter, copper-only terminals and a Type 3R enclosure, the data a plan reviewer checks against your permit plans.",
    card="Verified electrical specs from the Tesla Gen 3 Wall Connector cut sheet and what plan reviewers check.",
    table_caption="Tesla Wall Connector Gen 3 Specs for Permit Plans",
    table_headers=("Spec", "Value on the cut sheet"),
    table_rows=(
        ("Max output / breaker", "48 A on a 60 A double-pole breaker (11.5 kW at 240 V)"),
        ("Voltage / current range", "Nominal 200-240 V AC single-phase, 12-48 A"),
        ("Listing", "cULus, file E351001"),
        ("Conductors at max power", "Min. #6 AWG copper, 90°C THWN-2, on a 75°C-rated breaker (#4 AWG on a 60°C breaker)"),
        ("Terminals", "12-4 AWG, copper only"),
        ("Enclosure / GFCI", "Type 3R (IP54); integrated CCID20"),
        ("Disconnect", "External branch circuit breaker; no separate disconnect required"),
    ),
    sections=(
        ("What plan reviewers verify on the Gen 3 cut sheet", (
            "Reviewers match three things to your plans. The 48 A maximum output must agree with your <a href=\"/permit-documents/load-calculation/\">load calculation</a>, where an EV charger is a continuous load sized at 125%, giving the 60 A breaker. The cULus E351001 listing satisfies the listed-equipment requirement. The wire size on your <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a> must fit the cut sheet: #6 AWG copper at 90°C THWN-2 when the breaker is 75°C-rated, with copper-only terminals.",
        )),
        ("Lower breaker settings", (
            "The Gen 3 can be set to a lower output during commissioning. A 50 A breaker gives 40 A output (9.6 kW), 40 A gives 32 A (7.6 kW), and so on down to 15 A for 12 A output. If your panel cannot support 60 A, draw the lower breaker and the matching output on your plans so the load calculation and the cut sheet agree.",
        )),
        ("Where the cut sheet fits in your packet", (
            "New to the document? Read <a href=\"/guides/what-is-an-appliance-cut-sheet-for-electrical-permit/\">what an appliance cut sheet is for an electrical permit</a>. When you generate an EV charger permit with Permit Packets and pick this charger, the Tesla Gen 3 manufacturer PDF is bundled behind your Equipment Data sheet automatically. <a href=\"/start/?job=ev-charger&role=diy\">Start your EV charger permit packet</a> and preview it free.",
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size", "ev-charger-load-calculator"),
    doc_links=("equipment-cut-sheets", "single-line-diagram"),
    related_slugs=("what-is-an-appliance-cut-sheet-for-electrical-permit", "emporia-classic-ev-charger-cut-sheet-permit"),
    faqs=(
        ("What breaker does the Tesla Wall Connector Gen 3 need?", "For maximum 48 A output it needs a standard double-pole 60 A breaker. Lower breaker sizes reduce the output proportionally."),
        ("Is the Tesla Wall Connector Gen 3 UL listed?", "The cut sheet lists cULus approval under file E351001 and an integrated CCID20 ground-fault interrupter."),
        ("What wire size does a Tesla Wall Connector Gen 3 need?", "At full power on a 75°C-rated breaker the cut sheet calls for minimum #6 AWG, 90°C THWN-2 copper. On a 60°C-rated breaker it calls for #4 AWG. Terminals accept copper only."),
    ),
)

GUIDES["emporia-classic-ev-charger-cut-sheet-permit"] = Guide(
    slug="emporia-classic-ev-charger-cut-sheet-permit", category="concepts", job="ev-charger", role="diy",
    crumb="Emporia Classic Cut Sheet", h1="Emporia Classic EV Charger Cut Sheet & Specs for Permits",
    title="Emporia Classic EV Charger Cut Sheet & Specs for Permits",
    description="Emporia Classic EV charger cut sheet specs for an electrical permit: 48A hardwired on a 60A breaker, 11.5 kW, UL 2594 listing E528156.",
    answer="The Emporia Classic EV charger (model EMEVSE1) delivers 11.5 kW at 240V and 48A when hardwired, requiring a dedicated 60A-or-larger double-pole breaker. Its cut sheet lists UL 2594 certification (E528156), a Type 4 watertight enclosure and an internal GFCI, the details plan reviewers verify.",
    card="Verified electrical specs from the Emporia Classic cut sheet and what plan reviewers check.",
    table_caption="Emporia Classic EV Charger Specs for Permit Plans",
    table_headers=("Spec", "Value on the cut sheet"),
    table_rows=(
        ("Model number", "EMEVSE1 (white) / EMEVSE1-B (black)"),
        ("Input voltage", "208/240 VAC, 50/60 Hz"),
        ("Charge power", "11.5 kW (240 V / 48 A) or 9.6 kW (240 V / 40 A)"),
        ("Required breaker", "Dedicated 60 A+ double-pole for 48 A; 50 A+ for 40 A"),
        ("Install methods", "Hardwired up to 48 A; NEMA 14-50 plug up to 40 A"),
        ("Listing", "UL 2594, file E528156"),
        ("Enclosure / GFCI", "Watertight NEMA Type 4; internal GFCI (15-20 mA)"),
    ),
    sections=(
        ("What plan reviewers verify on the Emporia cut sheet", (
            "Reviewers check that the model number on the cut sheet matches your plans and that the install method matches the amperage: 48 A requires the hardwired setup on a 60 A double-pole breaker, while a NEMA 14-50 plug is limited to 40 A on a 50 A breaker. They confirm the UL 2594 listing (E528156) and compare the charge power to your <a href=\"/permit-documents/load-calculation/\">load calculation</a>. This cut sheet does not state terminal wire sizes, so size conductors from your <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a> and NEC ampacity tables.",
        )),
        ("GFCI note for plug-in installs", (
            "The charger has its own internal GFCI, and Emporia recommends a non-GFCI panel breaker to avoid nuisance trips. If your local code requires a GFCI breaker for a NEMA 14-50 circuit, the cut sheet recommends the hardwired version. See <a href=\"/guides/hardwired-vs-plug-in-ev-charger-permit/\">hardwired vs plug-in EV chargers</a>.",
        )),
        ("Where the cut sheet fits in your packet", (
            "New to the document? Read <a href=\"/guides/what-is-an-appliance-cut-sheet-for-electrical-permit/\">what an appliance cut sheet is for an electrical permit</a>. When you generate an EV charger permit with Permit Packets and pick this charger, the Emporia Classic manufacturer PDF is bundled behind your Equipment Data sheet automatically. <a href=\"/start/?job=ev-charger&role=diy\">Start your EV charger permit packet</a> and preview it free.",
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size", "ev-charger-load-calculator"),
    doc_links=("equipment-cut-sheets", "single-line-diagram"),
    related_slugs=("what-is-an-appliance-cut-sheet-for-electrical-permit", "wallbox-pulsar-plus-cut-sheet-permit"),
    faqs=(
        ("What breaker does the Emporia Classic EV charger need?", "The cut sheet requires a dedicated double-pole breaker of 60 A or more for 48 A charging, or 50 A or more for 40 A."),
        ("Is the Emporia Classic EV charger UL listed?", "The cut sheet lists UL 2594 certification under file E528156, plus FCC, ISED and Energy Star."),
        ("Can the Emporia Classic be hardwired or plugged in?", "Both. Hardwired supports up to 48 A; a NEMA 14-50 plug supports up to 40 A."),
    ),
)

GUIDES["wallbox-pulsar-plus-cut-sheet-permit"] = Guide(
    slug="wallbox-pulsar-plus-cut-sheet-permit", category="concepts", job="ev-charger", role="diy",
    crumb="Wallbox Pulsar Plus Cut Sheet", h1="Wallbox Pulsar Plus Cut Sheet & Specs for Electrical Permits",
    title="Wallbox Pulsar Plus Cut Sheet & Specs for Permits",
    description="Wallbox Pulsar Plus cut sheet specs for an electrical permit: 48A hardwired or 40A, 11.5 kW, UL 2594 and UL 2231, integrated CCID20, NEMA Type 4.",
    answer="The Wallbox Pulsar Plus delivers 11.5 kW at 48A (hardwired) or 9.6 kW at 40A (NEMA 14-50 or hardwired) on 240V. Its cut sheet lists UL 2594 and UL 2231 certification, an integrated CCID20 ground-fault device and a NEMA Type 4 enclosure, which plan reviewers check against your load calculation and diagram.",
    card="Verified electrical specs from the Wallbox Pulsar Plus cut sheet and what plan reviewers check.",
    table_caption="Wallbox Pulsar Plus Specs for Permit Plans",
    table_headers=("Spec", "Value on the cut sheet"),
    table_rows=(
        ("Model", "Pulsar Plus PUP2, 25 ft cable, SAE J1772 or NACS"),
        ("48 A model", "11.5 kW, 48 A rated current, hardwired only"),
        ("40 A model", "9.6 kW, 40 A rated current, NEMA 14-50 or hardwired"),
        ("Voltage", "208/240 V (Level 2), 60 Hz"),
        ("Listing", "UL 2594 and UL 2231 (NRTL)"),
        ("Ground-fault protection", "Integrated CCID20 (20 mA) plus ground monitoring, per UL 2231"),
        ("Enclosure", "NEMA Type 4 per UL 50E, indoor and outdoor"),
    ),
    sections=(
        ("Max power and breaker size for the Pulsar Plus", (
            "The cut sheet gives two ratings: 48 A (11.5 kW) and 40 A (9.6 kW) at 240 V single-phase. The charger is a continuous load, so NEC 625.41 sizes the circuit at 125% of rated current: a 48 A charger needs a 60 A breaker and a 40 A charger needs a 50 A breaker. The cut sheet itself lists ratings, not breaker sizes, so these come from the NEC. For the load calculation, 48 A at 240 V is 11,520 VA and 40 A is 9,600 VA. Check sizes with the <a href=\"/tools/ev-charger-wire-breaker-size/\">EV charger wire calculator</a>.",
        )),
        ("What plan reviewers verify on the Wallbox cut sheet", (
            "Reviewers check three things. First, the continuous load math: the rated current on the sheet must match the breaker and the <a href=\"/permit-documents/load-calculation/\">load calculation</a>. Second, conductor sizing: for the 48 A hardwired setting, a 60 A circuit is commonly drawn with #6 AWG copper at the 75°C column on your <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a>. This datasheet does not state terminal wire range or temperature rating, so confirm those in the installation manual. Third, the UL 2594 and UL 2231 listings, which satisfy the listed-equipment requirement.",
        )),
        ("GFCI, enclosure and local rules", (
            "The Pulsar Plus has an integrated CCID20 charge current interruption device plus ground monitoring, per UL 2231. Whether a separate GFCI breaker is also required depends on the NEC edition and your city's amendments, so confirm with your building department. The NEMA Type 4 rating per UL 50E covers indoor and outdoor mounting. See <a href=\"/guides/hardwired-vs-plug-in-ev-charger-permit/\">hardwired vs plug-in EV chargers</a>.",
        )),
        ("Where the cut sheet fits in your packet", (
            "New to the document? Read <a href=\"/guides/what-is-an-appliance-cut-sheet-for-electrical-permit/\">what an appliance cut sheet is for an electrical permit</a>. When you generate an EV charger permit with Permit Packets and pick this charger, the Wallbox Pulsar Plus manufacturer PDF is bundled behind your Equipment Data sheet automatically. <a href=\"/start/?job=ev-charger&role=diy\">Start your packet</a> or see the <a href=\"/ev-charger-permit/\">EV charger permit page</a>; the preview is free.",
        )),
    ),
    tool_links=("ev-charger-wire-breaker-size", "ev-charger-load-calculator"),
    doc_links=("equipment-cut-sheets", "single-line-diagram"),
    related_slugs=("what-is-an-appliance-cut-sheet-for-electrical-permit", "tesla-wall-connector-gen-3-cut-sheet-permit"),
    faqs=(
        ("Is the Wallbox Pulsar Plus UL listed?", "The cut sheet lists UL 2594 and UL 2231 certification by an NRTL, plus FCC Part 15 Class B and Energy Star."),
        ("Can the Wallbox Pulsar Plus be plugged into a NEMA 14-50?", "The 40 A model can use NEMA 14-50 or be hardwired. The 48 A model is hardwired only."),
        ("Does the Wallbox Pulsar Plus have built-in GFCI?", "Yes. The cut sheet lists an integrated CCID20 (20 mA) plus ground monitoring per UL 2231. Confirm with your city whether a GFCI breaker is also required."),
    ),
)


GUIDES["hot-tub-gfci-disconnect-wire-size-permit-guide"] = Guide(
    slug="hot-tub-gfci-disconnect-wire-size-permit-guide",
    category="diy-tips", job="hot-tub-240v", role="diy",
    crumb="Hot Tub GFCI & Wire Size Guide",
    h1="Hot Tub Electrical Permit Guide: GFCI, Wire Size & 5-Ft Rule",
    title="Hot Tub Electrical Permit Guide: GFCI, Wire & 5-Ft Rule",
    description="NEC Article 680 checklist for hot tub permits: 50A GFCI spa panel, #6 AWG copper wire, insulated green ground and 5-ft disconnect clearance.",
    answer=(
        "A residential hot tub electrical permit requires a dedicated 240V circuit sized at 125% of nameplate current, Class A GFCI protection (NEC 680.44), an insulated copper ground wire outdoors (NEC 680.42), and a maintenance disconnect installed at least 5 feet horizontally from the water (NEC 680.13)."
    ),
    card="NEC Article 680 wiring, 50A GFCI spa panel placement, insulated ground and trench rules.",
    table_caption="NEC Article 680 Hot Tub & Spa Permit Requirements",
    table_headers=("Requirement", "NEC Rule", "Standard 50A Spa Specification"),
    table_rows=(
        ("Overcurrent & GFCI protection", "NEC 680.44", "50 A 2-pole GFCI breaker inside listed outdoor spa panel"),
        ("Circuit conductors (75°C / 60°C)", "NEC 310.16 / 110.14(C)", "#6 AWG Cu (60°C / NM-B) or #8 AWG Cu THWN-2 (75°C conduit)"),
        ("Equipment grounding conductor", "NEC 680.42(A)(1)", "#10 AWG insulated green copper (bare ground prohibited outdoors)"),
        ("Maintenance disconnect location", "NEC 680.13", "Within sight of spa and >= 5 ft horizontally from inside water wall"),
        ("Underground PVC burial cover", "NEC Table 300.5", "18 inches minimum soil cover above Schedule 40/80 PVC"),
    ),
    sections=(
        ("Why outdoor hot tubs require an insulated copper ground wire", (
            "Inside a house, standard Romex (NM-B) uses a bare copper ground wire. For outdoor hot tubs and spas, NEC 680.42(A)(1) prohibits bare ground wires in the branch circuit—you must pull an insulated green copper equipment grounding conductor inside the raceway from the main panel to the spa disconnect and tub.",
            "Size your exact spa circuit and PVC conduit in seconds with our <a href=\"/tools/hot-tub-breaker-wire-size/\">hot tub breaker and wire size calculator</a>.",
        )),
        ("Placement rules for the 50A GFCI spa disconnect (NEC 680.13)", (
            "Plan reviewers reject many <a href=\"/hot-tub-240v-permit/\">hot tub permit packets</a> because the disconnect is drawn too close to the water or around a blind corner. Under NEC 680.13, the disconnect must be readily accessible, within sight of the spa, and at least 5 feet horizontally from the inside wall of the tub.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("hot-tub-breaker-wire-size", "residential-load-calculator"),
    doc_links=("site-plan", "single-line-diagram"),
    related_slugs=("heat-pump-mini-split-electrical-permit-mca-mocp", "ev-charger-trench-depth-conduit-rules-nec-300-5"),
    faqs=(
        ("Can I run Romex (NM-B) to an outdoor hot tub?", "NM-B cable may only be used indoors in dry locations up to the exterior wall transition; outdoors and underground you must transition to Schedule 40/80 PVC or liquidtight conduit with wet-rated THWN-2 conductors."),
        ("Does a hot tub need a neutral wire?", "Most 240V/120V spas with ozonators, stereos, or 120V control boards require a 4-wire feeder (two hots, one insulated neutral, and one insulated green ground). Pure 240V heaters may only need 3 wires—check the spa wiring diagram."),
        ("How is a hot tub counted in the home load calculation?", "The spa's nameplate VA (amps x 240 V) is added to your <a href=\"/permit-documents/load-calculation/\">NEC 220.82 dwelling load calculation</a> to verify your main service has spare capacity."),
    ),
)

GUIDES["heat-pump-mini-split-electrical-permit-mca-mocp"] = Guide(
    slug="heat-pump-mini-split-electrical-permit-mca-mocp",
    category="concepts", job="hot-tub-240v", role="diy",
    crumb="Heat Pump & Mini-Split MCA/MOCP",
    h1="Heat Pump & Mini-Split Electrical Permits: MCA vs. MOCP",
    title="Heat Pump & Mini-Split Electrical Permits: MCA vs MOCP",
    description="How to read MCA (Minimum Circuit Ampacity) and MOCP (Maximum Overcurrent Protection) on a heat pump or mini-split nameplate for NEC 440 permits.",
    answer=(
        "Under NEC Article 440, heat pump and mini-split circuits are sized from two numbers on the outdoor condenser nameplate rather than standard 125% continuous load math: Minimum Circuit Ampacity (MCA) sets the minimum wire ampacity, and Maximum Overcurrent Protection (MOCP) sets the maximum 2-pole breaker size."
    ),
    card="Size wire from MCA and pick the breaker from MOCP under NEC 440.22 for heat pumps and mini-splits.",
    table_caption="Reading Heat Pump & Mini-Split Nameplate Ratings (NEC Article 440)",
    table_headers=("Nameplate Rating", "What It Governs", "NEC Code Rule"),
    table_rows=(
        ("MCA (Minimum Circuit Ampacity)", "Minimum copper wire gauge (e.g., 19 A MCA -> #12 AWG Cu)", "NEC 440.32 (compressor + fan motor loads)"),
        ("MOCP / Max Fuse / Max Breaker", "Maximum 2-pole breaker size (e.g., 30 A MOCP -> 25 A or 30 A breaker)", "NEC 440.22 (allows motor starting inrush)"),
        ("Service disconnect", "Weatherproof pull-out or toggle disconnect within sight of condenser", "NEC 440.14 (within sight and readily accessible)"),
        ("Outdoor GFCI receptacle", "2023 NEC 210.8(F) requires GFCI on outdoor HVAC outlets in adopting cities", "NEC 210.8(F) (check local city amendments)"),
    ),
    sections=(
        ("Why a 30A breaker on #12 AWG wire is legal for a mini-split", (
            "On standard branch circuits, NEC 240.4(D) limits #12 AWG copper wire to a 20 A breaker. However, hermetic refrigerant motor-compressors governed by NEC Article 440 are an explicit exception in NEC 240.4(G): if a mini-split nameplate lists 18 A MCA and 30 A MOCP, #12 AWG copper wire paired with a 30 A 2-pole breaker is completely code-compliant.",
            "When you enter your heat pump or mini-split in our <a href=\"/hot-tub-240v-permit/\">240V appliance circuit permit generator</a>, the tool checks your breaker directly against the nameplate MCA and MOCP.",
        )),
        ("Disconnect and whip requirements at the outdoor unit", (
            "NEC 440.14 requires a disconnecting means within sight of and readily accessible from the outdoor heat pump or mini-split condenser, typically connected with a 6-foot nonmetallic liquidtight flexible conduit (LFNC) whip.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("residential-load-calculator", "hot-tub-breaker-wire-size"),
    doc_links=("single-line-diagram", "equipment-cut-sheets"),
    related_slugs=("hot-tub-gfci-disconnect-wire-size-permit-guide", "2023-nec-and-california-electrical-code-permit-guide"),
    faqs=(
        ("Do I need to attach the mini-split spec sheet to my permit?", "Yes. Plan reviewers verify MCA, MOCP, and voltage directly against the manufacturer's <a href=\"/permit-documents/equipment-cut-sheets/\">equipment cut sheet</a>."),
        ("Does replacing a gas furnace with a heat pump require a panel upgrade?", "Not always. Run your home's existing loads plus the heat pump nameplate VA in our <a href=\"/tools/residential-load-calculator/\">NEC 220.82 load calculator</a> to see if your current 100A or 200A panel passes."),
        ("Where does the outdoor disconnect need to be mounted?", "Within sight of the condenser (visible and within 50 feet) and never mounted on the removable access panel of the equipment itself."),
    ),
)


GUIDES["best-subpanel-sizes-detached-garage-workshop-adu"] = Guide(
    slug="best-subpanel-sizes-detached-garage-workshop-adu",
    category="best-of", job="subpanel", role="diy",
    crumb="Best Subpanel Sizes (60A vs 100A)",
    h1="Best Subpanel Sizes for a Detached Garage, Workshop or ADU",
    title="Best Subpanel Sizes for a Detached Garage, Workshop or ADU",
    description="Compare 60A, 100A and 125A subpanels for detached garages, workshops and ADUs: feeder wire sizes, conduit, ground rods and NEC 250.32 rules.",
    answer=(
        "A 60A subpanel (fed with #4 AWG aluminum or #6 AWG copper) covers a single 48A EV charger plus garage lights and outlets, while a 100A subpanel (#1 AWG aluminum or #3 AWG copper) is the best all-around choice for a detached garage, woodworking shop, or ADU running multiple 240V loads simultaneously."
    ),
    card="Compare 60A, 100A and 125A subpanels with feeder wire, conduit and ground rod checklists.",
    table_caption="60A vs. 100A vs. 125A Subpanel Feeder Comparison (75°C THWN-2)",
    table_headers=("Subpanel Size", "Aluminum Feeder Wire", "Copper Feeder Wire", "PVC Conduit (4-Wire)", "Best Use Case"),
    table_rows=(
        ("60 A Subpanel", "#4 AWG Al (3) + #8 Al EGC", "#6 AWG Cu (3) + #10 Cu EGC", "1 inch PVC", "Garage EV charger + 120V lighting & receptacles"),
        ("100 A Subpanel", "#1 AWG Al (3) + #6 Al EGC", "#3 AWG Cu (3) + #8 Cu EGC", "1-1/4 inch PVC", "Detached garage with EV charger + mini-split + tools"),
        ("125 A Subpanel", "#2/0 AWG Al (3) + #6 Al EGC", "#1 AWG Cu (3) + #6 Cu EGC", "1-1/2 inch PVC", "Full studio ADU with electric range, dryer & heat pump"),
    ),
    listicle_items=(
        "60 A 12-Space / 24-Circuit Subpanel — Compact feeder for a single EV charger and garage outlets",
        "100 A 20-Space / 40-Circuit Subpanel — Most versatile size for detached garages and workshops",
        "125 A 24-Space / 48-Circuit Subpanel — High-capacity feeder for ADUs and multi-circuit additions",
    ),
    sections=(
        ("Why 100A aluminum is the sweet spot for detached garages", (
            "Because trenching labor is the biggest cost of feeding a detached garage, upsizing from a 60 A feeder to a 100 A feeder using #1 AWG aluminum THWN-2 conductors in 1-1/4 in PVC adds very little material cost while doubling your future circuit headroom.",
            "Test your exact run length and voltage drop in our <a href=\"/tools/subpanel-feeder-calculator/\">free subpanel feeder calculator</a> before ordering wire.",
        )),
        ("Three mandatory NEC checks on every detached subpanel permit", (
            "When reviewing a <a href=\"/subpanel-permit/\">subpanel permit packet</a> for a detached building, inspectors always verify three rules: isolated neutral and ground buses with the bonding screw removed (NEC 250.24(A)(5)), a local disconnecting means at the building (NEC 225.31), and two 8-foot ground rods spaced at least 6 feet apart bonded to the subpanel ground bar (NEC 250.32 & 250.53).",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("subpanel-feeder-calculator", "residential-load-calculator"),
    doc_links=("single-line-diagram", "site-plan"),
    related_slugs=("electrical-permit-cost-and-timeline-by-city", "subpanel-vs-200a-panel-upgrade"),
    faqs=(
        ("Can I put a 100A subpanel on a 100A main service?", "Code allows a 100 A feeder breaker on a 100 A main panel if your <a href=\"/permit-documents/load-calculation/\">NEC 220.82 dwelling load calculation</a> proves the combined house and garage demand stays under 100 A."),
        ("Do I need a main breaker inside the detached garage subpanel?", "If the subpanel has more than 6 breakers (or serves as the building disconnect under NEC 225.31), installing a main-breaker subpanel (e.g., 100 A main breaker) provides a single-throw disconnect at the detached structure."),
        ("Can I reuse an existing 3-wire feeder to a detached garage?", "No. New subpanel feeders must be 4-wire (two hots, insulated neutral, and separate equipment grounding conductor) under NEC 250.32(B)."),
    ),
)

GUIDES["electrical-permit-cost-and-timeline-by-city"] = Guide(
    slug="electrical-permit-cost-and-timeline-by-city",
    category="local-guides", job="ev-charger", role="diy",
    crumb="Permit Cost & Timeline by City",
    h1="Residential Electrical Permit Cost & Timeline by City (2026)",
    title="Residential Electrical Permit Cost and Timeline by City",
    description="Compare residential electrical permit fees, online portals and plan-check timelines in Bellevue, San Francisco, Los Angeles, San Diego and Austin.",
    answer=(
        "Residential electrical permit fees typically range from $75 to $350 depending on circuit count and valuation, with online over-the-counter or express review taking 1 to 5 business days in cities like Los Angeles, Bellevue, and Austin when complete plans are uploaded to the city portal."
    ),
    card="Compare city permit portals, review workflows and fee structures across major US cities.",
    table_caption="Permit Portal & Review Workflow Across Major US Cities",
    table_headers=("City & Department", "Online Portal", "Notable Submittal Rule"),
    table_rows=(
        ("Los Angeles, CA (LADBS)", "ePlanLA", "Express permits available for standard residential EV chargers"),
        ("San Diego, CA (DSD)", "OpenDSD", "Fees based on scope per Information Bulletin 501; SDG&E coordination for upgrades"),
        ("San Francisco, CA (DBI)", "DBI Online Submittal", "Licensed C-10 contractor required; Form E-02 + PG&E EUSERC rules"),
        ("Bellevue, WA (Development Services)", "MyBuildingPermit.com", "PSE Form 7517 meter-main check for service upgrades"),
        ("Austin, TX (Austin DSD)", "Austin Build + Connect (AB+C)", "Austin Energy coordination required for service upgrades"),
        ("Mesa & Chandler, AZ", "DIMES / City Online Portal", "109°F outdoor ambient conductor derating; single combined PDF in Chandler"),
    ),
    sections=(
        ("What drives residential electrical permit fees?", (
            "Most municipal building departments calculate electrical permit fees using either a flat residential trade fee (common for single EV charger circuits) or a circuit-and-valuation schedule that adds small line-item fees for each new breaker, subpanel, or service ampere rating.",
            "Browse your city in our <a href=\"/permits/\">electrical permits by city directory</a>—including <a href=\"/permits/ca/los-angeles/ev-charger/\">Los Angeles</a>, <a href=\"/permits/ca/san-diego/ev-charger/\">San Diego</a>, <a href=\"/permits/tx/austin/ev-charger/\">Austin</a>, and <a href=\"/permits/wa/bellevue/ev-charger/\">Bellevue</a>—to view direct portal links and fee notes.",
        )),
        ("How to avoid multi-week plan-check delays", (
            "The biggest source of delay is not the city's initial queue—it is receiving a correction notice for a missing <a href=\"/permit-documents/load-calculation/\">NEC 220 load calculation</a>, unscaled <a href=\"/permit-documents/site-plan/\">site plan</a>, or missing UL cut sheet, which resets your review clock. Generating a complete <a href=\"/ev-charger-permit/\">permit packet</a> before applying keeps submittals clean on the first pass.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("ev-charger-load-calculator", "residential-load-calculator"),
    doc_links=("site-plan", "load-calculation"),
    related_slugs=("best-subpanel-sizes-detached-garage-workshop-adu", "cities-allowing-owner-builder-ev-charger-permits"),
    faqs=(
        ("Does Permit Packets include the city's permit filing fee?", "No. Permit Packets ($39, $89, or $169) drafts your permit plans and calculations. You pay your city's permit fee directly to the building department when you file."),
        ("Can I submit my permit packet online?", "Yes. Most cities accept PDF uploads through portals such as OpenDSD, ePlanLA, MyBuildingPermit.com, AB+C, or Accela Citizen Access. Your order page includes both one combined PDF and a split-file ZIP."),
        ("How many inspections are required after the permit is issued?", "Typically one final electrical inspection for an indoor EV charger or panel swap, or two inspections (underground trench rough-in + final) when trenching conduit to a detached garage or hot tub."),
    ),
)


GUIDES["how-much-does-an-electrical-permit-cost"] = Guide(
    slug="how-much-does-an-electrical-permit-cost",
    category="local-guides", job="ev-charger", role="diy",
    crumb="How Much Does a Permit Cost?",
    h1="How Much Does a Residential Electrical Permit Cost? (2026)",
    title="How Much Does a Residential Electrical Permit Cost? (2026)",
    description="Residential electrical permit fees range from $50 to $350 by city and project type. See typical city filing fees, plan-check costs and drafting options.",
    answer=(
        "A residential electrical permit typically costs $50 to $350 in municipal filing fees depending on whether you are adding a single 240V EV charger circuit or upgrading to a 200A service. When plans are required, automated permit drafting starts at $39 to $169 compared with $300 to $500+ for traditional CAD drafters."
    ),
    card="Breakdown of city electrical permit fees, plan-review charges and drafting costs by project type.",
    table_caption="Typical Residential Electrical Permit & Plan Preparation Costs",
    table_headers=("Project Type", "Typical City Filing Fee", "Plan Drafting Cost (Permit Packets)", "Traditional CAD Drafter"),
    table_rows=(
        ("Level 2 EV Charger (240V Circuit)", "$75 - $225", "$89 Instant ($169 City-Checked)", "$300 - $500+"),
        ("200A Panel / Service Upgrade", "$125 - $350", "$89 Instant ($169 City-Checked)", "$350 - $600+"),
        ("Detached Garage / ADU Subpanel", "$100 - $275", "$89 Instant ($169 City-Checked)", "$300 - $500+"),
        ("Hot Tub, Sauna or Heat Pump Circuit", "$75 - $200", "$89 Instant ($169 City-Checked)", "$300 - $450+"),
        ("Load Calc & Panel Capacity Audit Only", "N/A (pre-quote check)", "$39 Load Calc & Panel Audit", "$150 - $250"),
    ),
    sections=(
        ("How building departments calculate electrical permit fees", (
            "Municipal building departments use two common fee models: a flat residential trade permit fee (often $75 to $175 for an express EV charger or 240V circuit) or a line-item circuit and service ampere schedule that adds small fees per breaker, subpanel, or 200A service switch.",
            "Some cities also charge a separate plan-review fee (typically 25% to 65% of the permit fee) when drawings are required. Check your city's fee notes in our <a href=\"/permits/\">electrical permits by city directory</a>.",
        )),
        ("How to avoid paying twice for plans or service upgrades", (
            "Before collecting contractor quotes for a new EV charger or heat pump, run your home through our <a href=\"/tools/ev-charger-load-calculator/\">free EV charger load calculator</a> or order the $39 Load Calc & Panel Audit. Knowing your NEC 220 spare capacity up front prevents unnecessary $3,500+ service upgrades and keeps <a href=\"/ev-charger-permit/\">permit plan preparation</a> predictable.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("ev-charger-load-calculator", "residential-load-calculator"),
    doc_links=("load-calculation", "site-plan"),
    related_slugs=("do-you-need-an-engineer-stamp-for-residential-electrical-permit", "electrical-permit-cost-and-timeline-by-city"),
    faqs=(
        ("Does Permit Packets include the city's permit fee?", "No. You pay Permit Packets ($39, $89, or $169) for your permit plans and calculations, and pay the municipal filing fee directly to your city when submitting."),
        ("Are there any hidden subscription fees?", "No. Every package is a one-time purchase per project, and you can generate a full watermarked preview free before paying."),
        ("What if my city rejects my permit application?", "You can edit your inputs and regenerate your packet at any time, and orders can be refunded in full before you download the clean packet."),
    ),
)

GUIDES["do-you-need-an-engineer-stamp-for-residential-electrical-permit"] = Guide(
    slug="do-you-need-an-engineer-stamp-for-residential-electrical-permit",
    category="comparisons", job="panel-upgrade", role="hiring",
    crumb="Do You Need a PE Stamp?",
    h1="Do You Need an Engineer Stamp for a Residential Permit?",
    title="Do You Need an Engineer Stamp for a Residential Permit?",
    description="Find out when a city building department requires a PE stamp vs standard NEC load calculations, single-line diagrams and parcel site plans for homes.",
    answer=(
        "Most single-family residential electrical permits—including Level 2 EV chargers, 200A panel upgrades, subpanels, and hot tubs—do not require a Professional Engineer (PE) stamp. City plan reviewers instead check an NEC Article 220 load calculation, single-line diagram, scaled parcel site plan, and UL equipment cut sheets."
    ),
    card="When standard NEC plans pass plan check vs. when a licensed Electrical Engineer stamp is required.",
    table_caption="Standard NEC Plans vs. PE-Stamped Engineering Drawings",
    table_headers=("Project Scope", "PE Stamp Required?", "What the Building Department Reviews"),
    table_rows=(
        ("Single-Family Level 2 EV Charger (up to 48A–80A)", "Rarely (standard plans accepted)", "Parcel site plan, 1-line diagram, NEC 220 load calc, UL cut sheet"),
        ("200A Residential Service / Panel Upgrade", "Rarely (400A+ services may trigger PE)", "Riser diagram, NEC 220 load calc, grounding, NEC 230.67 SPD"),
        ("Detached Garage or ADU Subpanel (60A–125A)", "No (standard residential plans)", "Feeder schedule, voltage drop, site plan, NEC 250.32 grounding"),
        ("Hot Tub, Sauna or Heat Pump 240V Circuit", "No (standard residential plans)", "1-line diagram, GFCI / disconnect clearance, load calc"),
        ("Commercial EV Charging / Multi-Family / 400A+ Service", "Yes (typically requires EE stamp)", "Fault current study, coordination, stamped electrical sheets"),
    ),
    sections=(
        ("Why single-family electrical permits rarely need a PE stamp", (
            "State engineering acts exempt standard one- and two-family residential electrical installations from mandatory Professional Engineer (PE) stamping because conductor sizing, overcurrent protection, and dwelling demand factors are prescriptive under the National Electrical Code.",
            "Plan examiners simply need clear, legible documentation showing that the installation complies with the NEC—specifically an <a href=\"/permit-documents/load-calculation/\">NEC 220 load calculation</a>, a <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a>, and a scaled <a href=\"/permit-documents/site-plan/\">site plan</a>.",
        )),
        ("When you should hire a licensed Professional Engineer", (
            "If you are upgrading a residential service to 400 A or 600 A, installing commercial Level 2 or DC fast chargers, wiring a multi-family condo building, or responding to a city correction that explicitly requests a California or state PE seal, hire a local licensed Electrical Engineer.",
            "For standard 100 A to 225 A single-family projects, <a href=\"/panel-upgrade-permit/\">Permit Packets</a> generates complete, code-referenced drawings in minutes without paying $500+ for stamped commercial engineering.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("residential-load-calculator", "solar-120-percent-rule-calculator"),
    doc_links=("single-line-diagram", "load-calculation"),
    related_slugs=("how-much-does-an-electrical-permit-cost", "owner-builder-permit-vs-licensed-electrician"),
    faqs=(
        ("Is Permit Packets PE-stamped?", "No. Permit Packets is an automated drafting and NEC calculation tool, and every sheet clearly states that it is not PE-stamped."),
        ("How do I check if my city requires a PE stamp before buying?", "Check your city's checklist in our <a href=\"/permits/\">city electrical permit guides</a> or preview your packet free—Sheet E-1 displays your city's published checklist items before you pay."),
        ("Can a licensed electrician submit non-stamped plans?", "Yes. On residential projects, licensed electrical contractors routinely submit non-stamped single-line diagrams, load calculations, and site plans."),
    ),
)


GUIDES["ev-charger-permit-packet-checklist-for-homeowners"] = Guide(
    slug="ev-charger-permit-packet-checklist-for-homeowners",
    category="diy-tips", job="ev-charger", role="diy",
    crumb="EV Charger Permit Checklist",
    h1="EV Charger Permit Packet Checklist for Homeowners (2026)",
    title="EV Charger Permit Packet Checklist for Homeowners (2026)",
    description="Use this complete homeowner checklist to prepare an EV charger permit packet: GIS site plan, single-line diagram, NEC 220 load calc and UL cut sheet.",
    answer=(
        "A complete residential EV charger permit packet includes five core items: a filled city permit application, a scaled parcel site plan showing the panel and charger, a single-line diagram with wire and conduit sizes, an NEC Article 220 load calculation, and the charger manufacturer's UL 2594 specification sheet."
    ),
    card="Step-by-step homeowner submittal checklist covering all 5 required EV charger permit documents.",
    listicle_items=(
        "1. Completed City Electrical Permit Application & Owner-Builder Declaration",
        "2. Scaled Parcel Site Plan Showing Main Panel, Charger Location & Wire Route",
        "3. Single-Line Diagram with 125% Continuous Breaker, Wire Gauge & Conduit Schedule",
        "4. NEC Article 220 Dwelling Load Calculation Proving Service Capacity",
        "5. Manufacturer UL 2594 / NRTL Specification Cut Sheet",
    ),
    sections=(
        ("1. Gather your panel and charger details before opening the wizard", (
            "Before starting your <a href=\"/ev-charger-permit/\">EV charger permit packet</a>, snap a photo of the UL label inside your main electrical panel door to confirm your main breaker rating (100 A, 150 A, or 200 A) and verify two adjacent open breaker slots.",
            "Next, confirm your charger's maximum charging current (32 A, 40 A, or 48 A) and run your home's square footage and electric appliances through our <a href=\"/tools/ev-charger-load-calculator/\">free EV charger load calculator</a>.",
        )),
        ("2. Verify the five core sheets in your packet", (
            "City plan examiners check that your <a href=\"/permit-documents/site-plan/\">site plan</a>, <a href=\"/permit-documents/single-line-diagram/\">single-line diagram</a>, <a href=\"/permit-documents/load-calculation/\">load calculation</a>, and <a href=\"/permit-documents/equipment-cut-sheets/\">UL cut sheet</a> match each other—for example, a 48 A charger must show a 60 A 2-pole breaker and #6 AWG copper wire across every sheet.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("ev-charger-load-calculator", "ev-charger-wire-breaker-size"),
    doc_links=("site-plan", "equipment-cut-sheets"),
    related_slugs=("hardwired-vs-plug-in-ev-charger-permit", "7-reasons-electrical-permits-fail-plan-check"),
    faqs=(
        ("How long does it take to build the EV charger packet?", "Most homeowners enter their address, mark the panel and charger pins on the aerial map, and generate their free watermarked preview in under 5 minutes."),
        ("What if my city wants each sheet uploaded as a separate PDF?", "Every paid order includes both one combined PDF and a split-file ZIP with each sheet saved as an individually named PDF."),
        ("Where do I sign as an owner-builder?", "When you select 'I'm a homeowner doing the work myself', every drawing sheet prints an Owner-Builder signature and date line in the title block."),
    ),
)

GUIDES["sauna-electrical-permit-wire-breaker-gfci-rules"] = Guide(
    slug="sauna-electrical-permit-wire-breaker-gfci-rules",
    category="diy-tips", job="hot-tub-240v", role="diy",
    crumb="Sauna Electrical Permit Guide",
    h1="Sauna Electrical Permit Guide: Wire, Breaker & GFCI Rules",
    title="Sauna Electrical Permit Guide: Wire, Breaker and GFCI Rules",
    description="Size wire, breakers and conduit for an electric sauna heater under NEC 424.4: 240V continuous load math, copper wire temperature ratings and GFCI rules.",
    answer=(
        "An electric sauna heater requires a dedicated 240V circuit sized at 125% of its nameplate amperage under NEC 424.4(B), high-temperature copper conductors matching the heater terminal rating, and a local disconnecting means. Unlike hot tubs, most sauna heater manufacturers prohibit GFCI breakers—follow the UL listing manual."
    ),
    card="Wire gauge, breaker sizing, 90°C heater whip rules and GFCI guidance for electric sauna permits.",
    table_caption="Typical 240V Electric Sauna Heater Circuit Sizing (NEC 424.4)",
    table_headers=("Sauna Heater Output", "Nameplate Amps (240V)", "Breaker Size (125%)", "Copper Wire (75°C)"),
    table_rows=(
        ("6.0 kW Heater", "25.0 A", "35 A or 40 A 2-pole", "#8 AWG Cu THWN-2"),
        ("8.0 kW Heater", "33.3 A", "45 A or 50 A 2-pole", "#8 AWG Cu (75°C) or #6 AWG Cu"),
        ("9.0 kW Heater", "37.5 A", "50 A 2-pole", "#8 AWG Cu (75°C) or #6 AWG Cu"),
    ),
    sections=(
        ("Why sauna heaters have strict wire temperature and GFCI rules", (
            "Electric sauna heaters operate in high ambient heat and are classified as continuous fixed electric space-heating equipment under NEC 424.4(B), requiring 125% circuit sizing. Many UL 875 sauna heaters require 90°C-rated copper conductors inside the sauna wall cavity and explicitly prohibit GFCI breakers in their installation manual because moisture sensors and heating elements can cause nuisance trips.",
            "Verify your breaker and wire size with our <a href=\"/tools/hot-tub-breaker-wire-size/\">240V spa and sauna circuit calculator</a> and always attach the heater's UL specification sheet.",
        )),
        ("No receptacles inside the sauna room and disconnect placement", (
            "Under NEC 680 / UL 875 installation rules, standard 120V receptacles are prohibited inside a sauna room, and a disconnecting means must be accessible outside the sauna or at the panel. Generate a complete <a href=\"/hot-tub-240v-permit/\">240V appliance circuit permit packet</a> with your sauna's kW rating pre-filled.",
        )),
        _EXTRA_SEC,
    ),
    tool_links=("hot-tub-breaker-wire-size", "conduit-fill-trench-depth-calculator"),
    doc_links=("single-line-diagram", "equipment-cut-sheets"),
    related_slugs=("hot-tub-gfci-disconnect-wire-size-permit-guide", "ev-charger-trench-depth-conduit-rules-nec-300-5"),
    faqs=(
        ("Should I put a GFCI breaker on a hardwired electric sauna?", "Only if the sauna manufacturer's UL installation instructions permit or require it—most traditional Finnish sauna heaters (such as Harvia and Finlandia) instruct installers not to use GFCI breakers on hardwired units."),
        ("Can I use aluminum wire to feed a sauna heater?", "No. Sauna heater terminals are rated for copper conductors only; run copper wire from the breaker or junction box to the heater."),
        ("Does an outdoor barrel sauna need a trench permit?", "If you run underground PVC conduit from the house to an outdoor sauna, your city will inspect the 18-inch trench depth (NEC Table 300.5) before backfilling."),
    ),
)


GUIDES["how-to-check-if-panel-can-handle-ev-charger"] = _rep(
    GUIDES["how-to-check-if-panel-can-handle-ev-charger"],
    related_slugs=("ev-charger-permit-packet-checklist-for-homeowners", "how-to-read-electrical-panel-label-aic-bus-rating"),
)
GUIDES["7-reasons-electrical-permits-fail-plan-check"] = _rep(
    GUIDES["7-reasons-electrical-permits-fail-plan-check"],
    related_slugs=("ev-charger-permit-packet-checklist-for-homeowners", "how-to-check-if-panel-can-handle-ev-charger"),
)


GUIDES["hot-tub-gfci-disconnect-wire-size-permit-guide"] = _rep(
    GUIDES["hot-tub-gfci-disconnect-wire-size-permit-guide"],
    related_slugs=("sauna-electrical-permit-wire-breaker-gfci-rules", "heat-pump-mini-split-electrical-permit-mca-mocp"),
)
GUIDES["heat-pump-mini-split-electrical-permit-mca-mocp"] = _rep(
    GUIDES["heat-pump-mini-split-electrical-permit-mca-mocp"],
    related_slugs=("sauna-electrical-permit-wire-breaker-gfci-rules", "hot-tub-gfci-disconnect-wire-size-permit-guide"),
)
