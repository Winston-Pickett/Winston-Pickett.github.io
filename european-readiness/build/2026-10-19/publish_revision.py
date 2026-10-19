from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[3]
SECTION = ROOT / "european-readiness"
CANONICAL_PDF = SECTION / "editions" / "Europe_Readiness_Daily_2026-10-19.pdf"
DATED_PAGE = SECTION / "2026-10-19" / "index.html"
LANDING = SECTION / "index.html"
EDITIONS = SECTION / "editions.json"

DATE_LONG = "October 19, 2026"
CUTOFF_LONG = "October 19, 2026, 10:25 a.m. EDT (America/Detroit)"
DAILY_WINDOW = "October 18, 2026, 2:05 p.m. EDT through October 19, 2026, 10:25 a.m. EDT"
ROLLING_WINDOW = "August 19, 2026 through the research cutoff"


def validate_and_publish(source_pdf: Path) -> tuple[int, int, str]:
    if not source_pdf.exists() or source_pdf.stat().st_size <= 0:
        raise RuntimeError(f"Missing converted PDF: {source_pdf}")

    doc = fitz.open(source_pdf)
    page_count = len(doc)
    if page_count != 45:
        raise RuntimeError(f"Expected 45 pages in corrected edition, found {page_count}")

    all_text = "\n".join(page.get_text("text") for page in doc)
    required = [
        "1. Today's Bottom Line",
        "2. What Changed Since the Prior Complete Issue",
        "3. Leadership Application",
        "4. Verified Developments and Evidence Register",
        "5. Rolling Two-Calendar-Month Location/Event Register",
        "6. Standing Indicator Dashboard",
        "7. Reality Check and Corrections",
        "8. Upcoming and Watch Next",
        "9. Balanced Close, Reading Legend and Sources",
    ]
    missing = [x for x in required if x not in all_text]
    if missing:
        raise RuntimeError(f"Missing required sections: {missing}")

    dashboard_page = None
    for idx, page in enumerate(doc):
        text = page.get_text("text")
        if "6. Standing Indicator Dashboard" in text and "Troops and readiness" in text:
            dashboard_page = idx
            break
    if dashboard_page is None:
        raise RuntimeError("Corrected dashboard page was not found")

    dashboard_text = doc[dashboard_page].get_text("text")
    for label in [
        "Troops and readiness",
        "Exercises",
        "Mobilization",
        "Industry and logistics",
        "Air, missile and nuclear posture",
        "Civil defence",
        "Sabotage and hybrid incidents",
        "Diplomacy",
    ]:
        if dashboard_text.count(label) != 1:
            raise RuntimeError(f"Dashboard label count is not one for: {label}")

    blank = [idx + 1 for idx, page in enumerate(doc) if len(page.get_text("text").strip()) < 20]
    if blank:
        raise RuntimeError(f"Unexpected blank or near-blank pages: {blank}")

    links = sum(len(page.get_links()) for page in doc)
    outlines = len(doc.get_toc())
    if links < 200 or outlines < 150:
        raise RuntimeError(f"Navigation validation failed: links={links}, outlines={outlines}")

    metadata = doc.metadata or {}
    metadata.update({
        "title": "Europe Readiness Daily 2026-10-19 Revised 1",
        "author": "",
        "subject": "",
        "keywords": "",
        "creator": "Europe Readiness Daily",
        "producer": "LibreOffice and PyMuPDF",
    })
    doc.set_metadata(metadata)

    CANONICAL_PDF.parent.mkdir(parents=True, exist_ok=True)
    temp_pdf = CANONICAL_PDF.with_suffix(".tmp.pdf")
    doc.save(temp_pdf, garbage=4, deflate=True, clean=True)
    doc.close()
    temp_pdf.replace(CANONICAL_PDF)

    size = CANONICAL_PDF.stat().st_size
    digest = hashlib.sha256(CANONICAL_PDF.read_bytes()).hexdigest()
    return page_count, size, digest


def update_site(page_count: int, size: int, digest: str) -> None:
    kb = max(1, round(size / 1024))

    dated = DATED_PAGE.read_text(encoding="utf-8")
    dated = re.sub(r"\d+ pages · PDF · \d+ KB", f"{page_count} pages · PDF · {kb} KB", dated)
    dated = re.sub(r"<dt>Research cutoff</dt><dd>.*?</dd>", f"<dt>Research cutoff</dt><dd>{CUTOFF_LONG}</dd>", dated, flags=re.S)
    dated = re.sub(r"<dt>Daily coverage window</dt><dd>.*?</dd>", f"<dt>Daily coverage window</dt><dd>{DAILY_WINDOW}</dd>", dated, flags=re.S)
    dated = re.sub(r"<dt>Rolling register window</dt><dd>.*?</dd>", f"<dt>Rolling register window</dt><dd>{ROLLING_WINDOW}</dd>", dated, flags=re.S)
    dated = re.sub(r"<dt>File</dt><dd>.*?</dd>", f"<dt>File</dt><dd>{page_count} pages · {size:,} bytes · Final revised PDF</dd>", dated, flags=re.S)
    dated = re.sub(r"<code>[0-9a-fA-F]{64}</code>", f"<code>{digest}</code>", dated)

    revision_note = (
        '<p class="er-archive-warning"><strong>Formatting revision:</strong> '
        'Revised October 19, 2026 to correct layout defects in the PDF and Word editions. '
        'The research cutoff, evidence classifications and substantive reporting are unchanged.</p>'
    )
    if "Formatting revision:" not in dated:
        marker = '<section class="er-shell er-record">'
        dated = dated.replace(marker, marker + revision_note, 1)
    DATED_PAGE.write_text(dated, encoding="utf-8")

    landing = LANDING.read_text(encoding="utf-8")
    latest_start = landing.index('<article class="er-latest-card">')
    latest_end = landing.index('</article>', latest_start) + len('</article>')
    latest = landing[latest_start:latest_end]
    latest = re.sub(
        r"\d+ pages · PDF · \d+ KB · Research cutoff: 10:25 a\.m\. EDT",
        f"{page_count} pages · PDF · {kb} KB · Research cutoff: 10:25 a.m. EDT",
        latest,
    )
    landing = landing[:latest_start] + latest + landing[latest_end:]

    archive_start = landing.index('id="archive"')
    row_start = landing.index('<tr>', landing.index('<tbody>', archive_start))
    row_end = landing.index('</tr>', row_start) + len('</tr>')
    row = landing[row_start:row_end]
    if 'datetime="2026-10-19"' not in row:
        raise RuntimeError("October 19 is not the first archive row")
    row = re.sub(r"\d+ pages · \d+ KB", f"{page_count} pages · {kb} KB", row)
    landing = landing[:row_start] + row + landing[row_end:]
    LANDING.write_text(landing, encoding="utf-8")

    data = json.loads(EDITIONS.read_text(encoding="utf-8"))
    found = False
    for entry in data.get("editions", []):
        if entry.get("date") == "2026-10-19":
            entry["pages"] = page_count
            entry["bytes"] = size
            entry["status"] = "final"
            entry["revision"] = "Revised 1"
            found = True
            break
    if not found:
        raise RuntimeError("October 19 entry was not found in editions.json")
    EDITIONS.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    dated_after = DATED_PAGE.read_text(encoding="utf-8")
    landing_after = LANDING.read_text(encoding="utf-8")
    editions_after = json.loads(EDITIONS.read_text(encoding="utf-8"))
    checks = {
        "dated_page_count": f"{page_count} pages · PDF · {kb} KB" in dated_after,
        "dated_cutoff": CUTOFF_LONG in dated_after,
        "dated_daily_window": DAILY_WINDOW in dated_after,
        "dated_checksum": digest in dated_after,
        "revision_note": "Formatting revision:" in dated_after,
        "latest": f"{page_count} pages · PDF · {kb} KB · Research cutoff: 10:25 a.m. EDT" in landing_after,
        "archive": f"{page_count} pages · {kb} KB" in landing_after,
        "editions_date": editions_after["editions"][0]["date"] == "2026-10-19",
        "editions_pages": editions_after["editions"][0]["pages"] == page_count,
        "editions_bytes": editions_after["editions"][0]["bytes"] == size,
    }
    failed = [k for k, v in checks.items() if not v]
    if failed:
        raise RuntimeError(f"Post-update verification failed: {failed}")


def main() -> None:
    if len(sys.argv) != 2:
        raise SystemExit("usage: publish_revision.py converted.pdf")
    pages, size, digest = validate_and_publish(Path(sys.argv[1]))
    update_site(pages, size, digest)
    print(json.dumps({"pages": pages, "bytes": size, "sha256": digest, "pdf": str(CANONICAL_PDF)}, indent=2))


if __name__ == "__main__":
    main()
