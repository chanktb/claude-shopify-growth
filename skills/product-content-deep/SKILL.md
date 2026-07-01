---
name: product-content-deep
description: >
  Generate a unique, benefits-first product-page (PDP) description for a
  Shopify product (7 tier-aware sections: Lead, Key Benefits, Specs Table,
  How to Use, Best For / Use Cases, Comparison, FAQ). Replaces manufacturer
  boilerplate with original copy that satisfies the product-analyze Category 1
  (Product Copy Quality) and Category 5 (GEO/AI-Citation) rubrics. Outputs an
  HTML body for `descriptionHtml` + a flat FAQ array for `FAQPage` schema.
  Pairs with product-analyze (audit) and product-optimize (push + schema).
  Use when user says "write product description", "product copy", "PDP
  content", "rewrite product listing", "unique product description",
  "product-content-deep".
user-invokable: true
argument-hint: "<product-url-or-handle> [--site <domain>] [--tier variant-rich|technical-hardware|bundles-sets|consumables-bulk|seasonal-drops|specialty-premium] [--length 200|350|500] [--no-comparison] [--faq-count 3-5]"
license: MIT
metadata:
  author: "Khue Tran"
  version: "0.1.0"
  last_modified: "2026-07-01"
  recent_change: "v0.1.0 — Initial release. 7-section tier-aware template, flat FAQ array, HTML body output for descriptionHtml."
  category: content
---

# Product Content Deep: Benefits-First PDP Description Generator

Generates the unique, benefits-first product description that replaces
manufacturer boilerplate on a Shopify product page (PDP). Solves the #1
failure mode flagged by `product-analyze` Category 1 (Product Copy Quality):
pasting the manufacturer's thin, duplicated copy instead of writing an
original, buyer-focused description. This skill brings PDP copy depth on par
with a well-scoped landing page while keeping the buy-box the primary
conversion element (description supports the sale, it doesn't replace the
buy box).

## When this skill applies

**Any product page missing a unique description**, flagged by `product-analyze`
Category 1 < 15/20 or a GATE 6 hit ("description duplicated across > 5
products"). Applies to a single product per invocation; batch it from
`product-audit-pipeline` or `product-optimize` for multiple SKUs.

**Tier requirement**: none, this skill can run on any product. The tier
(see below) changes section emphasis and length, not whether the skill
applies.

## Architecture

Content is generated as an HTML body for the product's own
`descriptionHtml` field (NOT a metafield, unlike the collection module) plus
a companion flat FAQ array pushed to a metafield that feeds `FAQPage` schema.

```
Product.descriptionHtml
  └─ Lead + Key Benefits + Specs Table + How to Use + Best For + Comparison

Product.metafields.custom.faq_jsonld  (flat [{q,a}], same discipline as collections)
  └─ rendered as an on-page Q&A block + FAQPage JSON-LD by the theme
```

This pairs with the schema bundle in
`../product-analyze/references/product-schema.md` — the specs table section
below must use the same names/values as the `additionalProperty` block, and
the FAQ array must stay flat (never a schema.org wrapper) so the theme can
build both the visible accordion and the JSON-LD from one source.

## Category Taxonomy (tier-aware emphasis)

Detect (or accept via `--tier`) which of these six generic-ecommerce
categories the product belongs to. Each shifts section depth and the
unique-copy bar:

| Tier | Detection signal | Emphasis |
|------|-------------------|----------|
| **variant-rich** | ≥5 variants (size/color/style), e.g. apparel, footwear | Specs table covers the variant matrix; Comparison section leans on "which variant/size to pick" |
| **technical-hardware** | Spec-driven durable, e.g. electronics, tools, appliances | Deeper Specs Table + Comparison (vs. the next model up or a competitor spec); How to Use is mandatory (setup steps) |
| **bundles-sets** | Multi-item kit or set, e.g. a starter set, gift bundle | Key Benefits emphasizes "what's in the box" + value vs. buying separately; Comparison = bundle vs. à la carte |
| **consumables-bulk** | Low-differentiation, repeat-purchase, e.g. refills, pantry goods | Relaxed unique-copy bar (short Lead + Benefits is fine); emphasize value/reorder cadence and pack-size options over deep specs |
| **seasonal-drops** | Time-boxed or limited-run item, e.g. holiday decor, limited colorway | Lead emphasizes timing/availability; Best For leans on gifting/occasion use cases |
| **specialty-premium** | Higher price point, niche audience, e.g. premium home goods, boutique cosmetics | Deepest Lead + Comparison (justify the price tier); Best For narrows to the specific buyer profile, not a general audience |

If none of the six signals is clear, default to a balanced weighting across
all seven sections at the mid-length tier (350w).

## 7 Sections (default template)

Each section is a heading + body inside `descriptionHtml`, except the FAQ,
which is a separate flat array. Total target: 200–500 words in the
description body depending on `--length` and tier (technical-hardware and
specialty-premium default to 500w; consumables-bulk defaults to 200w).

### Section 1: Lead (1–2 sentences, ~20–40w)

The outcome or core use up front, not the SKU or brand recitation. Answer
"what does this do for me" before "what is this."

**Required elements**:
- Opens with the benefit or use case, not the product name repeated from
  the H1
- No AI-trigger phrases (see Em-Dash + AI-Trigger Compliance below)

**Anti-pattern**: "The Acme Wireless Charger is a wireless charger made by
Acme that charges your phone wirelessly." Rewrite: "Drop your phone on this
pad and it starts charging in under two seconds, no cable, no fumbling in
the dark."

### Section 2: Key Benefits (3–5 bullets, ~60–100w)

Feature → outcome bullets, not a spec dump. Each bullet leads with the
benefit, then names the feature that delivers it.

Format:
```html
<ul class="pdp-content__benefits">
  <li><strong>{Benefit}</strong>: {feature that delivers it, 1 sentence}</li>
</ul>
```

**Required elements**:
- 3–5 bullets, each a single sentence
- No bullet duplicates the Lead sentence
- At least one bullet ties to a buying-decision concern (durability,
  compatibility, ease of use, value)

### Section 3: Specs Table (structured, mirrors `additionalProperty`)

A semantic `<table>` with the same names and values you'll push to the
`additionalProperty` schema block (per
`../product-analyze/references/product-schema.md` §3). Keep them in sync;
a mismatch is a citability + trust gap, not just a schema gate.

```html
<table class="pdp-content__specs">
  <thead>
    <tr><th scope="col">Spec</th><th scope="col">Value</th></tr>
  </thead>
  <tbody>
    <tr><th scope="row">Material</th><td>{value}</td></tr>
    <tr><th scope="row">Dimensions</th><td>{L x W x H}</td></tr>
    <tr><th scope="row">Weight</th><td>{value}</td></tr>
    <tr><th scope="row">Compatibility</th><td>{value}</td></tr>
  </tbody>
</table>
```

Rows vary by category (apparel: material/fit/care; electronics:
power/ports/compatibility; home goods: dimensions/material/capacity;
cosmetics: volume/ingredients-summary/skin-type). Never invent a row value;
pull from the KB or Shopify metafields (see Factcheck Discipline below).

### Section 4: How to Use / Setup (where relevant, ~50–100w)

Short ordered steps for first use, setup, or application. Mandatory for
**technical-hardware**; optional (skip if truly not applicable) for
consumables-bulk and bundles-sets where "use" is self-evident.

```html
<ol class="pdp-content__howto">
  <li><strong>{Step name}</strong>: {1 sentence}</li>
</ol>
```

### Section 5: Who It's Best For / Use Cases (~40–80w)

States who/what it's best for, mapping to long-tail "best X for Y" AI
queries. 2–4 short use-case statements, not a generic "everyone will love
this."

Format: short paragraph or a 2–4 item `<ul>`, e.g.:
```html
<ul class="pdp-content__best-for">
  <li>{Use case 1}: {why it fits}</li>
  <li>{Use case 2}: {why it fits}</li>
</ul>
```

### Section 6: Comparison (~40–100w, prose or table)

How this product compares to alternatives or the next variant up. Tier
shapes the comparison target:
- **variant-rich**: this size/color vs. the others in the same line
- **technical-hardware**: this model vs. the next tier up, or vs. a common
  competitor spec point (no disparaging claims, factual deltas only)
- **bundles-sets**: bundle price/value vs. buying items à la carte
- **consumables-bulk**: this pack size vs. other pack sizes (value per
  unit)
- **seasonal-drops**: this drop vs. the standard/year-round version
- **specialty-premium**: this tier vs. the brand's entry-level option,
  justifying the price gap with concrete differences

Can skip with `--no-comparison` when there is truly no valid comparison
target (single-SKU brand-new product with no line siblings).

### Section 7: FAQ (3–5 Q&A, flat array, NOT part of `descriptionHtml`)

Real buyer questions (compatibility, sizing, use, care, returns), written as
a **flat array**, never a schema.org wrapper:

```json
[
  { "q": "{buyer question}", "a": "{direct answer, 1-3 sentences}" },
  { "q": "{buyer question}", "a": "{direct answer, 1-3 sentences}" }
]
```

`--faq-count` controls 3–5 (default 4). The theme renders the visible
accordion and the `FAQPage` JSON-LD from this same flat source (see
`../product-analyze/references/product-schema.md` §5).

## Generation Process

### Step 0.5: MANDATORY knowledge-base factcheck (HARD GATE 0)

Before writing ANY copy, grep your product knowledge base at
`knowledge-base/*.md` for this product line. Extract real specs, materials,
compatibility, use cases, and differentiators. **Never invent a spec.** If
the KB doesn't cover it, pull from Shopify product metafields, then the
manufacturer's spec page (WebFetch), and log a gap rather than guessing.
Same TIER_INTERNAL → TIER_SHOPIFY → TIER_WEBFETCH discipline as
`collection-content-deep` and `product-optimize`.

### Step 1: Pull product data

Pull via the Shopify connector:
- Title, handle, existing `descriptionHtml` (source of any real facts worth
  keeping; do not blindly discard), productType, vendor, tags
- Variants: price, compareAtPrice, sku, barcode, options (informs the
  Specs Table + variant-rich Comparison)
- Images + existing `alt` text
- Existing metafields: `custom.faq_jsonld` if present (don't duplicate
  themes already covered), any specs/additionalProperty metafields already
  populated

### Step 2: Detect tier

Auto-detect per the Category Taxonomy table above, or accept `--tier`
override. This decides section emphasis, default length, and how strict
the unique-copy bar is (relaxed for consumables-bulk, strictest for
specialty-premium and technical-hardware).

### Step 3: Identify comparison target

For variant-rich: pull sibling variants/options. For technical-hardware and
specialty-premium: identify the next tier up or the most common
alternative named in the KB. For bundles-sets: pull the à la carte prices
of the bundle's components. Skip per `--no-comparison` if none applies.

### Step 4: Generate per-section content

For each of the 7 sections, generate text using:
- KB facts (Step 0.5) — never invented specs
- Store-specific facts (pricing, shipping, returns) only where relevant to
  Key Benefits or Comparison
- Tier-specific emphasis (Category Taxonomy table)

### Step 5: Em-dash + AI-trigger compliance & Readability Constraints

Rule: keep em-dash usage very low, ≤0.3 em-dash per 100 words across ALL
copy (description + FAQ). Use colons / periods instead. Run
`scripts/reduce_emdash.py` before finalizing.

**Readability & Paragraph Rules (CRITICAL for mobile UX)**:
- **Max Paragraph Length**: every `<p>` MUST be short (2–4 sentences max, or
  ≤80 words).
- **Scannable Layout**: bullets for benefits/best-for, a semantic table for
  specs, bold lead-ins for key points. No wall-of-text paragraphs.

Self-check before push:
- Count em-dashes in generated body + FAQ (ratio ≤0.3/100w)
- No paragraph exceeds 4 sentences or 80 words
- No AI trigger phrases: "discover", "elevate", "seamless", "curated",
  "delve into", "in conclusion", "navigate the landscape", "in today's
  fast-paced", "it's important to note", "let's explore", "experience the
  difference"
- No internal source labels: never write "per our knowledge base", "the
  KB", "internal data" in customer-facing copy. State facts directly as the
  store's own product knowledge.

**Anti-AI-detection (human voice)** — the trigger blocklist alone is not enough;
the stronger tells are rhythm and vagueness:
- **Burstiness**: vary sentence length. Mix short, punchy lines with longer ones;
  uniform same-length sentences read as machine-generated.
- **Concrete over vague**: replace generic claims ("high quality", "perfect for
  everyone", "premium materials") with a specific KB fact (the actual material,
  the measured capacity, the real use case). Specificity is the #1 human signal
  on a PDP and also the thing a buyer actually needs.
- **Vocabulary diversity**: don't reuse the same adjective ("great", "amazing")
  across sections; don't open every bullet the same way.
- **No formulaic scaffolding**: avoid "Not only... but also", "Whether you're...
  or...", and "Looking for X? Look no further" openers.

### Step 6: Unique-copy check (HARD GATE, ties to product-analyze Cat 1.3)

Compare the generated description against the manufacturer's copy (if
known) and against your own other product descriptions. Target: <70%
similarity to manufacturer boilerplate, and not duplicated across >5 of
your own products. **consumables-bulk gets a relaxed bar**: near-identical
low-differentiation items (e.g. the same formula in different pack sizes)
can share most of the Lead + Benefits, but the Specs Table and pack-size
Comparison must still be unique per listing.

### Step 7: HTML structure

Wrap each `descriptionHtml` section in:
```html
<section class="pdp-content__section">
  <h2 class="pdp-content__heading">{Section Title}</h2>
  <div class="pdp-content__body">
    <!-- section content -->
  </div>
</section>
```

FAQ is written separately as `faq.json` (flat array), not inside
`descriptionHtml`.

### Step 8: Verified internal links (where the section calls for one)

Any link into a parent collection, a sibling product, or a blog post named
in Best For / Comparison must be confirmed against a live URL inventory
pull first. Never invent a `/products/`, `/collections/`, or
`/blogs/articles/` path.

## Composition with other skills

- **Before**: `product-analyze` (identifies which PDPs need a description
  rewrite and which tier applies)
- **After**: `product-optimize` (pushes `descriptionHtml` + FAQ metafield +
  schema bundle live, runs the pre-publish gate sweep, re-scores)
- **Schema ref**: `../product-analyze/references/product-schema.md` (specs
  table must mirror `additionalProperty`; FAQ must mirror `FAQPage`)
- **Reads from**: `knowledge-base/*.md` (product facts), existing
  `descriptionHtml` (salvageable real facts)
- **Writes to**: `description.html` + `faq.json` per product (consumed by
  `product-optimize` Step 6/9, not pushed directly by this skill)

## What this skill does NOT do

- Does NOT push content to Shopify (that's `product-optimize`, which also
  runs the HARD gate sweep before publish)
- Does NOT generate or edit product images (use the `blog-image` skill or
  a dedicated image pipeline)
- Does NOT audit or score a PDP (that's `product-analyze`; run it first to
  confirm this skill is needed, and after to confirm the lift)
- Does NOT modify price, inventory, or variant data
- Does NOT emit the `Product`/`Offer`/`AggregateRating` schema itself (that
  bundle is built in `product-optimize` Step 8, this skill only supplies
  the specs table and FAQ data it consumes)

## Output convention

Per-product artifact:
```
output/[site]/products/[handle]/
├── description.html      ← HTML body for descriptionHtml (this skill's output)
└── faq.json              ← flat [{q,a}] array for the FAQ metafield (this skill's output)
```

This mirrors the `output/[site]/products/[handle]/` convention already used
by `product-analyze` and `product-optimize`, keeping the ledger format
consistent across the kit. `product-optimize` reads both files directly in
its Step 6/9.
