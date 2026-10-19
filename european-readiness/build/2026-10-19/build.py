from __future__ import annotations

import hashlib
import io
import json
import os
import re
import shutil
from pathlib import Path

import fitz
from pypdf import PdfReader, PdfWriter
from reportlab.lib import colors
from reportlab.lib.colors import HexColor
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.pdfbase.pdfmetrics import stringWidth
from reportlab.pdfgen import canvas
from reportlab.platypus import (
    KeepTogether,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

ROOT = Path(__file__).resolve().parents[3]
SECTION = ROOT / "european-readiness"
BUILD = SECTION / "build" / "2026-10-19"
TMP = BUILD / "tmp"
TMP.mkdir(parents=True, exist_ok=True)

DATE_ISO = "2026-10-19"
DATE_LONG = "Monday, October 19, 2026"
CUTOFF = "October 19, 2026, 10:25 AM EDT"
DAILY_WINDOW = "October 18, 2026, 2:05 PM EDT through October 19, 2026, 10:25 AM EDT"
REGISTER_WINDOW = "August 19, 2026, 12:00 AM EDT through October 19, 2026, 10:25 AM EDT"
PDF_NAME = "Europe_Readiness_Daily_2026-10-19.pdf"
PDF_PATH = SECTION / "editions" / PDF_NAME
PREV_PDF = SECTION / "editions" / "Europe_Readiness_Daily_2026-10-18.pdf"
DATED_DIR = SECTION / DATE_ISO
DATED_PAGE = DATED_DIR / "index.html"
LANDING = SECTION / "index.html"
EDITIONS = SECTION / "editions.json"

NAVY = HexColor("#0B2538")
SLATE = HexColor("#40576A")
GOLD = HexColor("#A66A00")
LIGHT = HexColor("#F4F6F7")
RULE = HexColor("#D7DEE3")
TEXT = HexColor("#1B252C")
LINK = HexColor("#1B658A")
WHITE = colors.white

URLS = {
    "reuters_energy": "https://www.reuters.com/world/europe/russian-strike-kills-woman-hits-kyiv-subway-station-mayor-says-2026-10-19/",
    "ap_energy": "https://apnews.com/article/russia-ukraine-war-kyiv-attack-b041f78e5d037a0f3377b7108eac1dc7",
    "reuters_lithuania": "https://www.reuters.com/business/media-telecom/lithuania-increase-security-critical-infrastructure-prime-minister-says-2026-10-19/",
    "nato_hybrid": "https://www.nato.int/en/news-and-events/articles/news/2026/10/19/nato-allies-and-partners-meet-in-bucharest-to-strengthen-response-to-russias-hybrid-activities",
    "romania_update": "https://english.mapn.ro/cpresa/6892_Press-Release---UPDATE",
    "reuters_summit": "https://www.reuters.com/world/china/putin-proposes-summit-with-trump-xi-discuss-ukraine-deal-wsj-says-2026-10-19/",
    "ap_russia_drones": "https://apnews.com/article/russia-ukraine-war-energy-diesel-trump-f813d3725b8b5f23958a68a95729fd0d",
    "archive": "https://winston-pickett.github.io/european-readiness/",
    "edition": "https://winston-pickett.github.io/european-readiness/2026-10-19/",
    "pdf": "https://winston-pickett.github.io/european-readiness/editions/Europe_Readiness_Daily_2026-10-19.pdf",
}

styles = getSampleStyleSheet()
styles.add(ParagraphStyle(name="ERTitle", parent=styles["Title"], fontName="Helvetica-Bold", fontSize=26, leading=29, textColor=NAVY, spaceAfter=7))
styles.add(ParagraphStyle(name="ERSubtitle", parent=styles["Normal"], fontName="Helvetica", fontSize=12, leading=15, textColor=SLATE, spaceAfter=12))
styles.add(ParagraphStyle(name="ERDate", parent=styles["Normal"], fontName="Helvetica-Bold", fontSize=12, leading=15, textColor=GOLD, spaceAfter=12))
styles.add(ParagraphStyle(name="ERH1", parent=styles["Heading1"], fontName="Helvetica-Bold", fontSize=16.5, leading=20, textColor=NAVY, spaceBefore=10, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="ERH2", parent=styles["Heading2"], fontName="Helvetica-Bold", fontSize=12.2, leading=15, textColor=NAVY, spaceBefore=8, spaceAfter=4, keepWithNext=True))
styles.add(ParagraphStyle(name="ERBody", parent=styles["BodyText"], fontName="Helvetica", fontSize=10.3, leading=14.2, textColor=TEXT, spaceAfter=7))
styles.add(ParagraphStyle(name="ERSmall", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.4, leading=11.2, textColor=SLATE, spaceAfter=5))
styles.add(ParagraphStyle(name="ERCard", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.7, leading=13.2, textColor=TEXT, leftIndent=9, rightIndent=9, borderColor=RULE, borderWidth=0.7, borderPadding=8, backColor=LIGHT, spaceAfter=8))
styles.add(ParagraphStyle(name="ERSource", parent=styles["BodyText"], fontName="Helvetica", fontSize=8.2, leading=10.8, textColor=SLATE, spaceAfter=4))
styles.add(ParagraphStyle(name="ERCenter", parent=styles["BodyText"], fontName="Helvetica", fontSize=9.2, leading=12, alignment=TA_CENTER, textColor=SLATE))


def esc(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def link(label: str, url: str) -> str:
    return f'<link href="{url}" color="#1B658A"><u>{esc(label)}</u></link>'


def p(text: str, style: str = "ERBody") -> Paragraph:
    return Paragraph(text, styles[style])


def h1(text: str) -> Paragraph:
    return Paragraph(text, styles["ERH1"])


def h2(text: str) -> Paragraph:
    return Paragraph(text, styles["ERH2"])


def card(title: str, body: str, source_pairs: list[tuple[str, str]] | None = None) -> KeepTogether:
    source_html = ""
    if source_pairs:
        source_html = "<br/><b>Sources:</b> " + " | ".join(link(a, u) for a, u in source_pairs)
    return KeepTogether([p(f"<b>{esc(title)}</b><br/>{body}{source_html}", "ERCard")])


class BookmarkDoc(SimpleDocTemplate):
    def afterFlowable(self, flowable):
        if isinstance(flowable, Paragraph) and flowable.style.name in {"ERH1", "ERH2"}:
            text = flowable.getPlainText()
            key = "b_" + hashlib.md5((text + str(self.page)).encode()).hexdigest()
            self.canv.bookmarkPage(key)
            level = 0 if flowable.style.name == "ERH1" else 1
            self.canv.addOutlineEntry(text, key, level=level, closed=False)


def doc(path: Path) -> BookmarkDoc:
    return BookmarkDoc(
        str(path),
        pagesize=letter,
        leftMargin=0.70 * inch,
        rightMargin=0.70 * inch,
        topMargin=0.65 * inch,
        bottomMargin=0.58 * inch,
        title="Europe Readiness Daily 2026-10-19",
        author="",
        subject="",
        keywords="",
    )


def build_front(path: Path) -> None:
    story = []
    story += [p("EUROPE READINESS DAILY", "ERSmall"), p("Europe Readiness Daily", "ERTitle"), p("Verified preparations, escalation signals, and fact checks", "ERSubtitle"), p(DATE_LONG, "ERDate")]
    story += [p("Public-source awareness and planning brief. Not an official intelligence bulletin.", "ERCard")]
    purpose = (
        "Europe Readiness Daily is published to support awareness and practical planning, not to create fear or suggest that war is inevitable. "
        "This October 19 edition covers NATO and European allies, European Union institutions, the United States, Russia, Belarus and directly relevant Ukraine and Moldova developments, with particular attention to energy and critical-infrastructure resilience, hybrid threats, airspace and maritime incidents, readiness and diplomacy. "
        f"The daily research window is {DAILY_WINDOW}, America/Detroit; the rolling event-date register covers {REGISTER_WINDOW}, inclusive. "
        "Institutions and outlets actually searched included NATO, the Romanian Ministry of National Defence, the Council of the European Union, Lithuanian government and security reporting, Reuters and Associated Press. Originals and primary pages actually opened included NATO's October 19 Hybrid Symposium release and Romania's October 19 Defence Ministry update; Reuters and AP reports on the October 19 energy attack, Lithuanian critical-infrastructure security measures and the proposed Russia-U.S.-China summit were also opened and checked. "
        "A current Lithuanian government press release providing the detailed infrastructure list was not located, Russian and Belarusian defence originals were not successfully opened in this run, and public forensic evidence for several hybrid-attribution claims remains incomplete. The carried-forward register preserves prior documentation and was not fully revalidated row by row today."
    )
    story += [p(purpose)]
    story += [p("It brings together publicly documented security developments and distinguishes verified events from official assessments, routine exercises, recycled reporting, and unverified claims. The purpose is to help readers, finance and operations leaders, and CEOs recognize relevant exposures, protect people and assets, maintain business continuity, and make informed budget and forecast decisions. Preparation should be proportionate to credible evidence and an organization's actual dependencies, not to the volume or intensity of alarming headlines. This is a public-source planning brief, not an official intelligence warning, and increased preparedness does not by itself establish that conflict is imminent.")]
    story += [p(f"Generated and researched through: {CUTOFF} (America/Detroit). Source refresh: {CUTOFF}.<br/>Daily window: {DAILY_WINDOW}.<br/>Rolling two-calendar-month window: {REGISTER_WINDOW} (inclusive).<br/>Prior reliable complete issue: October 18, 2026, 2:05 PM EDT.<br/>Register status: 171 dated or qualifying records and six separately retained date-limited disclosures. Four current records were added to the 167-record October 18 continuity baseline.", "ERSmall")]
    story += [PageBreak()]

    story += [h1("Contents")]
    for item in [
        "1. Today's Bottom Line", "2. What Changed", "3. Leadership Application", "4. Verified Developments and Evidence Register", "5. Rolling Two-Month Location/Event Register", "6. Standing Indicator Dashboard", "7. Reality Check and Corrections", "8. Upcoming and Watch Next", "9. Balanced Close, Reading Legend and Sources"
    ]:
        story.append(p(item, "ERBody"))

    story += [h1("1. Today's Bottom Line")]
    story += [p("<b>Russia's October 19 attack on Ukraine's energy system is the strongest new infrastructure-disruption signal in this edition.</b> Reuters reported 16 ballistic missiles and more than 200 drones across Ukraine, with more than ten energy facilities damaged, at least three deaths and rolling outages affecting more than 550,000 households. Associated Press separately reported 28 substations and other critical energy facilities hit. This belongs in a wider-European readiness brief because power, rail, data, pharmaceutical storage and cross-border energy resilience can affect suppliers, humanitarian demand and continuity planning, but it should not be misread as proof that NATO has entered direct combat.")]
    story += [p("<b>Lithuania raised protection at strategic infrastructure after an attempted arson attack at a Starlink base station near Vilnius.</b> The prime minister said more forces and attention would be assigned to more than 15 strategic sites after government and security officials met. The attempted arson and security response are reported occurrences; the statement that the sabotage was linked to Russia is an official attribution that still requires case-specific evidence and legal findings. For business leaders, the immediate implication is to validate physical access controls, telecom dependencies, backup communications and third-party security rather than assume a nationwide service failure.")]
    story += [p("<b>NATO published new detail on an October 15-16 Hybrid Symposium in Bucharest.</b> NATO, allies, partners, the European Union, industry, Ukraine and Moldova discussed sabotage, drone incidents, cyberattacks and protection of critical infrastructure, particularly energy. The publication is newly available background, not a new October 19 military deployment. Its significance is the increasing integration of public agencies, intelligence, infrastructure operators and private companies around hybrid resilience.")]
    story += [p("<b>A proposed Putin-Trump-Xi meeting remains preliminary diplomacy, not a scheduled peace conference.</b> Reuters reported that Putin proposed a November meeting on the sidelines of the APEC summit. The Kremlin acknowledged discussions, a senior U.S. official said Trump had not agreed, and no agenda or settlement framework was finalized. The proposal is a de-escalatory channel worth monitoring, but it does not establish a ceasefire or justify removing disruption scenarios.")]
    story += [p("<b>The strongest counterevidence to an imminent direct NATO-Russia war remains the absence of a verified collective-war decision, general mobilization or operational nuclear-alert increase.</b> Romania's October 19 update confirmed that the two drones shot down on October 17 were Geran-family jet-powered attack drones, strengthening platform identification but not proving operator or deliberate intent to strike Romania. The evidence supports sustained long-term preparedness, elevated hybrid and infrastructure pressure, and serious eastern-flank incident risk. Publicly available evidence reviewed through the cutoff still does not establish Article 5 activation or an imminent conventional NATO-Russia conflict.")]
    story += [p(f"{link('Reuters: October 19 energy attack', URLS['reuters_energy'])} | {link('AP: energy and infrastructure impact', URLS['ap_energy'])} | {link('Reuters: Lithuania infrastructure security', URLS['reuters_lithuania'])} | {link('NATO Hybrid Symposium', URLS['nato_hybrid'])} | {link('Romanian Defence Ministry update', URLS['romania_update'])} | {link('Reuters: proposed summit', URLS['reuters_summit'])}", "ERSource")]

    story += [h1("2. What Changed Since the Prior Complete Issue")]
    story += [card("NEW INCIDENT | UKR-ENERGY-20261019", "Russia launched a broad ballistic-missile and drone attack that damaged Ukrainian energy infrastructure, caused widespread outages and also affected transport, pharmaceutical, commercial and residential assets. Occurrence confidence is high from multiple official accounts and independent reporting. The wider-war implication remains limited because the event occurred within the ongoing Russia-Ukraine war.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_energy"])])]
    story += [card("NEW PREPAREDNESS ACTION | LTU-CRITINFRA-20261019", "Lithuania's government agreed to raise preparedness and deploy more attention and forces around strategic infrastructure after an attempted Starlink-site arson attack and the prior day's drone incident. The protective decision is confirmed through the prime minister's statement. Attribution of the attempted arson to Russia remains an official investigative position rather than a completed public forensic finding.", [("Reuters", URLS["reuters_lithuania"])])]
    story += [card("NEWLY PUBLISHED BACKGROUND | NATO-HYBRID-SYMP-20261015-16", "NATO published its account of the October 15-16 Bucharest Hybrid Symposium. The event predates the current daily window but the public record is new today and is labeled background rather than a new October 19 incident.", [("NATO", URLS["nato_hybrid"])])]
    story += [card("NEW DIPLOMATIC PROPOSAL | RUS-USA-CHN-SUMMIT-20261019", "Putin proposed a Trump-Xi-Putin meeting at the November APEC summit. Discussions are preliminary, Trump has not agreed and no agenda or settlement exists. This is a possible diplomatic channel, not a concluded de-escalation measure.", [("Reuters", URLS["reuters_summit"])])]
    story += [card("UPDATED OFFICIAL IDENTIFICATION | ROU-AIR-20261017", "Romania's Defence Ministry now identifies the two October 17 targets destroyed over territorial waters as jet-powered Geran-family attack drones. This improves confidence in platform type but does not publicly establish operator, launch point or intent to attack Romanian territory.", [("Romanian MoD", URLS["romania_update"])])]
    story += [p("<b>No verified collective-war decision.</b> The reviewed sources did not establish NATO Article 5 activation, a general Russian or Belarusian mobilization order, or an operational nuclear-alert increase. Absence of a qualifying public record is source-limited evidence, not proof that all military activity is absent.")]

    story += [h1("3. Leadership Application: Prepare, Protect, Continue Operations, Plan Financially")]
    story += [card("Check now | UKR-ENERGY-20261019 | Energy, rail, data and supplier continuity", "Organizations with Ukrainian sites, suppliers, data dependencies, rail flows or humanitarian obligations should verify power status, backup generation, fuel availability, communications and employee safety through local operators and authorities. Operations should define minimum service, restoration priorities and alternatives that do not share the same grid or telecom dependency. Finance should separate temporary downtime, emergency freight, spoilage and overtime from permanent revenue loss, and should trigger forecast changes only from documented operating impact.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_energy"])])]
    story += [card("Check now | LTU-CRITINFRA-20261019 | Physical and communications resilience", "Companies with Lithuanian facilities or dependencies should confirm whether employees, telecom providers, data links, utilities or logistics partners are among the protected strategic sites. Security and IT owners should recheck access control, surveillance, incident escalation, backup communications and vendor continuity. Finance should treat any new security spend as approved, contingent or scenario-only and avoid treating a protective government posture as evidence of a service outage.", [("Reuters", URLS["reuters_lithuania"])])]
    story += [card("Prepare an option | NATO-HYBRID-SYMP-20261015-16 | Hybrid and critical-infrastructure risk", "Use the NATO themes as a structured test of actual exposure: sabotage, drones, cyber compromise, energy interruption and private-sector coordination. COOs should validate recovery time and manual-workaround assumptions; CFOs should identify insurance, capex, opex, liquidity and working-capital consequences; CEOs should define decision rights and stakeholder communications. Expensive changes require a company-specific exposure and cost-benefit case.", [("NATO", URLS["nato_hybrid"])])]
    story += [card("Monitor | RUS-USA-CHN-SUMMIT-20261019 | Diplomacy and sanctions", "Treasury, compliance and strategic planning should monitor whether the proposed meeting becomes scheduled and whether it produces sanctions, energy, trade or ceasefire measures. No base-case change is warranted from a proposed meeting alone. Observable triggers are formal confirmation, a published agenda, signed measures, legal waivers or verified cessation of attacks.", [("Reuters", URLS["reuters_summit"])])]
    story += [p("<b>No base-forecast change is warranted solely from today's geopolitical headlines.</b> The CEO should retain decision rights for life safety, minimum service, capital approval and communications; the COO should own tested fallbacks and recovery; and the CFO should own cash, working-capital and scenario assumptions. Use actual supplier, carrier, utility, banking, insurer and authority notices as triggers. This is management analysis, not legal, accounting, insurance or security advice.")]

    story += [h1("4. Verified Developments and Evidence Register")]
    story += [card("UKR-ENERGY-20261019 | Ukraine - national energy and transport infrastructure", "<b>Event/publication:</b> October 19, 2026. <b>Asset:</b> electricity/grid, rail, commercial and civilian facilities. <b>Kind/stage:</b> incident / damage, outages and restoration. <b>Evidence class:</b> CONFIRMED ACTION OR DOCUMENT for reported attacks and outages, with damage counts attributed to Ukrainian officials and Russian target claims separately attributed. Reuters reported 16 ballistic missiles, more than 200 drones, more than ten energy facilities damaged, three deaths and more than 550,000 households losing power. AP reported 28 substations and other critical energy facilities hit. <b>Occurrence confidence:</b> High. <b>Attribution/intent:</b> Russia acknowledged a large strike but described military-industrial targets; Ukraine said energy was the main target. <b>Imminent-war limit:</b> severe infrastructure warfare within Ukraine does not itself establish direct NATO-Russia combat.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_energy"])])]
    story += [card("LTU-CRITINFRA-20261019 | Lithuania - Vilnius and strategic infrastructure sites", "<b>Event/publication:</b> October 19, 2026. <b>Asset:</b> telecom, critical infrastructure and multi-sector continuity. <b>Kind/stage:</b> preparedness / heightened security ordered. <b>Evidence class:</b> CONFIRMED ACTION OR DOCUMENT for the prime minister's announced protective measures; OFFICIAL CLAIM/ASSESSMENT for Russian linkage. Lithuania said it would raise preparedness at more than 15 strategic sites after an attempted arson attack on a Starlink base and the October 18 drone incident. <b>Occurrence confidence:</b> High for the response and reported arson attempt. <b>Attribution/intent:</b> medium pending completed investigation and public evidence. <b>Imminent-war limit:</b> heightened infrastructure protection is not a mobilization or attack order.", [("Reuters", URLS["reuters_lithuania"])])]
    story += [card("NATO-HYBRID-SYMP-20261015-16 | NATO / Romania - Bucharest", "<b>Event:</b> October 15-16, 2026. <b>Publication:</b> October 19, 2026. <b>Asset:</b> energy, cyber, critical infrastructure and multi-sector resilience. <b>Kind/stage:</b> preparedness and policy coordination / symposium completed. <b>Evidence class:</b> CONFIRMED ACTION OR DOCUMENT. NATO said allies, partners, the EU, industry, Ukraine and Moldova discussed sabotage, drones, cyberattacks, energy infrastructure and private-sector cooperation. <b>Occurrence confidence:</b> Very high. <b>Attribution/intent:</b> NATO's statements about Russian hybrid activity are official assessments; individual cases require separate evidence. <b>Imminent-war limit:</b> resilience coordination is not proof of an imminent conventional attack.", [("NATO", URLS["nato_hybrid"])])]
    story += [card("ROU-AIR-20261017 | Romania - Black Sea territorial waters", "<b>Material update:</b> October 19, 2026. <b>Asset:</b> military airspace. <b>Kind/stage:</b> incident / targets destroyed; identification updated. <b>Evidence class:</b> CONFIRMED ACTION OR DOCUMENT. Romania's ministry now states that the two October 17 targets were jet-powered Geran-family attack drones. <b>Occurrence confidence:</b> Very high. <b>Attribution/intent:</b> platform family is now official; operator, launch point and deliberate Romanian targeting remain unproven publicly. <b>Imminent-war limit:</b> the incident is serious but does not establish Article 5 activation or a NATO attack decision.", [("Romanian MoD", URLS["romania_update"])])]
    story += [card("RUS-USA-CHN-SUMMIT-20261019 | Russia / United States / China", "<b>Event/publication:</b> October 18-19, 2026. <b>Asset:</b> policy, sanctions and multi-sector exposure. <b>Kind/stage:</b> policy/diplomacy / proposal under discussion. <b>Evidence class:</b> CREDIBLY REPORTED, NOT INDEPENDENTLY CONFIRMED as a scheduled meeting. Putin proposed a trilateral summit at the November 18-19 APEC meeting. The Kremlin acknowledged discussions; a senior U.S. official said Trump had not agreed. <b>Occurrence confidence:</b> High for the reported proposal. <b>Attribution/intent:</b> negotiating objectives remain disputed. <b>Imminent-war limit:</b> a proposed meeting is not an agreed ceasefire or security settlement.", [("Reuters", URLS["reuters_summit"])])]
    story += [card("RUS-ENERGY-INCIDENTS-20261018 | Russia - St. Petersburg and multiple regions", "<b>Newly reported background.</b> <b>Event:</b> October 18, 2026. <b>Asset:</b> oil/fuel, logistics and IT/data. <b>Kind/stage:</b> incident / fires and damage assessment. AP reported Ukrainian drone strikes set fires at an oil export terminal and oil depot, with additional targets including a logistics center and data center. Russia said it destroyed 1,015 drones; that national total was not independently counted by AP. <b>Occurrence confidence:</b> High for fires and company/local-official acknowledgements. <b>Attribution/intent:</b> Ukraine's role is broadly acknowledged, while exact target effects and Russian interception numbers remain source-dependent. <b>Imminent-war limit:</b> deep strikes within the Russia-Ukraine war do not by themselves establish NATO participation.", [("AP", URLS["ap_russia_drones"])])]

    story += [h1("5. Rolling Two-Calendar-Month Location/Event Register")]
    story += [p(f"<b>Inclusive event-date window:</b> {REGISTER_WINDOW}. <b>171 dated or qualifying records</b> are retained, comprising the 167-record October 18 continuity baseline plus four current additions. Six date-limited disclosures remain separate and excluded from the precise dated count. Rows are ordered by affected location in the carried-forward baseline; current addenda are inserted near their corresponding country or institutional group and use stable IDs rather than renumbering every retained row.")]
    story += [p("<b>Continuity limitation:</b> Most older source originals were not reopened in this manual October 19 run. Carried-forward pages retain their prior record wording and links; they are continuity evidence, not new reporting or an exhaustive incident census. The PDF footer is updated to the current edition, while the text of carried-forward records preserves the date and evidentiary limits under which they were originally documented.")]
    story += [h2("001. Belarus - CSTO exercise venues | BLR-CSTO-ARRIVAL-20261009 | 2026-10-09 to 2026-10-16 | defense/military")]
    story += [p("Exercise/training window. CSTO announced Indestructible Brotherhood-2026 and Barrier-2026 in Belarus with more than 1,500 personnel, over 300 equipment items and about 80 UAVs according to organizers. The announced window ended October 16; independent completion and withdrawal were not reverified. Occurrence confidence is high that the organization issued the figures, while scale and intent are official claims. No general mobilization, NATO-facing attack order or operational nuclear-alert change was established.")]
    story += [h2("002. Belarus / Russia - nationwide joint air-force phase | BLR-AIR-20260825 | 2026-08-25 to 2026-09-10 | military airspace")]
    story += [p("Exercise. Belarusian and Russian forces conducted announced air-force and air-defence training. The published window ended, and completion was not independently reverified in this edition. Occurrence confidence is medium-high; the stated purpose was training and operational intent against NATO was not established.")]
    story += [PageBreak()]

    doc(path).build(story)


def build_addendum(path: Path, heading: str, entries: list[tuple[str, str, list[tuple[str, str]]]]) -> None:
    story = [h1(heading)]
    story += [p("Current addendum inserted into the carried-forward register at the nearest practical location. Stable IDs preserve continuity; the baseline pages retain their original numbering.", "ERSmall")]
    for title, body, sources in entries:
        story.append(card(title, body, sources))
    doc(path).build(story)


def build_back(path: Path) -> None:
    story = [h1("6. Standing Indicator Dashboard")]
    dashboard = [
        ["Indicator", "Latest material change and evidence", "Next observable development"],
        ["Troops and readiness", "Oct. 17-19. Romanian F-16 shootdowns and updated Geran-family identification. High evidence for Romanian action; no broad force-posture change established.", "Formal NATO force decision, verified deployment or new basing order."],
        ["Exercises", "Steadfast Noon remains scheduled routine training with no live nuclear weapons. No new alert change identified.", "Official completion, withdrawal or a separately announced exercise."],
        ["Mobilization", "Not established in sources reviewed. No new broad Russian, Belarusian or NATO mobilization order was found.", "Published call-up order, reserve expansion or force-generation directive."],
        ["Industry and logistics", "Oct. 19 energy damage in Ukraine; continuing Black Sea and land-transit pressure. High evidence for outages and logistics exposure.", "Restoration data, carrier restrictions, border throughput or funded procurement."],
        ["Air, missile and nuclear posture", "Near-term incident pressure remains elevated. Romania confirms drone platform family; no operational nuclear-alert increase identified.", "Verified alert-state change, weapons loading evidence or collective NATO decision."],
        ["Civil defence", "Lithuania heightened security at more than 15 strategic infrastructure sites. High confidence in protective action.", "Named implementation orders, duration, closures or stand-down."],
        ["Sabotage and hybrid incidents", "NATO published Bucharest symposium conclusions; Lithuania's arson investigation continues. Occurrence and attribution confidence remain separate.", "Forensic findings, charges, court records or coordinated resilience measures."],
        ["Diplomacy", "Proposed Trump-Putin-Xi meeting remains preliminary. No agenda, acceptance or ceasefire agreement.", "Formal meeting confirmation, published agenda, signed measure or cancellation."],
    ]
    t = Table(dashboard, colWidths=[1.35*inch, 3.35*inch, 2.1*inch], repeatRows=1, hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0,0), (-1,0), NAVY), ("TEXTCOLOR", (0,0), (-1,0), WHITE), ("FONTNAME", (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE", (0,0), (-1,-1), 8), ("LEADING", (0,0), (-1,-1), 10.4), ("VALIGN", (0,0), (-1,-1), "TOP"),
        ("GRID", (0,0), (-1,-1), 0.35, RULE), ("ROWBACKGROUNDS", (0,1), (-1,-1), [colors.white, LIGHT]),
        ("LEFTPADDING", (0,0), (-1,-1), 5), ("RIGHTPADDING", (0,0), (-1,-1), 5), ("TOPPADDING", (0,0), (-1,-1), 5), ("BOTTOMPADDING", (0,0), (-1,-1), 5),
    ]))
    story += [t, Spacer(1, 8), p("Direction rule: directional arrows are withheld where comparable denominators are unavailable. More retrieved records do not, by themselves, establish a rising attack rate.", "ERSmall")]

    story += [h1("7. Reality Check and Corrections")]
    story += [p("<b>No specific false claim adjudicated in this edition.</b> Several consequential claims require qualification rather than a true-or-false label.")]
    story += [card("Romanian drone attribution", "Romania now officially identifies the destroyed targets as Geran-family jet-powered attack drones. This confirms the platform family in the government's assessment, not the operator, launch point or deliberate intent to attack Romania.", [("Romanian MoD", URLS["romania_update"])])]
    story += [card("Ukraine early-warning claim", "Ukraine said it received no warning before the first ballistic wave and information before a second wave arrived too late. The U.S. secretary of state denied that intelligence sharing had been paused. The evidence therefore supports a specific warning failure under investigation, not a proven complete termination of all intelligence support.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_energy"])])]
    story += [card("Proposed trilateral summit", "The meeting is not scheduled and no peace terms have been agreed. Reporting supports that the idea is being discussed, while the U.S. has not accepted and the Kremlin says no substantive agenda exists.", [("Reuters", URLS["reuters_summit"])])]
    story += [card("NATO Hybrid Symposium date", "The symposium occurred October 15-16; NATO published its account October 19. It is newly published background, not a new event occurring today.", [("NATO", URLS["nato_hybrid"])])]
    story += [card("Energy ceasefire", "Continuing attacks on Ukrainian and Russian energy assets show that no broad, mutually implemented energy ceasefire can be treated as established. Public proposals and political claims remain distinct from observed cessation.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_russia_drones"])])]

    story += [h1("8. Upcoming and Watch Next")]
    story += [p("<b>Tuesday, October 20 | NATO and Black Sea.</b> Romania previously indicated that the North Atlantic Council was expected to discuss Black Sea defence and deterrence. Watch for an official NATO decision, capability commitment, counter-drone measure or no-action outcome. A scheduled discussion is not a deployment.")]
    story += [p("<b>November 18-19 | APEC summit in Shenzhen.</b> Watch whether a Trump-Putin-Xi meeting is formally accepted and scheduled. A confirmed meeting, agenda or signed measure would materially change the diplomatic assessment; continued discussion without agreement would not.")]
    story += [p("<b>Lithuanian critical-infrastructure measures.</b> Watch for the named facilities, duration, force allocation, operating restrictions, investigation findings and eventual stand-down. Protective measures matter operationally only where they change access, service or supplier performance.")]
    story += [p("<b>Ukrainian energy restoration.</b> Watch verified restoration progress, rolling-outage duration, rail and data impacts, cross-border electricity needs and humanitarian supply requirements. These observables determine financial and operational exposure more reliably than attack counts alone.")]
    story += [p("<b>NATO annual nuclear exercise.</b> Watch for official completion and withdrawal information. Routine exercise activity should not be converted into a nuclear-alert claim without verified operational evidence.")]

    story += [h1("9. Balanced Close, Reading Legend and Sources")]
    story += [p("The strongest escalation evidence is the combination of a major attack on Ukraine's energy system, Lithuania's decision to increase protection around strategic infrastructure, Romania's confirmed destruction and updated identification of attack drones, and NATO's continued focus on hybrid resilience. The strongest counterevidence is that the reviewed public record still does not establish NATO Article 5 activation, a collective decision to initiate hostilities, broad new Russian or Belarusian mobilization, or an operational nuclear-alert increase. The evidence supports elevated hybrid, infrastructure and eastern-flank incident pressure alongside substantial long-term preparedness, but it does not support a claim that direct conventional NATO-Russia war is imminent.")]
    story += [p("<b>Reading legend.</b> Event date is when the underlying activity occurred; publication date is when a source reported it. CONFIRMED ACTION OR DOCUMENT identifies the precise action or record verified, not every allegation within it. OFFICIAL CLAIM/ASSESSMENT confirms that an institution made an assessment. CREDIBLY REPORTED, NOT INDEPENDENTLY CONFIRMED identifies evidence limits. High confidence concerns occurrence; attribution and intent can remain lower. Preparedness, exercises, procurement and civil-protection guidance do not by themselves prove imminent war.")]
    story += [h2("Current source list")]
    sources = [
        ("Reuters, October 19: Russian strike and energy damage", URLS["reuters_energy"]),
        ("Associated Press, October 19: power grid and infrastructure effects", URLS["ap_energy"]),
        ("Reuters, October 19: Lithuania critical-infrastructure security", URLS["reuters_lithuania"]),
        ("NATO, October 19: Bucharest Hybrid Symposium", URLS["nato_hybrid"]),
        ("Romanian Ministry of National Defence, October 19 update", URLS["romania_update"]),
        ("Reuters, October 19: proposed Putin-Trump-Xi summit", URLS["reuters_summit"]),
        ("Associated Press, October 18: Ukrainian drone attacks in Russia", URLS["ap_russia_drones"]),
    ]
    for label, url in sources:
        story.append(p(link(label, url), "ERSource"))
    story += [p("The carried-forward location register contains additional original links embedded in the retained October 18 baseline pages. Those rows preserve their original evidence status and are not represented as newly rechecked today.", "ERSmall")]
    doc(path).build(story)


def extract_pages(reader: PdfReader, first_page: int, last_page: int, out_path: Path) -> None:
    writer = PdfWriter()
    for page_number in range(first_page, last_page + 1):
        writer.add_page(reader.pages[page_number - 1])
    with out_path.open("wb") as f:
        writer.write(f)


def combine(parts: list[Path], out_path: Path) -> None:
    writer = PdfWriter()
    for part in parts:
        r = PdfReader(str(part))
        for pg in r.pages:
            writer.add_page(pg)
    with out_path.open("wb") as f:
        writer.write(f)


def normalize_pdf(input_path: Path, output_path: Path) -> tuple[int, int, int]:
    pdf = fitz.open(str(input_path))
    link_count = 0
    blank_pages = []
    render_dir = TMP / "renders"
    if render_dir.exists():
        shutil.rmtree(render_dir)
    render_dir.mkdir(parents=True)
    for i, page in enumerate(pdf):
        rect = page.rect
        page.draw_rect(fitz.Rect(0, rect.height - 31, rect.width, rect.height), color=(1,1,1), fill=(1,1,1), overlay=True)
        page.insert_text((36, rect.height - 11), "Public-source awareness and planning brief", fontname="helv", fontsize=7.3, color=(0.28,0.34,0.38), overlay=True)
        right = f"2026-10-19 | Page {i+1}"
        tw = fitz.get_text_length(right, fontname="helv", fontsize=7.3)
        page.insert_text((rect.width - 36 - tw, rect.height - 11), right, fontname="helv", fontsize=7.3, color=(0.28,0.34,0.38), overlay=True)
        text = page.get_text("text").strip()
        if len(text) < 25:
            blank_pages.append(i+1)
        link_count += len(page.get_links())
        pix = page.get_pixmap(matrix=fitz.Matrix(1.15, 1.15), alpha=False)
        pix.save(str(render_dir / f"page-{i+1:03d}.png"))
    if blank_pages:
        raise RuntimeError(f"Rendered PDF contains pages with insufficient text: {blank_pages}")
    metadata = pdf.metadata or {}
    metadata.update({"title":"Europe Readiness Daily 2026-10-19", "author":"", "subject":"", "keywords":"", "creator":"Europe Readiness Daily", "producer":"ReportLab and PyMuPDF"})
    pdf.set_metadata(metadata)
    pdf.save(str(output_path), garbage=4, deflate=True, clean=True)
    count = len(pdf)
    pdf.close()
    return count, link_count, len(list(render_dir.glob("page-*.png")))


def build_site(page_count: int, byte_size: int) -> None:
    kb = max(1, round(byte_size / 1024))
    summary = "The October 19 edition examines a major attack on Ukraine's energy system, Lithuania's heightened protection of strategic infrastructure, NATO hybrid-resilience coordination, updated Romanian drone identification and a proposed Russia-U.S.-China summit. It includes leadership applications and the full rolling evidence register with linked sources."

    template = (SECTION / "2026-10-18" / "index.html").read_text(encoding="utf-8")
    page = template.replace("2026-10-18", "2026-10-19").replace("Sunday, October 18, 2026", DATE_LONG).replace("October 18, 2026", "October 19, 2026")
    page = re.sub(r"55 pages · PDF · 210 KB", f"{page_count} pages · PDF · {kb} KB", page)
    page = page.replace("Research cutoff: 2:05 p.m. EDT", "Research cutoff: 10:25 a.m. EDT")
    page = page.replace("October 18, 2026, 2:05 p.m. EDT (America/Detroit)", "October 19, 2026, 10:25 a.m. EDT (America/Detroit)")
    page = page.replace("October 16, 2026, 8:22 a.m. EDT through October 18, 2026, 2:05 p.m. EDT", DAILY_WINDOW.replace("AM", "a.m.").replace("PM", "p.m."))
    page = page.replace("August 18, 2026 through the research cutoff", "August 19, 2026 through the research cutoff")
    page = re.sub(r"55 pages · 215,460 bytes · Final PDF", f"{page_count} pages · {byte_size:,} bytes · Final PDF", page)
    old_summary = "This edition examines Romania's confirmed drone shootdowns, Lithuania's shelter and airport response to a suspected drone, adopted European Council defence and Ukraine-support conclusions, Black Sea grain-logistics disruption, and continuing readiness signals. It connects verified developments to people, logistics, operating continuity, sanctions and trade exposure, and financial planning while keeping confirmed actions, official claims, exercises, and unresolved attribution distinct."
    page = page.replace(old_summary, summary)
    DATED_DIR.mkdir(parents=True, exist_ok=True)
    DATED_PAGE.write_text(page, encoding="utf-8")

    landing = LANDING.read_text(encoding="utf-8")
    landing = landing.replace('href="/european-readiness/2026-10-18/">Read the latest edition', 'href="/european-readiness/2026-10-19/">Read the latest edition')
    latest = f'''<article class="er-latest-card">
      <div class="er-date-tile" aria-label="October 19, 2026"><span>October</span><strong>19</strong><span>2026</span></div>
      <div class="er-card-copy"><p class="er-label">Europe Readiness Daily</p><h3><a href="/european-readiness/2026-10-19/">{DATE_LONG}</a></h3><p>{summary}</p><p class="er-meta">{page_count} pages · PDF · {kb} KB · Research cutoff: 10:25 a.m. EDT</p></div>
      <div class="er-card-actions"><a class="er-button" href="/european-readiness/2026-10-19/">Read this edition <span aria-hidden="true">→</span></a><a class="er-download" href="/european-readiness/editions/{PDF_NAME}" download="{PDF_NAME}">Download the PDF ↓</a></div>
    </article>'''
    landing, n = re.subn(r'<article class="er-latest-card">[\s\S]*?</article>', latest, landing, count=1)
    if n != 1:
        raise RuntimeError("Could not replace Latest Edition card")
    row = f'''<tr><th scope="row"><time datetime="2026-10-19">October 19, 2026</time></th><td><a href="/european-readiness/2026-10-19/">Europe Readiness Daily <span aria-hidden="true">→</span></a><span class="er-table-note">Verified preparations, escalation signals, and fact checks</span></td><td><a href="/european-readiness/editions/{PDF_NAME}" download="{PDF_NAME}">PDF ↓<span class="er-sr-only">, October 19, 2026</span></a><span class="er-table-note">{page_count} pages · {kb} KB</span></td></tr>'''
    if 'datetime="2026-10-19"' not in landing:
        pos = landing.index("<tbody>", landing.index('id="archive"')) + len("<tbody>")
        landing = landing[:pos] + row + landing[pos:]
    LANDING.write_text(landing, encoding="utf-8")

    data = json.loads(EDITIONS.read_text(encoding="utf-8"))
    data["editions"] = [e for e in data.get("editions", []) if e.get("date") != DATE_ISO]
    data["editions"].insert(0, {"date":DATE_ISO,"title":"Europe Readiness Daily","page":"/european-readiness/2026-10-19/","pdf":f"/european-readiness/editions/{PDF_NAME}","pages":page_count,"bytes":byte_size,"status":"final"})
    EDITIONS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    checks = {
        "latest": 'aria-label="October 19, 2026"' in landing and 'href="/european-readiness/2026-10-19/">Read this edition' in landing,
        "archive": '<time datetime="2026-10-19">October 19, 2026</time>' in landing,
        "edition_page": PDF_NAME in page and DATE_LONG in page,
        "editions_json": data["editions"][0]["date"] == DATE_ISO,
        "no_drive": "drive.google.com" not in landing.lower() and "google drive" not in landing.lower() and "drive.google.com" not in page.lower(),
    }
    bad = [k for k,v in checks.items() if not v]
    if bad:
        raise RuntimeError(f"Site verification failed: {bad}")


def main() -> None:
    if not PREV_PDF.exists():
        raise FileNotFoundError(PREV_PDF)
    front = TMP / "front.pdf"
    back = TMP / "back.pdf"
    build_front(front)
    build_back(back)

    ltu = TMP / "add_ltu.pdf"
    nato = TMP / "add_nato.pdf"
    rus = TMP / "add_rus.pdf"
    ukr = TMP / "add_ukr.pdf"
    build_addendum(ltu, "Lithuania - current register addendum", [("LTU-CRITINFRA-20261019 | Lithuania - Vilnius and strategic sites | 2026-10-19 | telecom / multi-sector", "Preparedness action. Lithuania's prime minister said protection would increase at more than 15 strategic infrastructure sites after an attempted arson attack at a Starlink base and the prior drone incident. Occurrence confidence is high for the meeting, arson attempt and protective decision. Attribution to Russia is an official investigative position and is not treated as independently completed forensic proof. Last material change: October 19, 2026.", [("Reuters", URLS["reuters_lithuania"])])])
    build_addendum(nato, "NATO - current register addendum", [("NATO-HYBRID-SYMP-20261015-16 | NATO / Romania - Bucharest | 2026-10-15 to 2026-10-16 | multi-sector", "Preparedness and policy coordination. NATO published on October 19 that allies, partners, the EU, industry, Ukraine and Moldova met in Bucharest to discuss sabotage, drone incidents, cyberattacks, energy infrastructure and private-sector coordination. Occurrence confidence is very high for the official event record. NATO's attribution of broader Russian hybrid activity is an official assessment; individual events require separate proof. Last material change: October 19 publication of the completed-event record.", [("NATO", URLS["nato_hybrid"])])])
    build_addendum(rus, "Russia and diplomacy - current register addendum", [("RUS-USA-CHN-SUMMIT-20261019 | Russia / United States / China | 2026-10-18 to 2026-10-19 | multi-sector", "Diplomatic proposal. Putin proposed a trilateral meeting with Trump and Xi at the November APEC summit. Kremlin discussions are acknowledged, Trump has not agreed and no agenda or settlement is finalized. Occurrence confidence is high for the reported proposal; implementation and negotiating intent remain uncertain. Last material change: October 19, 2026.", [("Reuters", URLS["reuters_summit"])])])
    build_addendum(ukr, "Ukraine - current register addendum", [("UKR-ENERGY-20261019 | Ukraine - national energy and transport infrastructure | 2026-10-19 | electricity / rail / multi-sector", "Incident and restoration. Russia launched a broad missile and drone attack that damaged energy facilities and caused rolling outages affecting more than 550,000 households, with transport, commercial, pharmaceutical and residential damage also reported. Occurrence confidence is high. Russian and Ukrainian descriptions of target selection differ, while the broader infrastructure disruption is independently reported. Last material change: October 19, 2026.", [("Reuters", URLS["reuters_energy"]), ("AP", URLS["ap_energy"])])])

    prior = PdfReader(str(PREV_PDF))
    chunks = []
    for name, start, end in [
        ("reg_a.pdf", 8, 25),
        ("reg_b.pdf", 26, 29),
        ("reg_c.pdf", 30, 43),
        ("reg_d.pdf", 44, 45),
        ("reg_e.pdf", 46, 51),
    ]:
        out = TMP / name
        extract_pages(prior, start, end, out)
        chunks.append(out)

    merged = TMP / "merged.pdf"
    parts = [front, chunks[0], ltu, chunks[1], nato, chunks[2], rus, chunks[3], ukr, chunks[4], back]
    combine(parts, merged)
    PDF_PATH.parent.mkdir(parents=True, exist_ok=True)
    pages, links, renders = normalize_pdf(merged, PDF_PATH)
    size = PDF_PATH.stat().st_size
    if pages < 50:
        raise RuntimeError(f"Unexpectedly short PDF: {pages} pages")
    if renders != pages:
        raise RuntimeError(f"Render count mismatch: {renders} renders for {pages} pages")
    if links < 80:
        raise RuntimeError(f"Too few preserved hyperlinks: {links}")
    build_site(pages, size)
    print(json.dumps({"pdf":str(PDF_PATH),"pages":pages,"bytes":size,"links":links,"rendered_pages":renders,"sha256":hashlib.sha256(PDF_PATH.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
