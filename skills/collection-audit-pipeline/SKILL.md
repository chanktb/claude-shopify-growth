---
name: collection-audit-pipeline
description: >
  Site-wide collection audit orchestrator for Shopify stores. Pulls ALL
  collections via Shopify connector pagination, runs a 2-tier audit (Tier 1
  metadata-only quick-scan on all collections + Tier 2 full collection-analyze
  deep-scan on bottom-quartile candidates), detects site-wide cannibal pairs
  via title/handle/product overlap matrix, surfaces 10 site-wide patterns,
  and produces a ranked portfolio report (HTML + per-collection JSON +
  ranked refresh queue). Use when user says "audit all collections", "site
  collection audit", "collection portfolio", "rank my collections", "find
  worst collections", or any whole-site Shopify category-page review.
user-invokable: true
argument-hint: "<site-domain> [--tier-2-top N] [--no-tier-2] [--no-gsc] [--cannibal-only] [--format html|md|json]"
license: MIT
metadata:
  author: "Khue (ktbteam)"
  version: "0.1.0"
  last_modified: "2026-06-21"
  recent_change: "v0.1.0 — Initial release. 2-tier pipeline (metadata quick-scan all + deep-scan bottom-quartile) + site-wide cannibal detection."
  category: audit
---

# Collection Audit Pipeline: Site-Wide Portfolio Analyzer

Sister skill to `blog-audit-pipeline` but for Shopify collection pages.
Runs a 2-tier audit across ALL collections on a site (typically 50–300 for
mid-size Shopify stores), surfacing patterns + cannibal pairs + a prioritized
refresh queue.

Reference documents:
- `references/tier-1-quick-scan.md` — Tier 1 metadata-only checklist
  (Shopify-connector-only, no WebFetch). Scores 0–50 per collection.
- `references/cannibal-detection.md` — Site-wide cannibal pair matrix logic
- `references/portfolio-report-template.md` — output HTML structure

## Input Handling

- **Site domain** — e.g. `your-store.com` (resolves to Shopify connector)
- The pipeline assumes the Shopify connector is already authenticated for
  the target shop. Verify with `get-shop-info` before running.

## Flags

- `--tier-2-top N` (default: 20) — number of bottom-Tier-1 collections to
  promote to full Tier-2 deep-scan via `collection-analyze`
- `--no-tier-2` — Tier 1 only (fastest, ~5 minutes for 200 collections)
- `--no-gsc` — skip GSC pull for Tier 2 collections
- `--cannibal-only` — skip scoring entirely, run only the cannibal detection
  matrix on all collections (~2 minutes)
- `--format html|md|json` — default html for portfolio dashboard; md for
  human-readable; json for downstream consumption

## Pipeline Phases

### Phase 0 — Connector check (10 sec)

Verify Shopify connector is authenticated and matches the site domain:
```
get-shop-info → confirm domain matches argv[1]
```
If mismatch, fail fast with "switch-shop required" instruction.

### Phase 1 — Bulk metadata pull (1–3 min for ≤300 collections)

Paginate `search_collections` 50/page until `hasNextPage = false`. Cache
to `workspace/articles/[site]/_pipeline/shopify-collections-all.json`.

Fields collected per collection:
- `id`, `handle`, `title`, `updatedAt`
- `productsCount`
- `image.url` or null
- `sortOrder` (MANUAL / BEST_SELLING / ALPHA_ASC / etc)
- `ruleSet.appliedDisjunctively` + `ruleSet.rules[]`

### Phase 2 — Tier detection (in-memory, fast)

For each collection, apply tier rules from `collection-analyze` SKILL.md:
- mega-hub: productsCount ≥ 2000 AND ruleSet OR-union ≥ 3 product-types
- hub: 1000–1999 or generic-category title
- brand: 100–999 + brand-prefix title
- sub: <100 + sub-collection naming
- tool: title contains "Bit"/"Lamp"/"Drill"/"Tool"/"Brush"
- new: published in last 30 days

### Phase 3 — Tier 1 quick-scan score (in-memory)

For each collection, score against Shopify-metadata-only checks (no
WebFetch needed). See `references/tier-1-quick-scan.md` for full rubric:

| Check | Max | Detection |
|---|---|---|
| Image present (hub/brand) | 5 | `image != null` |
| Handle has no typo | 5 | Regex match common typos (`colletion`, doubled chars, etc) |
| Title is not "Do not DELETE" | 4 | Title doesn't contain debt markers |
| Sort order matches tier expectation | 3 | hub → BEST_SELLING / sub → MANUAL |
| Product count in tier range | 3 | hub ≥100 / brand 30-999 / sub 10-200 / tool 20-150 |
| Cross-brand contamination check (brand tier) | 3 | Smart rule has consistent VENDOR/TAG anchor |
| Smart rule complexity | 3 | OR-union ≤10 conditions; warn ≥10 |
| Has been updated recently | 2 | updatedAt within 90 days |
| Title format consistency | 2 | No "Colletion", no "Ver1/Ver 1/V1" mix, no all-caps mid-sentence |

Total Tier 1 max: 30 pts.

### Phase 4 — Site-wide pattern statistics

Compute and report on the full collection set:
- % image:null by tier
- % handle typo
- % "Do not DELETE" admin debt
- Tier distribution (mega-hub / hub / brand / sub / tool / new counts)
- Sort-order distribution
- Smart-rule complexity histogram
- Most-recently-updated vs stale-90d split

### Phase 5 — Site-wide cannibal detection

For every pair of collections (O(n²) but with cheap title-prefix bucketing):

1. **Title token Jaccard** ≥ 0.5 → candidate
2. **Handle token Jaccard** ≥ 0.5 → candidate
3. **Smart-rule tag overlap** ≥ 0.5 → candidate
4. Combined → cannibal-pair report with verdict suggestion (MERGE / DIFFERENTIATE / PARALLEL OK)

See `references/cannibal-detection.md` for the matrix logic. Output:
`workspace/articles/[site]/_pipeline/cannibal-pairs.md`

Special-case detection: explicit version naming (V1/V2/Ver1/Ver 2/B1) →
default to DIFFERENTIATE. Field lesson: version-numbered collections (e.g.
"Builder Gel V1" vs "Builder Gel V2") usually represent distinct product
generations sold in parallel, not duplicate/cannibalizing pages — treat them
as PARALLEL OK unless product overlap is near-total.

### Phase 6 — Bottom-quartile selection for Tier 2

Sort all collections by Tier 1 score ascending. Pick bottom-N (default 20):
- Skip "Do not DELETE" admin debt (not real-traffic candidates)
- Skip Tier 1 score = 0 with productCount < 10 (probably orphaned)
- Surface 20 actionable candidates with biggest lift potential

### Phase 7 — Tier 2 deep-scan dispatch

For each bottom-quartile collection, dispatch
`collection-analyze <url> --tier <auto-detected> --strict` and collect the
full 100-pt scorecard.

If `--no-gsc` not set, mandate GSC pull for each.

### Phase 8 — Portfolio report assembly

Output:
- `workspace/articles/[site]/_pipeline/portfolio-report.md` — main report
- `workspace/articles/[site]/_pipeline/refresh-queue.md` — ranked action list
- `workspace/articles/[site]/_pipeline/cannibal-pairs.md` — detected pairs
- `workspace/articles/[site]/_pipeline/site-patterns.md` — 10-pattern stats
- `workspace/articles/[site]/[handle]/collection-quality-score.md` — per
  bottom-quartile collection (from Tier 2 dispatch)

## Phase pre-requisites (don't skip)

| Phase | Exit criterion |
|---|---|
| 0 | Connector authenticated + domain matches |
| 1 | All collections in JSON cache, count >= 10 (else nothing to audit) |
| 2 | Every collection has tier assigned |
| 3 | Tier 1 scores in distribution |
| 4 | Pattern stats computed |
| 5 | Cannibal-pair list emitted |
| 6 | Bottom-N picked, list saved |
| 7 | Per-collection full scorecards saved (if Tier 2 enabled) |
| 8 | All report files written |

## Cost estimate (rough, per mid-size site ≈ <N> collections)

- Phase 1 (pagination): ~6 Shopify connector calls
- Phase 2–6: in-memory, no API calls
- Phase 7 Tier 2 (default 20 collections): ~20 × (1 Shopify + 1 WebFetch + 1
  GSC) = ~60 API calls. Optional skip with `--no-tier-2`.
- Phase 8: file writes only

Total: ~70 API calls + ~30 minutes wall-clock for the default config.

## What this skill does NOT do

- Does NOT push fixes to Shopify (audit-only)
- Does NOT pull full product list per collection (curation check stays
  deferred; pipeline doesn't have time budget for it)
- Does NOT publish or modify any storefront data
- Does NOT replace `collection-analyze` for single-page deep audits — that
  skill remains the canonical "I want to deep-dive THIS collection" tool

## Composition

- **Calls**: `collection-analyze` (per bottom-quartile collection in Phase 7)
- **Reads from**: Shopify connector + GSC connector
- **Writes to**: `workspace/articles/[site]/_pipeline/` + per-collection
  artifacts

## Output convention

```
workspace/articles/[site]/_pipeline/
├── shopify-collections-all.json     (Phase 1 cache)
├── tier-1-scores.json               (Phase 3 output, all collections scored)
├── site-patterns.md                 (Phase 4 stats)
├── cannibal-pairs.md                (Phase 5 detected pairs)
├── refresh-queue.md                 (Phase 6 ranked list)
└── portfolio-report.md              (Phase 8 main deliverable)

workspace/articles/[site]/[handle]/
└── collection-quality-score.md      (Phase 7, bottom-quartile only)
```

## Re-run / re-audit

Pass `--resume` to skip Phase 1 if JSON cache < 24h old. Useful when
iterating on report format or re-running Tier 2 only.
