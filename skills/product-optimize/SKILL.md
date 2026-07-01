---
name: product-optimize
description: >
  End-to-end workflow to optimize a Shopify product page (PDP) from a low
  baseline composite score to 85+/100 for SEO + GEO (AI-search) and conversion.
  Combines product-analyze (audit) + product-content-deep (unique benefits-first
  description, specs table, FAQ, comparison) + the Product schema bundle + a
  buy-box/trust pass. Includes HARD gates: zero invented specs, schema mirrors
  the visible price/availability (Merchant-Center feed-safe), unique copy (no
  manufacturer boilerplate), image alt coverage, zero em-dash, zero AI-trigger
  phrases. Use when the user says "optimize product page", "optimize PDP",
  "rewrite product description", "fix product listing SEO", "improve product
  page", or "scale product optimization".
user-invokable: true
argument-hint: "<product-handle-or-url> [--site <domain>] [--tier hero|standard|variant-parent|technical|consumable|new] [--dry-run] [--no-gsc]"
license: MIT
metadata:
  author: "Khue Tran — PDP playbook modeled on the collection-mega-hub-optimize workflow"
  version: "0.1.0"
  category: optimize
  composite_target: "85+ / 100"
---

# Product Page Optimizer: End-to-End PDP Workflow

Takes a Shopify product page from "manufacturer-boilerplate description + thin
schema + no reviews surface" to a unique, benefits-first PDP with a complete,
feed-safe `Product` schema bundle, a specs table, an FAQ, comparison content,
and clean internal links. Composite target: **≥85/100** per the
`product-analyze` rubric, with **zero Merchant-Center feed-risk gates**.

**This is the money-page playbook.** It chains `product-analyze` (audit),
`product-content-deep` (description generation), the Shopify connector
(product/metafield/schema push), and a buy-box/trust pass. Every step has a HARD
gate that must pass before the next runs.

## When to invoke

- After `product-analyze` returns composite < 80 for a product
- When the description is manufacturer boilerplate (duplicated, thin)
- When a product has traffic (GSC impressions) but a snippet/schema gap
- Pipeline mode: chained from `product-audit-pipeline` for batch optimization

## When NOT to invoke

- Products being discontinued / hidden (waste of effort)
- Products where price/inventory is in flux mid-launch (schema will churn)
- A whole collection at once — audit first (`product-audit-pipeline`), then run
  this per prioritized product

## The Workflow

### Step 0.5 — MANDATORY: knowledge-base factcheck (HARD GATE 0)

Before writing ANY product copy, grep your product knowledge base at
`knowledge-base/*.md` for this product line. Extract the real specs, materials,
compatibility, use cases, and differentiators. **Never invent a spec.** If the
KB doesn't cover it, pull from the Shopify product metafields + the
manufacturer's spec page (WebFetch) and log a TIER_INTERNAL gap. See
`knowledge-base/README.md`. This is the same Gate 0 discipline as the collection
module: TIER_INTERNAL → TIER_SHOPIFY → TIER_WEBFETCH → never guess.

### Step 1: Baseline pull

Pull in parallel:
- **Shopify**: product (title, descriptionHtml, productType, vendor, tags,
  status, seo fields), variants (price, compareAtPrice, sku, barcode/GTIN,
  inventory, options), images + `altText`, metafields.
- **Live page** (WebFetch): `<title>`, meta, H1, buy-box (price/stock/variant
  selector), reviews block, JSON-LD (`Product`/`Offer`/`AggregateRating`/
  `Breadcrumb`), image count/alt, specs table, FAQ, related block.
- **GSC 90d** (optional, `--no-gsc` to skip): clicks, impressions, position,
  CTR, top queries.

Output: `output/[site]/products/[handle]/baseline-snapshot.json`.

**🚨 Feed pre-flight**: record the visible price + availability now — every later
step must keep the `Offer` schema mirroring them (Gate 7).

### Step 2: Tier detection

Detect tier (hero / variant-parent / technical / consumable / new / standard) per
the `product-analyze` §Tier Adjustments. Tier decides which gaps are Critical and
which content sections the description needs (Step 6).

### Step 3: SEO title (`seo.title`) rewrite

Pattern: `{Brand} {Product} {Key Attribute} {Modifier}` front-loading the primary
keyword, ≤60ch. Do **not** rename `product.title` casually — it cascades to the
buy box, cart, orders, and feed. Optimize the `seo.title` metafield instead;
rename `product.title` only with explicit owner approval.

**HARD GATE 2**: HTML `<title>` ≤60ch on the live page (Step 10).

### Step 4: Meta description rewrite (120–160ch)

Pattern: `{benefit} + {key spec} + {soft CTA: free ship / N reviews / in stock}`.

**HARD GATE 3 (AI-trigger phrases)**: 0 instances of "Discover", "Experience",
"Elevate", "Explore", "Delve into", "flawless", "seamless", "curated", etc.
Replace with concrete verbs and specifics.

### Step 5: Buy-box & trust pass

Verify (and flag for the owner where you can't push): reviews visible near the
top, stock/availability clear, shipping + returns near the buy box, ≥4 images
with alt, variant selector clarity. These drive Cat 4 and several feed signals.

### Step 6: Description rewrite (invoke `product-content-deep`)

Generate a unique, benefits-first description. Section shape (tier-aware):

1. **Lead** — the outcome / core use in the first 1-2 sentences (not the SKU).
2. **Key benefits** — 3-5 scannable bullets tying features to outcomes.
3. **Specs table** — dimensions, material, capacity, compatibility (structured;
   mirrors the `additionalProperty` schema).
4. **How to use / setup** — short steps where relevant.
5. **Who it's best for / use cases** — maps to "best X for Y" AI queries.
6. **Comparison** — how it compares to alternatives or the next variant up.
7. **FAQ** — 3-5 real buyer questions (flat `[{q,a}]`), feeds `FAQPage` schema.

**HARD GATE 8 (unique copy)**: <70% similarity to the manufacturer copy AND not
duplicated across >5 of your own products. Manufacturer boilerplate = re-write.

**HARD GATE 4 (em-dash)**: 0 em-dash (`—`) across the description + FAQ. Run
`scripts/reduce_emdash.py`.

**HARD GATE 13 (no source labels)**: never expose "the KB", "knowledge base",
"per our data" in customer copy. Write facts directly as the store's own product
knowledge.

### Step 7: Internal linking

Link the PDP into the graph, all verified live (Gate 1):
- Up to the **parent collection**.
- Across to **related / complementary products** (2-5).
- Out to a **relevant blog post** (buying guide) if one exists.

**HARD GATE 1 (URL inventory)**: never write a `/collections/` or `/products/` or
`/blogs/articles/` link without confirming it in an inventory pull.

### Step 8: Product schema bundle (audit-first, never duplicate)

Do NOT blindly push a fresh schema block. First check what the theme + review
apps already emit (from Step 1 / `product-analyze`), then act:

- **Theme already emits `Product` + `Offer`** (Dawn and most themes do) → verify it
  is correct and **live-bound** (price/availability from the variant object, not a
  frozen value); add ONLY the missing pieces (usually `additionalProperty` +
  `FAQPage`). Never add a second `Product` block.
- **A review app already emits `AggregateRating`** → leave it; never double-emit.
- **No schema present** → add the full bundle via a theme snippet bound to live
  objects (push to a DUPLICATE theme for preview).

Split by volatility: **dynamic fields (price, availability, rating) render live
from Liquid** so they self-update when price/stock/reviews change; **static fields
(specs, description, brand, gtin, FAQ) are content you push once.** See
`../product-analyze/references/product-schema.md` §0 for the decision table.

**🚨 HARD GATE 7 (feed-safe schema) 🛑**: `Offer.price` and `Offer.availability`
MUST mirror the visible buy box byte-for-byte (per selected variant; use
`AggregateOffer` for a price range). A mismatch is a Merchant-Center disapproval.
**HARD GATE 10 (identifiers) 🛑**: `gtin`/`mpn` present for known-manufacturer
products (or `identifier_exists: no` for private-label). **HARD GATE 11**:
`AggregateRating` only when real reviews exist; never hard-code; never double-emit
(check the reviews app isn't already injecting it).

### Step 9: Push

Push in a batched update: `descriptionHtml`, `seo.title`, `seo.description`, spec
+ FAQ metafields, and image `altText` (Gate 9: every image has descriptive alt).
Schema that the theme renders from metafields goes via metafields; theme-file
edits (a `product-structured-data` snippet) go to a DUPLICATE theme for preview
(the MCP safelist commonly blocks writes to the live theme).

### Step 10: Pre-publish verification

Delegate the mechanical sweep to a cheap sub-agent (`Agent(subagent_type:Explore,
model:haiku, ...)`) and read the 1-line summary:
1. Em-dash = 0; AI-trigger = 0 across title + meta + description + FAQ.
2. HTML title ≤60ch on the live page.
3. Every internal link returns 200 (HEAD check).
4. **Schema `price`/`availability` == visible buy box** (Gate 7, re-verified live).
5. Every image has non-empty `alt` (Gate 9).
6. FAQ renders (flat `[{q,a}]`, not a schema.org wrapper) — grep the live page.

**HARD GATE 5 (link health)**: 0 broken internal links or block publish.

### Step 11: Live re-score

Run `product-analyze <live-url>`. **HARD GATE 6**: composite ≥85/100 **AND zero
🛑 feed-risk gates** (G2/G3/G4). A high score with an open feed gate still fails —
fix the feed gate first.

### Step 12: Publish notification (optional, Gate 14)

If a channel is configured, run `scripts/notify_collection_publish.py` (reuse it
with `--tier product` or the closest tier icon) after Step 11 passes. Skipped
cleanly when unconfigured.

## The HARD Gates

| Gate | Check | Pass criteria |
|------|-------|---------------|
| **0** | KB-first factcheck | Pull real specs from `knowledge-base/*.md` before writing; never invent a spec |
| 1 | URL inventory | Every internal link verified in an inventory pull |
| 2 | Title length | HTML `<title>` ≤60ch live |
| 3 | AI-trigger phrases | 0 across title + meta + description + FAQ |
| 4 | Em-dash | 0 across description + FAQ |
| 5 | Link health | 0 broken internal links |
| 6 | Composite score | ≥85/100 live AND zero 🛑 feed gates |
| **7** 🛑 | Feed-safe schema | `Offer.price` + `availability` mirror the visible buy box exactly |
| 8 | Unique copy | <70% vs manufacturer; not duplicated across >5 own products |
| 9 | Image alt | Every product image has descriptive `alt` |
| **10** 🛑 | Identifiers | `gtin`/`mpn` present for known-manufacturer products (or `identifier_exists: no`) |
| 11 | Rating integrity | `AggregateRating` only when real reviews exist; never hard-coded or double-emitted |
| 12 | FAQ live render | FAQ renders from a flat `[{q,a}]` source (not a schema.org wrapper) |
| 13 | No source labels | 0 mentions of "KB" / "knowledge base" in customer copy |
| 14 | Notification | (optional) sent after Step 11, or skipped cleanly |

🛑 = Merchant-Center feed risk. Failing any gate blocks the push.

## Composition with other skills

- **Phase 0/11** (audit + re-score): `product-analyze`
- **Phase 6** (description gen): `product-content-deep`
- **Schema**: `../product-analyze/references/product-schema.md`
- **Pipeline mode**: `product-audit-pipeline` batches this over a prioritized list

## Output convention

```
output/[site]/products/[handle]/
├── baseline-snapshot.json      # Step 1
├── seo-rewrite.json            # Step 3-4 title + meta
├── description.html            # Step 6 unique benefits-first body
├── schema-bundle.json          # Step 8 Product/Offer/Rating/Breadcrumb/FAQ
├── prepush-verify.json         # Step 10
└── composite-score-final.md    # Step 11 ≥85 + 0 feed gates
```

## Reference docs

- `references/hard-gates.md` — gate details + Merchant-Center feed-safety notes
- `../product-analyze/references/product-schema.md` — schema templates
- `../product-analyze/references/product-rubric-100pt.md` — the scoring rubric
