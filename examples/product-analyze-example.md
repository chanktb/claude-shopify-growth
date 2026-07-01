# Product Quality Score — Brand A Insulated Water Bottle

> Sanitized example output of `/product-analyze`. Store, brand, and product are
> fictional; the findings and score are representative of a typical
> un-optimized product page.

- **URL**: `https://your-store.com/products/brand-a-insulated-water-bottle`
- **Tier**: variant-parent (2 size variants) · consumable-leaning
- **Audited**: 2026-07-01 · product-analyze v0.1.0 · `--no-gsc`

## Composite: 41 / 100

| Category | Score | Notes |
|---|---:|---|
| 1 — Product Copy Quality | 8 / 20 | Manufacturer boilerplate, not benefits-first, duplicated across the catalog |
| 2 — SEO + Commercial Intent | 16 / 25 | Title 68ch (truncates); meta present but templated; canonical OK |
| 3 — Product Schema + Technical | 6 / 20 | **No `Product`/`Offer`/`AggregateRating` schema** — only Breadcrumb + Org |
| 4 — Trust & Conversion | 9 / 20 | 0 reviews; stock shown; no specs table; no related block |
| 5 — GEO / AI-Citation | 2 / 15 | No FAQ, no comparison, no machine-readable specs |
| **Total** | **41 / 100** | |

## 🔴 GATES triggered

1. **G1 — No `Product` JSON-LD** (page is indexable). The page emits
   `BreadcrumbList`, `Organization`, and `WebSite` schema, but **no `Product` or
   `Offer` block**. Result: no Google Shopping rich result, no star snippet
   eligibility, and no structured surface for AI Overviews / ChatGPT / Perplexity
   to cite. *Verified by `curl … | grep '"@type"'` — WebFetch reported "no schema"
   which was a false negative; the real gap is specifically the missing `Product`
   type.*
2. **G6 — Description duplicated across the catalog.** The exact same
   manufacturer blurb ("No UV light needed, odorless, fast drying…") appears on
   dozens of products. Thin + duplicate content; search engines discount it and
   it cannibalizes.
3. **Gate 2 — Title > 60 characters** (68ch incl. the ` – Brand A Store` suffix).
   The SERP truncates it mid-phrase. `seo.title` is null, so the theme falls back
   to the raw product title.

## Critical / High / Medium / Low fixes

### 🔴 Critical
- **Add a `Product` + `Offer` schema bundle** bound to the live variant
  (price/availability), plus `BreadcrumbList` (already present). This is the
  single highest-leverage fix: it unlocks rich results + AI citation. Keep it
  live-bound so it never drifts. → `product-optimize` Step 8.
- **Rewrite the description** (Gate G6). Replace the shared boilerplate with a
  unique, benefits-first body: lead with the outcome (insulation hours, capacity
  in real terms), then a specs table, "best for", and an FAQ. → `product-content-deep`.

### 🟠 High
- **Set `seo.title` ≤ 60ch** front-loading the primary keyword:
  e.g. `Brand A Insulated Water Bottle, 500 & 750ml` (44ch).
- **Add product reviews** (0 today). Enable/collect reviews; once real reviews
  exist, emit `AggregateRating` (never before). Adds a star snippet + trust.
- **Add a specs table** (capacity, material, insulation, weight, dimensions) and
  mirror it as `additionalProperty` in schema so AI can extract it.

### 🟡 Medium
- **Add an FAQ block** (3–5 real buyer questions: "How long does it stay cold?",
  "Is it dishwasher safe?") with `FAQPage` schema — the top AI-citation surface.
- **Per-image alt text.** All images share one generic alt (the product title
  repeated). Give each a descriptive alt (front / lid-open / in-hand / scale).
- **Add a related-products block** (cross-sell + internal links).

### 🟢 Low
- Add a one-line "best for" statement to catch "best bottle for X" AI queries.
- Tighten the meta description to a specific benefit + CTA (it's currently a
  templated "Shop … at Brand A Store").

## Schema Audit

| Type | Present? | Notes |
|---|---|---|
| `BreadcrumbList` | ✅ | Correct, matches visible breadcrumb |
| `Organization` / `WebSite` | ✅ | Site-level, fine |
| `Product` | ❌ | **Missing — Critical (G1)** |
| `Offer` (price/availability) | ❌ | Missing; add live-bound |
| `AggregateRating` | ❌ | Correctly absent (0 reviews) — add only when reviews exist |
| `additionalProperty` (specs) | ❌ | Missing |
| `FAQPage` | ❌ | Missing |

## Shopify Snapshot

- Variants: 2 — `500ml` ($5.99, was $15.50), `750ml` ($11.00, was $23.25); both in stock (7 units total)
- Identifiers: `mpn` set via feed metafield; **`barcode`/GTIN empty** (add GTIN for a known-manufacturer product, or set `identifier_exists: no`)
- Images: 4 (all with the same generic alt)
- Reviews: 0

## GSC Snapshot

`--no-gsc` — skipped for this example. With GSC connected, this section shows
90-day clicks / impressions / avg position / CTR and the top queries, and enables
the CTR-drag and intent-leak checks in Category 2.

## Re-audit

After applying the Critical + High fixes, re-run:
```
/product-analyze https://your-store.com/products/brand-a-insulated-water-bottle
```
Target: composite ≥ 85 **and** zero 🛑 feed-risk gates. The `Product`+`Offer`
schema fix alone typically moves Category 3 from ~6 to ~17.
