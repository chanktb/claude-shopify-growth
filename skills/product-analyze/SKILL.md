---
name: product-analyze
description: >
  Audit and score a Shopify product page (PDP) on a 5-category 100-point scoring
  system built for commercial product pages (NOT collections or blogs).
  Categories: Product Copy Quality (20), SEO + Commercial Intent (25), Product
  Schema + Technical (20), Trust & Conversion (20), GEO / AI-Citation Readiness
  (15). Pulls live data via the Shopify connector + WebFetch + GSC 90d.
  Generates prioritized recommendations (Critical/High/Medium/Low) with specific
  fixes and Merchant-Center feed risk flags. Use when the user says "analyze
  product page", "audit PDP", "product page score", "check product listing",
  "rate this product page", "product SEO audit", or any Shopify product-page review.
user-invokable: true
argument-hint: "<product-url-or-handle> [--site <domain>] [--no-gsc] [--tier hero|standard|variant-parent|technical|consumable|new] [--strict] [--format markdown|json]"
license: MIT
metadata:
  author: "Khue Tran — PDP rubric modeled on the collection-analyze scoring system"
  version: "0.1.0"
  category: audit
---

# Product Analyzer: Quality Audit & Scoring for Shopify Product Pages

Scores a Shopify product page (PDP) on a 0–100 scale across 5 commerce-focused
categories. Pulls live data from the connected Shopify store (product, variants,
images, price, inventory), renders the public URL via WebFetch (markup + Product
schema), and overlays Google Search Console performance (90-day clicks /
impressions / position / CTR).

**This is NOT collection-analyze.** A PDP is the money page — it carries
transactional intent, a single-product schema (`Product` + `Offer` +
`AggregateRating`), a buy box, variants, and reviews. "Good copy" here means a
unique, benefits-first description that closes a buyer and feeds Google Shopping
+ AI Overviews — not category navigation.

Reference documents (paths from skill root):

- `references/product-rubric-100pt.md` — full per-category checklist with
  decision rules, anti-patterns, tier adjustments, and gate details
- `references/product-schema.md` — JSON-LD templates for `Product`, `Offer`,
  `AggregateRating`, `Review`, `BreadcrumbList`, and `additionalProperty` specs

## Input Handling

- **URL**: e.g. `https://your-store.com/products/{handle}`
- **Handle**: e.g. `{handle}` (pair with `--site your-store.com`)

### Flags

- `--site <domain>` — required when input is a bare handle
- `--no-gsc` — skip GSC pull (offline mode / no credentials; CTR signal falls back to neutral)
- `--tier hero|standard|variant-parent|technical|consumable|new` — override the auto-detected tier (see Step 1.5)
- `--strict` — N/A items earn 0/N instead of partial credit, surfacing content gaps directly
- `--format markdown|json` — default markdown; JSON for pipeline consumption

## Scoring Process

### Step 1: Live Data Extraction

Pull data from THREE sources, in parallel where possible:

**1a. Shopify Admin API** (via your Shopify MCP connector's `get-product` and friends):
- Product GID, title, handle, descriptionHtml, productType, vendor, tags, status
- Variants (first 20): price, compareAtPrice, sku, barcode (GTIN), inventoryQuantity, availableForSale, selectedOptions
- Images/media: count, `altText` per image, featuredMedia URL
- SEO fields (`seo.title`, `seo.description`), metafields (specs, reviews app)
- createdAt, updatedAt, publishedAt

**1b. WebFetch the public URL** — render the page and extract:
- `<title>`, meta description, canonical, OG/Twitter tags
- H1 (must equal product name, single H1)
- Description body: word count, uniqueness signal, bullet/scannability
- Buy box: visible price, compare-at, stock badge, variant selector, add-to-cart, shipping/returns near buy box
- Reviews: star rating + count visible, review block present
- JSON-LD: `Product`, `Offer`, `AggregateRating`, `Review`, `BreadcrumbList`
- Image count + zoom, spec/dimensions table presence, related-products block
- FAQ / Q&A block, comparison content

**1c. GSC 90-day pull** (`gsc-query` skill or equivalent) for the product URL:
- Total clicks, impressions, average position, CTR
- Top 10 queries with clicks/impressions/position
- Position distribution (1–3 / 4–10 / 11–20 / 21–30 / 31–100)

Skip 1c if `--no-gsc`; mark CTR-dependent SEO sub-checks as N/A.

### Step 1.5: Tier Detection

Auto-detect the product's tier — the rubric weights certain checks higher per
tier (see `references/product-rubric-100pt.md` §Tier Adjustments):

| Tier | Detection rule | Rubric emphasis |
|------|----------------|-----------------|
| **hero** | Top revenue/traffic product (GSC clicks high, or flagged best-seller) | Reviews + schema + conversion weighted highest; a schema gap is Critical |
| **variant-parent** | ≥ 5 variants (size/color/style) | Variant UX + canonical/variant-URL handling weighted higher |
| **technical** | `productType`/title implies spec-driven durables (electronics, tools, appliances, equipment) | Specs table + `additionalProperty` + compatibility weighted higher |
| **consumable** | Low-differentiation, repeat-purchase, low price | Price + availability + reviews weighted; unique-copy bar relaxed |
| **new** | Published in last 30 days | Schema + freshness weighted; Critical if `Product` schema missing |
| **standard** | Default when none of the above | Balanced weighting |

User can override with `--tier`. Pipeline mode (`product-audit-pipeline`) forces
re-detection per product.

### `--strict` mode

By default, N/A items (e.g. reviews sub-check when the store has no reviews app)
earn partial credit (1/N). With `--strict`, N/A items earn 0/N, surfacing the
content gap directly instead of masking it with vacuous full credit. Use
`--strict` for site-wide pipeline runs, before/after re-audits, and hero-tier
products.

### Step 2: Score Each Category

Load `references/product-rubric-100pt.md` for the full checklist.

#### Category 1 — Product Copy Quality (20 points)

**Design principle**: a PDP description is benefits-first and unique. The #1
failure mode is pasting the manufacturer's boilerplate (thin, duplicated across
every retailer). Lead with the benefit/use, then back it with specs.

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Product title clarity | 4 | Brand + product + key attribute + type; readable; not keyword-stuffed |
| Description depth (benefits-first) | 4 | Opens with core benefit/use, then specs; ≥150 words of unique copy |
| Unique (not manufacturer boilerplate) | 3 | <70% similarity to the manufacturer/other-retailer copy; an original angle |
| Buying-decision clarity | 3 | Answers who it's for, what problem it solves, what's in the box, how it compares |
| Human voice (AI-content signals) | 3 | ≤0.3 em-dash / 100 words; ≤3 AI-trigger phrases; **burstiness** (varied sentence length, not uniform); concrete specifics over vague filler ("high quality" / "perfect for everyone"); no formulaic scaffolding |
| Scannability | 3 | Bullets for specs/features; short paragraphs; key info above the fold |

#### Category 2 — SEO + Commercial Intent (25 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| `<title>` format + length | 4 | 50–60 chars; brand + product + key modifier; primary keyword front-loaded |
| Meta description | 3 | 120–160 chars; benefit + soft CTA (free ship / in stock / N reviews) |
| H1 = product name | 2 | Single H1, matches the product; not boilerplate |
| URL structure | 2 | `/products/{kebab-handle}`; clean; no typos |
| Canonical + variant handling | 3 | Self-canonical; variant URLs (`?variant=`) canonical to the main product (no dup content) |
| Image alt text | 2 | Product images have descriptive `alt` (not `IMG_1234` / empty) |
| GSC CTR signal | 3 | CTR ≥ benchmark at position 1–10. Position 1–10 but CTR < benchmark → title/meta drag |
| GSC position vs intent | 3 | Ranking queries match product/transactional intent (not informational leak) |
| Internal links INTO product | 3 | ≥3 inbound links (parent collection, related products, blog) with anchor variety |

#### Category 3 — Product Schema + Technical (20 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| `Product` JSON-LD present | 3 | `@type` Product with `name`, `image`, `description`, `sku` |
| `Offer` complete | 4 | `price`, `priceCurrency`, `availability`, `url`, `priceValidUntil`; **matches the visible price** |
| Brand + identifiers | 3 | `brand`; `gtin`/`mpn`/`sku` where available (Google Shopping requirement for known manufacturers) |
| `AggregateRating` + `Review` | 3 | `ratingValue` + `reviewCount` when reviews exist; individual `Review` markup |
| `BreadcrumbList` JSON-LD | 2 | Present; matches the visible breadcrumb (product ← collection ← home) |
| `additionalProperty` specs | 2 | Structured specs as `additionalProperty` / `PropertyValue` (feeds AI + rich results) |
| Valid + no errors | 2 | Passes the Rich Results Test; no schema errors; images meet minimum dimensions |
| LCP / mobile | 1 | LCP < 2.5s if measurable; else neutral |

#### Category 4 — Trust & Conversion (20 points)

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Reviews present + visible | 4 | ≥1 review; star rating + count near the top; not stale-only |
| Stock / availability clarity | 2 | In-stock / low-stock / backorder clearly stated |
| Shipping + returns info | 3 | Shipping cost/time + returns policy visible or linked near the buy box |
| Images: count + quality | 3 | ≥4 images (angles + in-use + scale); zoomable; clean first image |
| Specs / dimensions table | 3 | Structured specs table (dimensions, materials, compatibility) present |
| Cross-sell / related | 2 | "Related" / "frequently bought together" / "complete the set" block |
| USP / benefit callouts | 2 | Key benefits as scannable callouts, not buried in prose |
| Variant UX | 1 | Clear variant selector (swatch/dropdown); price + stock update per variant |

#### Category 5 — GEO / AI-Citation Readiness (15 points)

PDPs get cited in AI Overviews / ChatGPT / Perplexity for "best X", "X vs Y",
"is X good for Z". This category scores how extractable + citable the page is.

| Check | Points | Pass Criteria |
|-------|--------|---------------|
| Direct-answer product Q&A / FAQ | 4 | 3–5 Q&A answering real buyer questions (compatibility, sizing, use, care); `FAQPage` schema |
| Comparison / "vs" content | 3 | How it compares to alternatives or variants (table or prose); citable passage |
| Structured, machine-readable specs | 3 | Specs as a table **and** `additionalProperty` so AI can extract them |
| Entity clarity | 2 | Consistent brand + model + category naming across title, schema, and copy |
| Use-case / "best for" framing | 3 | States who/what it's best for (maps to long-tail "best X for Y" AI queries) |

### Step 3: GATES (Hard fail flags)

Each GATE adds a `🔴 GATE` flag at the top of the report and forces a "Critical"
recommendation. GATES do not zero the score, but several also carry a
**Merchant-Center feed risk** (Shopping disapproval):

1. **No `Product` JSON-LD AND the product is indexable** (lost Shopping + AI-citation surface)
2. **`Offer` price in schema ≠ visible price** (Merchant Center disapproval risk 🛑)
3. **`availability` schema wrong** (says `InStock` when out of stock, or vice versa) 🛑
4. **Missing `gtin`/`mpn` AND brand is a known manufacturer** (Shopping feed rejection risk 🛑)
5. **GSC: 0 clicks AND > 500 impressions in 90d** (severe title/meta drag → rewrite)
6. **Description duplicated across > 5 products** (manufacturer boilerplate → thin content)
7. **Image `alt` missing on > 50% of images** (accessibility + image-search loss)
8. **Duplicate / conflicting schema** — two `Product` blocks OR two `AggregateRating` blocks on one page (theme + a review app both emit). Invalid; Google may ignore or flag it.

> **Drift detection**: GATE 2 (schema `price` ≠ visible price) is also how you
> catch a *stale* schema — a static block that fell out of sync after a price or
> stock change fails GATE 2. The fix is to live-bind the dynamic fields (see
> `references/product-schema.md` §0), not to re-push a fresh number.

### Step 4: Generate Fix Recommendations

Each finding gets a severity tag:

- **🔴 Critical** — GATE-triggered OR a category scoring < 50% of its max
- **🟠 High** — a single check failing AND tied to traffic OR conversion loss
- **🟡 Medium** — a single check failing AND nice-to-fix
- **🟢 Low** — polish / consistency / long-tail

Each fix includes: the exact finding (current value + expected value), the
proposed change (with example markup / copy snippet), the estimated lift
(qualitative), and the location to edit (Shopify admin deep-link when possible).

### Step 5: Export Markdown Report

Write the report to:
```
output/[site]/products/[product-handle]/product-quality-score.md
```

Report sections (in order):
1. Header — product title, URL, tier, audit timestamp, version
2. Composite score (e.g. `71 / 100`) + category breakdown table
3. 🔴 GATES triggered (with 🛑 Merchant-Center feed-risk flags)
4. Critical / High / Medium / Low fixes
5. GSC Snapshot (90d clicks / imps / position / CTR + top queries)
6. Shopify Snapshot (variants, price range, inventory, image count)
7. Schema Audit (what's present vs missing, with feed-risk callouts)
8. Re-audit instructions ("re-run after fix X to verify")

JSON export available with `--format json`.

## What This Skill Does NOT Do

- Does NOT rewrite the description or title (use `/product-optimize`)
- Does NOT auto-fix schema or push changes (audit-only)
- Does NOT analyze collection pages (use `/collection-analyze`)

## Composition with Other Skills

- **After**: `product-optimize` — consumes this report as its baseline + gaps
- **Sibling**: `product-audit-pipeline` — batch all products, rank by composite score
- **Reuses**: `gsc-query` (GSC pull), `seo-schema` (Schema.org validation)

## Output Convention

Per-product artifact:
```
output/[site]/products/[product-handle]/
├── product-quality-score.md       (this skill's output)
├── product-quality-score-vN.md    (iteration history)
├── shopify-snapshot.json          (raw connector pull, for re-use)
└── gsc-snapshot.json              (raw GSC pull, for re-use)
```

This mirrors the collection module's `output/[site]/[handle]/` convention,
keeping the ledger format consistent across the kit.
