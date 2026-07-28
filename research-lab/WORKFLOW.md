# Finance Transformation Research Lab Update Policy

## Purpose

The Research Lab is an indexed collection of reported finance benchmarks, survey findings, industry volumes, and respondent expectations. It presents sourced data without recommendations, implementation guidance, or instructions for using the information.

## Canonical files

- `data.json` is the only source of published Research Lab records.
- `data.schema.json` defines the required record structure.
- `update-log.json` records each published change.
- `index.html` renders the dataset and must not contain manually maintained research cards.

## Eligible subjects

- Finance transformation
- FP&A
- Planning, forecasting, and budgeting
- Finance data, systems, and enterprise performance management
- AI use, governance, and outcomes in finance
- Finance operating models
- Risk, resilience, treasury, liquidity, and working capital

## Source standards

Prefer original publications from regulators, public institutions, research firms, professional associations, universities, standard setters, and named corporate research programs. Use the original publisher's page or report rather than a secondary article whenever it is available.

A record must have:

- a stable HTTPS source URL;
- a named publisher and publication;
- an exact reported metric or clearly identified benchmark;
- a reporting period, publication date, or study year;
- sample size, population, benchmark coverage, or an explicit statement that the public source does not provide it;
- enough source context to distinguish a historical result, current benchmark, survey response, estimate, or forecast.

## Exclusions

Do not publish:

- recommendations, advice, implementation steps, or "how to use" material;
- unsupported claims, anonymous statistics, unattributed graphics, or AI-generated summaries presented as sources;
- duplicate findings already represented by the same source and reporting period;
- marketing claims that lack a stated method, respondent base, benchmark population, or traceable underlying publication;
- a calculated combination of percentages from different studies;
- a source that cannot be opened and verified at publication time.

## Record preparation

Preserve the meaning, population, timeframe, qualifiers, and units reported by the source. Paraphrase concisely without strengthening causal language or converting respondent expectations into observed results. Identify estimates and forecasts explicitly.

Assign the next available ID within the record's theme:

- `P` - Planning & forecasting
- `D` - Data & systems
- `A` - AI in finance
- `O` - Operating model
- `R` - Risk & resilience
- `C` - Cash & working capital

## Validation before publication

1. Confirm every required schema field.
2. Confirm IDs and source URLs are unique where appropriate.
3. Compare each metric, timeframe, coverage statement, and qualifier with the original source.
4. Confirm that the record contains no recommendation or implementation guidance.
5. Confirm that `lastUpdated`, `addedOn`, `updatedOn`, and `source.accessedOn` use ISO `YYYY-MM-DD` dates.
6. Confirm `data.json` remains valid JSON and all active records render.
7. Open every newly added source URL.

If any validation is uncertain, do not publish the candidate.

## Change control

Add verified records to `data.json`, update `lastUpdated`, and append one entry to `update-log.json`. Do not automatically delete existing records. Mark a record `superseded` or `archived` only when the original publisher corrects, withdraws, or replaces it, and document the reason in the update log.

After publishing, verify the live Research Lab, record count, theme filters, source links, privacy link, and Google Analytics tag.
