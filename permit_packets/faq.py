"""The homepage FAQ. The page and its FAQPage structured data both read this list, so they never differ.

Answers may hold inline HTML (links); the structured data gets the plain text."""
from __future__ import annotations

from permit_packets.content import CITY_CHANGES_ANSWER, POSITIONING

FAQ: list[tuple[str, str]] = [
    ("Do I need an electrician?",
     POSITIONING + " Who can file depends on your city. Many let homeowners file for work they do themselves on their own home; "
     'some require a licensed electrician for all electrical work. See <a href="/permits/">the permit rules for your city</a>.'),
    ("What's in a packet?",
     'A cover sheet with code notes, a site plan on aerial imagery with your lot lines, a single-line diagram, an NEC Article 220 load calculation with panel schedule, and the manufacturer cut sheets, as one PDF or a ZIP of individual files.'),
    ('How long does it take?',
     'Most packets are generated in under 5 minutes. The 24-Hour City-Checked Packet is reviewed and released within 24 hours.'),
    ('Is this stamped by an engineer?',
     "No. It's an automated drafting and NEC calculation tool, not a PE-stamped document. Some cities or jobs need a stamp or a licensed electrician's review; check with your building department."),
    ('Who submits it to the city?',
     "You do. After you pay, your order page gives you the clean PDF, the individual files, the city's submission steps and copy-paste fields for the portal."),
    ('Which cities does it cover?',
     "Any U.S. address works. Cities we've set up use their published checklist; everywhere else uses a general checklist, so confirm local requirements with your building department."),
    ('Can a homeowner pull their own permit?',
     "Many cities allow owner-builder permits for a home you live in, and rules vary. Choose \"I'm a homeowner doing the work myself\" when the wizard asks who the packet is for, and the packet prints your name with no license number."),
    ('Can my electrician use it?',
     "Yes. Choose \"I'm an electrician\" (or the contractor option) and the packet prints their license number in the title block."),
    ('How does payment work?',
     'You pay securely through Whop. Once the payment goes through, your order unlocks automatically. We email you the link to your order page; lost it? Use Find my order.'),
    ('Can I get a refund?',
     'Yes, a full refund if you ask before downloading your clean packet. 24-Hour City-Checked orders can be refunded any time before they\'re released. See the <a href="/refund/">Refund Policy</a>.'),
    ('What if my city asks for changes?',
     CITY_CHANGES_ANSWER),
]
