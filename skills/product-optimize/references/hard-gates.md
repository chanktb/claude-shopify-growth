# Hard Gates: PDP Optimization (with Merchant-Center feed safety)

Non-negotiable gates for `product-optimize`. Failing any blocks the push. The
gates marked 🛑 also carry a **Google Merchant Center feed risk** — a mismatch
there can disapprove the product and take it out of Shopping and free listings,
which is worse than a low score. Fix 🛑 gates first, always.

The shared gates (0, 1, 2, 3, 4, 5, 13) work exactly as in the collection
module's `hard-gates.md`. This file details the PDP-specific ones.

---

## Gate 0: KB-First Factcheck (never invent a spec)

A PDP lives or dies on factual accuracy. A wrong dimension, material, or
compatibility claim is a return, a bad review, and a trust hit. Before writing,
grep `knowledge-base/*.md` for the product line and pull the real specs. Priority
order: TIER_INTERNAL (your KB) → TIER_SHOPIFY (product metafields) →
TIER_WEBFETCH (manufacturer spec page) → never guess. Log a TIER_INTERNAL gap if
the KB doesn't cover it; do not fill the gap with an estimate.

---

## Gate 7 🛑: Feed-safe `Offer` (price + availability mirror the page)

**The single most common Merchant-Center disapproval.** The `Offer.price` and
`Offer.availability` in your JSON-LD must equal the visible buy box, for the
selected variant, at all times.

Failure modes:
- Schema `price` is the compare-at (higher) price while the page shows the sale
  price → "price mismatch" disapproval.
- Schema `availability: InStock` while the variant is sold out → "availability
  mismatch" + a customer hits an unbuyable page.
- A variant product emits a single `Offer` with one variant's price → wrong for
  every other variant. Use `AggregateOffer` (lowPrice/highPrice) instead.

How to apply:
1. Bind schema to the theme's product/variant object; never hard-code a number.
2. In Step 10, fetch the live page and assert `schema.offers.price` ==
   `visible price` and `schema.offers.availability` == the real inventory state.
3. For multi-variant products, verify the `AggregateOffer` range matches the min
   and max variant prices.

---

## Gate 8: Unique copy (no manufacturer boilerplate)

The manufacturer's description is shipped to every retailer; reusing it is thin,
duplicated content that Google and AI engines discount. It also often duplicates
across your own catalog (same blurb on 12 SKUs).

Pass criteria:
- <70% similarity to the manufacturer / another retailer's copy for the SKU.
- Not duplicated across >5 of your own products (a GATE in `product-analyze`).
- Benefits-first: leads with the outcome, then the specs.

Fix: rewrite from the KB facts + real use cases. Keep the specs (facts) but the
prose, angle, and structure are yours.

---

## Gate 9: Image alt coverage

Every product image needs a descriptive `alt` (feeds Google Images + AI image
understanding + accessibility). `IMG_1234`, empty, or the raw filename fails.
Pattern: `{brand} {product} {view/attribute}` — e.g. "Acme trail bottle, lid
open, 500ml". Push `altText` on every media in Step 9; re-verify in Step 10.

---

## Gate 10 🛑: Product identifiers (GTIN / MPN)

Google Shopping requires a unique product identifier for products from a known
manufacturer: a `gtin` (barcode: UPC/EAN/ISBN) or, failing that, `brand` + `mpn`.
Missing them risks feed rejection for that item.

Pass criteria:
- Known-manufacturer product: `gtin` OR (`brand` + `mpn`) present in schema AND in
  the Shopify variant (barcode field).
- Private-label / handmade / custom: set `identifier_exists: no` in the feed and
  skip GTIN (this is legitimate — do not fabricate a barcode).

---

## Gate 11: Rating integrity

`AggregateRating` is powerful (star snippet) but policy-sensitive.

- Emit it ONLY when real, on-page reviews exist. No reviews → no rating schema.
- Never hard-code a rating value; bind it to the reviews source.
- Never double-emit: many reviews apps (Loox, Judge.me, Stamped) already inject
  `AggregateRating`. Two blocks on one page is an error. Verify exactly one.

---

## Gate 12: FAQ live render (flat `[{q,a}]`)

The PDP FAQ is the top AI-citation surface. It must render from a flat array of
`{q, a}` objects, the same discipline as the collection module — never a
schema.org `FAQPage` wrapper stored in the content metafield (that produces empty
DOM nodes). The theme builds the `FAQPage` wrapper; you provide the flat data.
Verify on the live page in Step 10 (grep the question-text class).

---

## Order of enforcement

```
Step 0.5 → Gate 0 (KB factcheck)
Step 1   → Gate 7 pre-flight (record visible price/availability)
Step 3   → Gate 2 (title length pre-check)
Steps 3-6 → Gate 3 (AI-trigger), Gate 13 (no source labels)
Step 6   → Gate 4 (em-dash), Gate 8 (unique copy)
Step 7   → Gate 1 (URL inventory)
Step 8   → Gate 7 🛑, Gate 10 🛑, Gate 11 (schema build)
Step 9   → Gate 9 (image alt on push)
Step 10  → Gates 1,2,3,4,5,7,9,12 re-verified on the live page
Step 11  → Gate 6 (composite ≥85 AND zero 🛑 feed gates)
Step 12  → Gate 14 (optional notification)
```

A run that ships with an open 🛑 gate is a feed incident, not just a quality miss.
Log it to `CHANGELOG-live-fixes.md` with a revert plan.
