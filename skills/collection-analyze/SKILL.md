---
name: collection-analyze
description: >
  Audit and score Shopify collection pages on a 5-category 100-point scoring
  system custom-built for commercial category pages (NOT blog posts). Categories:
  Collection Copy Quality (20), SEO + Commercial Intent Match (25), Product
  Curation Quality (20, warning-only), Technical + Schema (15), UX & Conversion
  Signals (20). Pulls live data via Shopify connector + WebFetch + GSC 90d.
  Generates prioritized recommendations (Critical/High/Medium/Low) with specific
  fixes. Detects cross-page cannibalization when 2+ collections supplied. Use
  when user says "analyze collection", "audit collection", "collection score",
  "check collection quality", "collection review", "rate this collection",
  "collection health check", or any Shopify category-page review.
user-invokable: true
argument-hint: "<collection-url-or-handle> [--site <domain>] [--cannibal-pair <handle2>] [--no-gsc] [--no-curation-check] [--tier hub|brand|sub|tool|new|mega-hub] [--strict] [--format markdown|json]"
license: MIT
metadata:
  author: "Khue Tran (ktbteam) — collection-analyze rubric modeled on blog-analyze by The Minh Nguyen (NextGrowth.AI)"
  version: "0.2.1"
  last_modified: "2026-06-21"
  recent_change: "v0.2.1 — Content-placement rubric overhaul: Cat 1.1 caps above-grid copy at 20-40w tagline (was 40-120w); Cat 1.2 redefines below-grid as FAQ accordion 300-500w (was 150w long-form). Above-grid >60w now triggers Cat 5.9 penalty (product cards pushed below fold). Field lesson: collection pages must prioritize product visibility; long-form copy lives in expandable FAQ below grid, not above. v0.2.0 was Add --strict + mega-hub tier + mandate GSC in pipeline mode."
  category: audit
---

# Collection Analyzer: Quality Audit & Scoring for Shopify Category Pages

Scores Shopify collection pages on a 0–100 scale across 5 commerce-focused
categories. Pulls live data from the connected Shopify store (product list, sort
order, image, ruleset), renders the public URL via WebFetch (markup + schema),
and overlays Google Search Console performance (90-day clicks / impressions /
position / CTR).

**This skill is NOT blog-analyze.** Collection pages live by different rules:
commercial intent dominates, prose is short, schema is `CollectionPage` +
`ItemList` not `BlogPosting`, and "good copy" means a sentence that closes a
buyer — not 1,800 words of E-E-A-T.

Reference documents (paths from skill root):

- `references/collection-rubric-100pt.md` — full per-category checklist with
  decision rules and anti-patterns
- `references/curation-warning-rules.md` — product-curation warning ledger
  (active / sales 6mo / in stock / category price tier). **Warning-only** —
  these never reduce the composite score; they appear in the report under a
  separate "Curation Watchlist" section.
- `references/schema-collectionpage.md` — JSON-LD templates for `CollectionPage`,
  `ItemList`, `BreadcrumbList`, and `Product` schema with `aggregateRating`

## Input Handling

- **URL**: e.g. `https://your-store.com/collections/{handle}`
- **Handle**: e.g. `{handle}` (pair with `--site your-store.com`)
- **Cannibal pair**: pass `--cannibal-pair <handle2>` to score 2 collections and
  compute a cross-page intent-overlap report (Jaccard on resolved queries +
  product-set overlap + title-handle similarity)

### Flags

- `--site <domain>` — required when input is a bare handle
- `--cannibal-pair <handle2>` — score the second handle as well; emit a
  combined "cannibal-report.md" alongside both individual scorecards
- `--no-gsc` — skip GSC pull (offline mode or no credentials; CTR signal in
  SEO category falls back to neutral)
- `--no-curation-check` — skip Shopify product-list pull (page-only audit)
- `--tier hub|brand|sub|tool|new` — override the auto-detected tier (see Step 1.5)
- `--format markdown|json` — default markdown; JSON for pipeline consumption

## Scoring Process

### Step 1: Live Data Extraction

Pull data from THREE sources, in parallel where possible:

**1a. Shopify Admin API** (via your Shopify MCP connector's `get-collection` and friends):
- Collection GID, title, handle, description (HTML body)
- Hero image URL (or `null` flag)
- Product count, sortOrder (MANUAL / BEST_SELLING / ALPHA_ASC / CREATED / etc)
- ruleSet (smart-collection logic) or manual product list
- updatedAt, publishedAt

**1b. WebFetch the public URL** — render the page and extract:
- `<title>`, meta description, canonical, OG/Twitter tags
- H1 (must equal collection title, or be intentional override)
- Above-grid copy length + word count
- Below-grid copy presence + word count (long-form SEO copy, optional but a
  major lift for commercial intent)
- Visible price range, stock badge presence, "Sort by" dropdown options, filter
  facets (collection sidebar)
- JSON-LD schema blocks: `CollectionPage`, `ItemList`, `BreadcrumbList`,
  `Product` (with `aggregateRating` if any)
- Number of product cards above the fold (mobile + desktop)
- Pagination type (numeric / infinite scroll / load-more)

**1c. GSC 90-day pull** (`gsc-query` skill or equivalent) for the collection URL:
- Total clicks, impressions
- Average position
- CTR
- Top 10 queries with their clicks/impressions/position
- Position distribution (1–3 / 4–10 / 11–20 / 21–30 / 31–100)

Skip 1c if `--no-gsc` is set; mark SEO sub-checks that depend on CTR as N/A.

### Step 1.5: Tier Detection

Auto-detect the collection's tier — the rubric weights certain checks higher
per tier (see `references/collection-rubric-100pt.md` §Tier Adjustments):

| Tier | Detection rule | Rubric emphasis |
|------|----------------|-----------------|
| **mega-hub** (v0.2.0+) | `productsCount ≥ 2000` AND ruleSet is OR-union of 3+ product types | Sub-navigation required; filter sidebar Brand+Color+Type+Size all required; "browse by brand" tiles below grid |
| **hub** | `productsCount ≥ 1000` (and < 2000) OR title is a generic category (e.g. "Electronics", "Apparel & Accessories") | Schema + hero image + sort/filter UX weighted higher |
| **brand** | Title starts with a brand name AND `productsCount` 100–999 | SEO title format + brand-keyword H1 weighted higher |
| **sub** | Title is a sub-collection ("Brand A Spring 2026", "Brand B Winter Collection", `productsCount` < 100) | Freshness + new-arrival schema weighted higher |
| **tool** | Title contains "Tool", "Equipment", "Hardware", "Device", "Accessory" | Curation price-tier check stricter (technical/hardware items have a high price floor — configure per store; see curation-warning-rules.md) |
| **new** | Published in last 30 days | Tier `sub` weights + Critical fix if schema missing |

User can override with `--tier`. Pipeline mode (collection-audit-pipeline)
forces re-detection per collection.

### `--strict` mode (v0.2.0+)

By default, N/A items (e.g. Cat 1.5 em-dash compliance when body is empty)
earn partial credit (1/3) — the rubric assumes "absence cannot violate".
With `--strict`, N/A items earn 0/N, surfacing the *content gap* directly
instead of masking it with vacuous full credit.

Use `--strict` for:
- Site-wide pipeline runs (don't let vacuous-credit hide systemic gaps)
- Re-audits comparing before/after (need an honest baseline)
- Hub-tier collections (high expectations — partial credit misleads)

Example: a collection audited without `--strict` scored 50/100. With
`--strict`: ~44/100. The 6-point delta is exactly the "vacuous credit" that
run earned by having zero copy to evaluate.

### Step 2: Score Each Category

Load `references/collection-rubric-100pt.md` for the full checklist.

#### Category 1 — Collection Copy Quality (20 points)

**Design principle (v0.2.1)**: Collection pages PRIORITIZE PRODUCT
VISIBILITY. Long-form copy lives in a below-grid expandable FAQ, NOT in a
wall of text above the grid. Above-grid copy must be a single-sentence
tagline (20–40 words) — anything longer pushes product cards below the
fold and triggers a Cat 5.9 penalty.

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Above-grid tagline (1 sentence) | 4 | **20–40 words**, single sentence. Positions the collection + USP. NOT a paragraph. |
| Below-grid FAQ accordion (expandable, default collapsed) | 4 | **300–500 words across 3–5 Q&A pairs**. Q&A format unlocks AI citation surface (ChatGPT/Perplexity prefer Q&A). FAQ accordion is crawlable but doesn't block scroll. |
| Voice match BRAND.md | 3 | Tone matches `sites/[site]/BRAND.md`; no AI-flavored boilerplate; no taboo phrases |
| Buying-decision clarity | 3 | Tagline + FAQ together answer: who is this for, what to pick, what's different vs sibling collection |
| Em-dash + AI-trigger compliance | 3 | ≤0.3 em-dash / 100 words across tagline + FAQ; AI trigger phrases ≤3 instances |
| Free of duplicate/template boilerplate | 3 | Compare FAQ block to ≥5 other collections on the site; flag >80% similarity. Generic "shop our X collection" tagline = boilerplate. |

**v0.2.1 enforcement notes**:
- Above-grid copy >60 words → −2 pts Cat 5.9 (above-fold density penalty)
- Above-grid copy >120 words → −4 pts Cat 5.9 + advisory: "convert to expandable accordion or move to below-grid FAQ"
- Below-grid copy as long-form paragraph (no accordion) is acceptable but
  scores lower than FAQ format because FAQ wins AI citation (Q&A is the
  preferred surface)
- "FAQ schema" `FAQPage` JSON-LD recommended on the FAQ block (separate
  from CollectionPage schema) — adds +1 bonus to Cat 4.4 if present

#### Category 2 — SEO + Commercial Intent Match (25 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| `<title>` format + length | 4 | 30–60 chars; "{Brand or Category} + {Modifier} + Site Brand"; includes primary keyword |
| Meta description format + length | 3 | 120–160 chars; ends with a soft CTA + USP (free ship / bulk pricing / next-day) |
| H1 match user intent | 3 | H1 = collection title OR a search-friendly rewrite; not boilerplate |
| URL structure | 2 | `/collections/{kebab-handle}`; no typos (cf. `brand-a-premium-line-colletion`); ≤6 segments |
| Canonical | 2 | Self-canonical; no canonical pointing to a different collection |
| Hreflang (if multi-locale) | 2 | Present and correct, or N/A for single-locale stores |
| GSC CTR signal | 3 | CTR ≥ 2% at average position 1–10. If position 1–10 but CTR <1.5% → title/meta drag |
| GSC position vs intent | 3 | Top 5 queries match collection title intent (not blog/PDP queries leaking in) |
| Internal links INTO collection | 3 | ≥3 internal links from blog/PDP/other collections (require anchor variety — see anchor-quality guidance below) |

#### Category 3 — Product Curation Quality (20 points, warning-only)

Pulls product list via Shopify connector. Per `references/curation-warning-rules.md`:

| Check | Points | Warning (does NOT reduce score) |
|-------|--------|---------------------------------|
| All products ACTIVE status | 4 | Draft/archived in collection → warning list |
| All in-stock OR last-purchase < 60d | 4 | OOS + cold → warning |
| Category-appropriate price tier | 4 | Per your store's configured category price-tier table (see curation-warning-rules.md — define floor/ceiling per product category). Out-of-tier → warning |
| Collection size healthy | 3 | hub ≥ 100 / brand 30–500 / sub 10–100 / tool 20–80 / new ≥ 5 |
| Sort order matches intent | 3 | BEST_SELLING for hub; MANUAL with curated top for brand campaign; ALPHA for tool by SKU |
| Cross-brand contamination | 2 | A single-brand collection (e.g. "Brand A") contains 0 non-Brand-A products (unless explicitly a multi-brand bundle) |

**Important**: by design, curation issues are reported as warnings under
"Curation Watchlist" in the report, but DO NOT subtract from the composite
score. The 20 points are earned by *running* the check successfully and
surfacing the warnings — not by passing them.

If `--no-curation-check` is set, this category falls back to a flat 15/20
(neutral) and the report includes a "Curation check skipped" notice.

#### Category 4 — Technical + Schema (15 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| `CollectionPage` JSON-LD | 3 | Present with `@type`, `name`, `description`, `url`, `mainEntity` |
| `ItemList` JSON-LD | 3 | Present with `itemListElement` array including position + url + name + image per product (or `BreadcrumbList` ItemList alternative) |
| `BreadcrumbList` JSON-LD | 2 | Present; matches visible breadcrumb on page |
| `Product` schema per card | 2 | Inline product cards expose Product schema OR linked PDPs have it (verify 3-sample) |
| Pagination rel + canonical | 2 | `rel=next/prev` correct OR canonical strategy explicit (e.g. all-pages → page 1) |
| Mobile renders < 3.5s LCP | 2 | If PageSpeed / CrUX available; else neutral |
| No mixed content / console errors | 1 | Clean dev console on load |

#### Category 5 — UX & Conversion Signals (20 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Hero image present (not `null`) | 3 | Listed collection image OR header hero block visible. Penalize hub/brand tier with `image=null` heavily. |
| Price visible on cards | 3 | Compare-at strikethrough + sale price; "Bulk/wholesale price" badge if applicable |
| Stock indicator | 2 | "Low stock" / "In stock" / "Out of stock" badge visible |
| Sort dropdown | 2 | Best Selling + Price + New + Alpha all available |
| Filter sidebar | 3 | ≥3 facets for hub/brand (color, type, size, brand) — sub/tool tier exempt |
| Social proof | 2 | Reviews count + star rating visible on cards (≥30% of products) |
| Mobile grid sane | 2 | 2-column grid mobile; image:text ratio matches; card height uniform |
| Sticky add-to-cart / quick-buy | 2 | Either quick-add hover button OR mobile sticky cart pill |
| Above-the-fold density | 1 | ≥6 product cards visible above the fold on desktop. **v0.2.1 penalty cascade**: above-grid copy 60–120w → −2 pts here (cap at 0); >120w → −4 pts here (cap at 0). Above-grid copy is a product-visibility tax. |

### Step 3: GATES (Hard fail flags)

The GATES below do not zero the score, but each adds a `🔴 GATE` flag at the
top of the report and forces a "Critical" recommendation:

1. **Typo in handle or title** (e.g. "colletion")
2. **Hero image `null` AND tier ∈ {hub, brand}** (high-traffic collection without hero)
3. **JSON-LD `CollectionPage` missing AND productCount > 50** (lost organic CTR + AI-citation surface)
4. **GSC: 0 clicks AND >500 impressions in last 90d** (severe title/meta drag — content fundamental rewrite needed; same rule as blogs: "0 clicks = rewrite")
5. **Cannibal pair: Jaccard query overlap ≥ 0.6** (force-merge or differentiate decision)
6. **Cross-brand contamination > 20% in a brand collection** (curation failure — surfaced as Critical even though scoring is warning-only)

### Step 4: Cross-Page Cannibal Check (only if `--cannibal-pair` set)

Compute and report:
- Title token Jaccard
- Handle token Jaccard
- GSC query Jaccard (top 50 queries each)
- Product GID set overlap (Shopify connector)
- SERP shared-URL count (DataForSEO optional, else N/A)

Output a verdict — **MERGE** / **DIFFERENTIATE** / **PARALLEL OK** — with
specific fix steps. See `references/collection-rubric-100pt.md` §Cannibal
Verdict Rules.

### Step 5: Generate Fix Recommendations

Each finding gets a severity tag:

- **🔴 Critical** — GATE-triggered OR composite category < 50% of max
- **🟠 High** — single check failing AND tied to traffic loss OR conversion loss
- **🟡 Medium** — single check failing AND nice-to-fix
- **🟢 Low** — polish / consistency / long-tail

Each fix recommendation includes:
- The exact finding (with current value + expected value)
- The proposed change (with example markup / copy snippet where applicable)
- Estimated lift (qualitative: "fixes CTR drag" / "unlocks schema-rich result")
- File or location to edit (Shopify admin URL deep-link when possible)

### Step 6: Export Markdown Report

Write the report to:
```
output/[site]/[collection-handle]/collection-quality-score.md
```

Report sections (in order):
1. Header — collection title, URL, tier, audit timestamp, version
2. Composite score (e.g. `73 / 100`) + category breakdown table
3. 🔴 GATES triggered (if any)
4. Critical / High / Medium / Low fixes
5. Curation Watchlist (warning-only)
6. GSC Snapshot (90d clicks / imps / position / CTR + top queries)
7. Shopify Snapshot (product count, sort order, ruleSet summary)
8. Schema Audit (what's present vs missing)
9. (If cannibal pair) Cannibal Verdict section
10. Re-audit instructions ("re-run after fix X to verify")

JSON export available with `--format json` — same structure, machine-readable.

## What This Skill Does NOT Do

- Does NOT rewrite the collection description (use `/collection-refresh` —
  Phase 2 skill, not yet built)
- Does NOT auto-fix schema or title (audit-only)
- Does NOT publish or push changes to Shopify
- Does NOT analyze individual product pages (use a future `/pdp-analyze` skill)

## Composition with Other Skills

- **Before**: `blog-audit-pipeline` (sister at the blog tier) — they share the
  workspace convention
- **After**: `collection-refresh` (Phase 2) — consumes this report as input
- **Sibling**: `collection-cannibal` (Phase 2) — site-wide cannibal map
- **Sibling**: `collection-audit-pipeline` (Phase 2) — batch all collections,
  rank by composite score

## Reference Skills Reused

- `gsc-query` — for the GSC 90d pull in Step 1c
- `gsc-performance` — for position distribution detail (optional)
- `seo-schema` — for Schema.org validation against Google guidelines

## Output Convention

Per-collection artifact:
```
output/[site]/[collection-handle]/
├── collection-quality-score.md       (this skill's output)
├── collection-quality-score-vN.md    (iteration history)
├── shopify-snapshot.json             (raw connector pull, for re-use)
├── gsc-snapshot.json                 (raw GSC pull, for re-use)
└── (if cannibal) cannibal-report.md  (cross-page verdict)
```

This matches `output/[site]/[slug]/quality-score.md` for blogs, keeping
ledger format consistent across the toolkit.
