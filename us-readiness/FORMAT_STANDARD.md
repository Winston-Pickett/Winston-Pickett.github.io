# U.S. Domestic Readiness | Locked Format Standard

**Status:** Adopt European Readiness Daily's October 19, 2026 Revised 1 Word visual system and its approved November 2026 structural amendments, adapted only for the U.S. market.
**Read with:** `us-readiness/WORKFLOW.md`, `european-readiness/WORKFLOW.md`, `european-readiness/FORMAT_STANDARD.md`.
**Visual master:** private approved Europe Readiness Word master, copied to a separately verified U.S. derivative. Do not use a newly designed or PDF-first substitute.

## 1. Preserved layout
- U.S. Letter portrait; margins left/right 0.70 in, top approximately 0.68 in, bottom approximately 0.62 in.
- Arial body 10.5 pt near black #1B252C; small text 9 pt #40576A; source text 8.5 pt #40576A; register narrative 9.5 pt.
- Title 26 pt dark blue #17365D; Heading 1 Arial bold 17 pt navy #0B2538; Heading 2 12.5 pt; Heading 3 10.5 pt.
- Preserve original master named styles, front page, masthead/subtitle treatment, headers/footers, exact navy/white contrast, source styling, divider/card shapes, date/cutoff metadata and contents-page layout.
- Do not shrink body fonts, rebuild via direct formatting, or create independent PDF layouts.
- One dedicated contents page followed by a hard page break, with ten numbered contents entries plus one unnumbered U.S. Business Risk Outlook entry.
- Anonymous Word/PDF report metadata and body; website and social post branding may retain the author's name.

### Canonical edition URL immediately beneath version date
Approved November 19, 2026 for all subsequent U.S. master editions: on the opening page, insert an actual clickable hyperlink reading `GitHub edition: https://winston-pickett.github.io/us-readiness/YYYY-MM-DD/` on the line directly below the version/edition date. Match existing font family, text treatment, spacing and alignment; do not move or restyle other opening-page elements. The URL must match the dated published edition in `editions.json`, and must remain clickable in the final Word and Word-exported PDF. If not published yet, identify it as a planned URL, not a live publication. This is part of the single Full Master Edition with the executive summary integrated, not a separate executive document.

## 2. Unnumbered front end
Maximum two pages, after Contents and before Section 1: `U.S. Business Risk Outlook`, subtitle `Region-by-Region Intelligence for Business Leaders`. Same European executive card system and proportions, with 150-200 word substantive bottom line, meaningful regional exposures, previous-day delta, specific CFO/COO/CISO/CHRO actions and source links. Every material region card states documented concern, affected industry/dependency, conditional operations/financial consequences, owner, observable trigger, date/source and uncertainty. No generic one-line regional risk labels.

## 3. Ten sections
Exactly the ten U.S. headings and order in `WORKFLOW.md` section 5, each as a Word Heading 1; U.S. infrastructure posture is the Europe Section 5 analogue. The old European Russia/NATO subject text MUST NOT persist. Each primary section stands independently; references to the full register are not substitutes for full section content.

## 4. Register
Location-grouped single-column narrative records with Heading 2 titles, register and source styles cloned from European master. Preserve ID, event and publication dates, location, operator/sector, root cause, impact, restoration, incident status, intent, attribution and dated clickable source links. Complete rolling *60 calendar days* (not Europe two-calendar-month convention); label pre-window carry-ins separately, no fabricated entries or wide multi-column tables, no count reset or 60-item cap. The full 60-day register is in Section 6, not an image or link-only appendix. Date-limited/context items appear exactly once after Section 6, separate from incidents.

## 5. Dashboard
Exactly nine vertical stacked cards cloned from European dashboard, never a wide table. Order: physical sabotage; essential services; critical-infrastructure cyber; operational technology/ICS; transportation/logistics; telecom/data; banking/payments; foreign-actor attribution; government protective posture. Each card shows dated current evidence or `No newly verified material change`, last-supported baseline, uncertainty and next observable trigger. No invented colored risk levels or speculation.

## 6. Links and tables
- Text remains selectable in both Word and the PDF exported from Word.
- Cite each material claim using functioning hyperlinks to original dated source material; link annotations in PDF must be audited.
- Images for LinkedIn do not replace sources in the PDF. Do not post tables as image-only PDF pages.
- Use only genuinely narrow two-column tables when necessary and modelled by the master; no wide dashboard narrative tables.
- Repeat table headers across pages and prevent unreadable row splits. Dark fill requires explicit white foreground text.

## 7. Publication gate
Automated: 10 headings/order and one two-page executive front-end, 9 dashboard cards, original style equality, contents placement, no duplicates, stable IDs/60-day window/counts, provenance and source link audit, cutoff consistency, anonymous metadata, numbered pages and headers, PDF selectable text and URI annotations.
Visual: render every DOCX page and every PDF page, inspect at readable size, check clipping, overlap, orphan headings, legibility, source labels and last pages. Word/PDF parity must pass.
Release: commit final PDF, dated page, `editions.json`, Latest Edition and Archive as a coordinated unit; verify GitHub Pages deployment and publicly loadable URL. Source DOCX kept private, corrections disclosed with original cutoff. Do not publish a known-defective edition.

## 8. LinkedIn distribution
Mirror European practice: a concise, factual blurb + canonical dated edition link, not a separately authored LinkedIn article replacing the newsletter and not an infographic carousel. Preserve the same approved banner approach, at most one suitable 16:9 cover visual. Let readers access the complete clickable-source PDF in the GitHub dated edition.

## Incident heading taxonomy (approved November 20, 2026)

For every incident card in **Section 4 (Verified Developments and Evidence Register)** and **Section 6 (Rolling 60-Day Location/Event Register)**, prefix the existing Heading 2 with one **primary risk type**, followed by ` | `, leaving the rest of the heading intact, including the stable incident ID, original date/disclosure qualifiers, place/operator description, and H1/H2/D1/D2 where present. Existing location-group ordering and all named styles remain unchanged. The risk type does not replace causal class, severity, attribution, sector cross-dependencies, or permanent ID.

Example: `Telecom and Data | US26-0052 | 2026-11-19 01:01 EST | Harrison/Marion/Monongalia Counties, West Virginia | D2`.

Controlled primary risk types: `Physical Sabotage and Security`; `Essential Services` (electricity, water, wastewater, utilities, major environmental essential-service impacts); `Cyber and Critical Infrastructure` (confirmed/suspected cyber incident, supplier cyberattacks); `Operational Technology / ICS` (actual control-system incidents only); `Transportation and Logistics` (aviation, rail, roads, ports, freight); `Telecom and Data` (telecommunications, 911, cloud/SaaS/communications, data-network services); `Banking and Payments` (banks, payment processors, card/settlement systems); `Healthcare` (clinical system outages and diversion); `Industrial and Manufacturing` (plant, chemical, production incidents).

Choose exactly one primary type based on the principal affected business dependency, not suspected state attribution. Describe secondary affected sectors in the incident body. Foreign-actor attribution and government protective posture remain separate standing dashboard indicators, never headline risk types. Do not use an invented national threat score. Before release, verify every Heading 2 for an incident has an approved prefix, the underlying ID is unchanged, the register count is stable, and Word/PDF pagination and clickable links remain valid. Apply prospectively to all future U.S. editions only. The European Readiness standard is unaffected.


## Controlling amendment: LinkedIn article derivative (2026-11-24)
Produce TWO versions of each daily issue: (1) authoritative complete Word-first master and PDF with full 60-calendar-day register, published to GitHub only after release gates; (2) a separate editable Word LinkedIn article edition derived from that same validated master, matching the European abbreviated article approach. This supersedes earlier one-version/blurb-only restrictions solely for this derivative; it is not an independently researched executive report. Retain the title, date, disclaimer, executive outlook, ten numbered sections, material developments, dashboard, action priorities, corrections, and relevant clickable sources. Replace the detailed Section 6 register with a clearly labeled placeholder in its original position, including the rolling dates, incident totals by class and direct canonical dated GitHub link to the complete register. State prominently near the opening that the full version is available on GitHub only after live publication is verified; before then label it pending. Use a conservative editorial target of 100,000 characters or less, and verify the current LinkedIn article limit when possible; count the actual copyable article text including headings, spaces and links and report the count. Shorten repetitive material further if needed, without removing critical caveats or changing findings. Filename: US_Domestic_Readiness_Daily_YYYY-MM-DD_LINKEDIN.docx. Provide the downloadable derivative and the usual short referral blurb every run. Do not automatically post to LinkedIn, email, or archive the derivative publicly. If release fails, mark derivative private/pending and do not claim the GitHub link is live. Keep Europe unchanged.
