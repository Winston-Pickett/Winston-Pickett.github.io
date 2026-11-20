import fs from "node:fs";
import path from "node:path";

const root = process.cwd();
const standard = JSON.parse(fs.readFileSync(path.join(root, "site-standard.json"), "utf8"));
const failures = [];

for (const page of standard.protectedPages) {
  const file = path.join(root, page);
  if (!fs.existsSync(file)) {
    failures.push(`${page}: missing protected page`);
    continue;
  }
  const html = fs.readFileSync(file, "utf8");
  const start = html.indexOf('<header class="site-header">');
  const end = html.indexOf("</header>", start);
  const header = start >= 0 && end >= 0 ? html.slice(start, end) : "";
  if (!header) {
    failures.push(`${page}: site header missing`);
    continue;
  }
  if (standard.wordmarkHomeRequired && !header.includes("Winston Pickett home")) {
    failures.push(`${page}: Home wordmark missing`);
  }
  if (standard.contactRequired && !header.includes("contact-link")) {
    failures.push(`${page}: Contact action missing`);
  }
  for (const item of standard.navigation) {
    if (!header.includes(`>${item.label}<`)) {
      failures.push(`${page}: navigation missing ${item.label}`);
    }
  }
}

const home = fs.readFileSync(path.join(root, "index.html"), "utf8");
const cssMatch = home.match(/href="(\/_next\/static\/chunks\/[^"]+\.css)"/);
if (!cssMatch) {
  failures.push("index.html: stylesheet reference missing");
} else {
  const cssFile = path.join(root, cssMatch[1].slice(1));
  if (!fs.existsSync(cssFile)) failures.push(`${cssMatch[1]}: stylesheet missing`);
  else {
    const css = fs.readFileSync(cssFile, "utf8");
    for (const rule of [
      ".home-page .site-header{height:76px}",
      ".home-page .hero{min-height:540px}",
      ".home-page .scenario-visual{min-height:540px}",
      ".insights-page .site-header{height:76px}"
    ]) {
      if (!css.includes(rule)) failures.push(`stylesheet: locked rule changed or missing: ${rule}`);
    }
  }
}

const research = fs.readFileSync(path.join(root, "research-lab/index.html"), "utf8");
if (!research.includes("Compact desktop layout")) {
  failures.push("research-lab/index.html: compact Research Lab standard missing");
}

if (failures.length) {
  console.error("Published site standard failed:\n" + failures.map(item => `- ${item}`).join("\n"));
  process.exit(1);
}
console.log(`Published site standard verified across ${standard.protectedPages.length} pages.`);
