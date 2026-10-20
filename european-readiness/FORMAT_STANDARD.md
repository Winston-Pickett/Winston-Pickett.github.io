# Europe Readiness Daily Format Standard

**Template version:** 1.0  
**Effective date:** 2026-10-19  
**Status:** Locked  
**Canonical visual baseline:** `Europe Readiness Daily 2026-10-19 Revised 1.docx`  
**Private master template:** Google Drive folder `Europe Readiness Daily`, file `Europe Readiness Daily MASTER TEMPLATE v1.0.docx`  
**Master template file ID:** `1bXogv6Mhbba7izNNHGaONdv2NN2AYVhx`  
**Baseline DOCX SHA-256:** `5a95faac126af209f8ace5e246052dc3d12cefabf59dacd48fd3d333dc84968e`  
**Baseline review PDF SHA-256:** `091d5b5dbfbd7dbe023f9a716079dafbac2045a97b821faee7db45681a6af4fb`

## 1. Change control

The October 19 Revised 1 Word edition is the authoritative visual and structural template for all future editions. The template may not be redesigned, restyled, simplified, condensed, expanded, or replaced without explicit user approval. Daily content, dates, register records, page count, source links, and naturally required pagination may change. The visual system, style definitions, hierarchy, spacing rules, dashboard treatment, register treatment, headers, footers, and document workflow remain fixed.

Any proposed visual change must be presented separately and approved before use. A production problem is not permission to substitute a new layout. A report that cannot be produced with the locked template must be reported as failed rather than published in a different format.

## 2. Authoritative production sequence

1. Copy the locked Word master template.
2. Replace edition-specific text while preserving all named styles, section properties, headers, footers, fields, colors, spacing, and layout rules.
3. Build the complete Word document first. The Word document is the source of truth.
4. Validate structure and content in Word.
5. Render every Word page to images and inspect every page.
6. Export the PDF from the approved Word master. Do not independently recreate or restyle the PDF.
7. Render every PDF page to images and inspect every page.
8. Compare the Word and PDF editions for section order, record count, source links, page flow, headings, dashboard cards, register entries, and metadata.
9. Publish only after both formats pass all gates.

## 3. Page geometry and typography

- Page size: U.S. Letter, portrait.
- Page width and height: 8.5 by 11 inches.
- Left and right margins: 0.70 inch.
- Top margin: approximately 0.68 inch.
- Bottom margin: approximately 0.62 inch.
- Primary typeface: Arial.
- Body style: 10.5 point Arial, near-black `#1B252C`, 6 point space after.
- Small text: 9 point Arial, slate `#40576A`, 4 point space after.
- Source text: 8.5 point Arial, slate `#40576A`, 3 point space after.
- Register text: 9.5 point Arial, near-black `#1B252C`, 5 point space after.
- Title: 26 point, dark blue `#17365D`.
- Heading 1: 17 point bold Arial, navy `#0B2538`, 10 point space before, 7 point space after, keep with next.
- Heading 2: 12.5 point bold Arial, navy `#0B2538`, 8 point space before, 4 point space after, keep with next.
- Heading 3: 10.5 point bold Arial, navy `#0B2538`, 8 point space before, 4 point space after, keep with next.
- No body text may be reduced below the locked style sizes to force pagination.
- Direct formatting must not replace or override named styles except for deliberate inline emphasis and hyperlinks.

## 4. Fixed document structure

Every edition contains the permanent purpose and scope language followed by these nine sections, in this order and with actual Word heading styles:

1. Today's Bottom Line
2. What Changed
3. Leadership Application
4. Verified Developments and Evidence Register
5. Rolling Two-Month Location/Event Register
6. Standing Indicator Dashboard
7. Reality Check and Corrections
8. Upcoming and Watch Next
9. Balanced Close, Reading Legend and Sources

The contents guide, section numbering, heading levels, and navigation structure must remain consistent. A section heading may not appear alone at the bottom of a page. Each Heading 1 must remain with at least the first substantive paragraph or card of its section.


## 4.1 Contents-page and content-placement lock

- Page 2 is a dedicated contents page. It contains the Contents heading and exactly the nine section entries, followed by a hard page break.
- No event card, register entry, date-limited disclosure, dashboard item, reality-check item, watch item, balanced-close text, source list or other substantive report content may appear on the contents page.
- Date-limited disclosures appear only once, at the end of Section 5 immediately before Section 6.
- Section 9 must be written for the current edition and cutoff. Do not carry forward a prior edition's balanced-close paragraph or source list without explicit current-edition validation.
- During visual QA, compare the opening page, contents page, one representative event-card page, one representative register page, the complete dashboard, Sections 7 and 8, and the final source page against the October 19 Revised 1 baseline for layout continuity.

## 5. Dashboard lock

The Standing Indicator Dashboard uses the October 19 Revised 1 stacked-card layout. It must not use the defective wide three-column table design.

Each indicator is a separate vertically stacked block with:

- indicator title;
- latest material change and evidence;
- next observable development.

The following eight indicators remain in the same order unless the user approves a structural change:

1. Troops and readiness
2. Exercises
3. Mobilization
4. Industry and logistics
5. Air, missile and nuclear posture
6. Civil defence
7. Sabotage and hybrid incidents
8. Diplomacy

No indicator text may overlap, run outside the page, or be reduced to unreadable type. Content wraps vertically and may continue naturally onto another page.

## 6. Register lock

- Use location-grouped entries with Heading 2 record titles and `ER Register` narrative paragraphs.
- Preserve stable event IDs.
- Keep source links in the `ER Source` style.
- Do not replace the register with an extremely wide table.
- Do not compress entries into dense multi-column layouts.
- Do not duplicate records, disclosures, sources, or headings across sections.
- Date-limited disclosures appear exactly once in their designated subsection.
- Pagination may expand as the register grows. Content must never be omitted or shrunk merely to maintain a target page count.

## 7. Tables and dark backgrounds

- Use tables only where the baseline template uses them or where a narrow two-column structure is genuinely readable.
- Do not use a three-column narrative table for the Standing Indicator Dashboard.
- Dark navy backgrounds require explicit white `#FFFFFF` text.
- Header rows repeat across page breaks when a table spans pages.
- Rows may not split when doing so creates unreadable fragments.
- Narrative cells must wrap and remain within page margins.
- Color may supplement meaning but may not be the only carrier of meaning.

## 8. Header, footer, metadata, and anonymity

- Use the same anonymous header and footer treatment as the baseline.
- Include page numbers and issue date consistently.
- Do not add personal names, prepared-for lines, biographies, or personal bylines to the report.
- DOCX and PDF author, subject, keywords, comments, custom properties, and XMP metadata must remain anonymous.
- Required reader-facing statement: `Public-source awareness and planning brief. Not an official intelligence bulletin.`

## 9. Required automated checks

Before publication, the production process must verify:

- exactly nine primary numbered sections;
- section order matches this standard;
- all primary sections use Heading 1 styles;
- all record headings use the approved subordinate heading style;
- no duplicated stable event IDs;
- no duplicated date-limited disclosure block;
- no heading orphaned at a page bottom;
- no blank or near-blank unintended pages;
- no text outside page bounds;
- no overlapping text boxes, paragraphs, cells, or table content;
- no dark-on-dark or light-on-light text;
- dashboard contains all eight indicator titles exactly once;
- dashboard does not contain the prohibited wide three-column narrative table;
- all hyperlinks are present and functional in both Word and PDF;
- Word and PDF report the same research cutoff and record counts;
- anonymous metadata is preserved;
- Latest Edition, Archive, dated page, canonical PDF, and `editions.json` agree after publication.

## 10. Visual inspection gate

Automated checks do not replace human visual inspection. Every page of both Word and PDF must be rendered and reviewed at readable size. Reviewers must inspect the opening pages, contents, every section transition, all table and card pages, the complete dashboard, representative register pages across the document, the date-limited disclosures, final source pages, and the last page.

Publication is blocked if any known clipping, overlap, duplicated text, orphaned heading, broken link, unreadably small text, missing content, inconsistent style, or unexplained format deviation remains.

## 11. Revision naming and archive behavior

- Normal daily DOCX: `Europe Readiness Daily YYYY-MM-DD.docx`
- Normal public PDF: `Europe_Readiness_Daily_YYYY-MM-DD.pdf`
- Corrected private DOCX: `Europe Readiness Daily YYYY-MM-DD Revised N.docx`
- The canonical public PDF path may be replaced by a corrected commit because Git history preserves the prior binary.
- The dated edition page must disclose a material formatting correction while retaining the original research cutoff.
- Prior dated editions remain intact.

## 12. Prohibited production shortcuts

- No PDF-first independent layout.
- No ad hoc ReportLab replacement for the locked Word design.
- No using a previous defective edition as the styling source.
- No direct-formatting rebuild when the template is available.
- No wide narrative tables that require horizontal compression.
- No font-size reductions to solve overflow.
- No spot-check-only QA.
- No publication merely because a file was generated successfully.
- No unapproved design changes.
