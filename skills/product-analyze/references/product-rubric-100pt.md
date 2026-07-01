# Product Page Rubric: 100 Points (decision rules + anti-patterns)

Deep reference for `product-analyze`. The SKILL.md has the summary tables; this
file has the decision rules, anti-patterns, tier adjustments, and gate details.

Composite = Cat1 (20) + Cat2 (25) + Cat3 (20) + Cat4 (20) + Cat5 (15) = 100.

---

## Category 1 — Product Copy Quality (20)

**The core anti-pattern: manufacturer boilerplate.** The same paragraph the
brand ships to every retailer is thin, duplicated content. Google and AI engines
both discount it. The fix is a unique, benefits-first rewrite that leads with the
outcome and backs it with specs.

Decision rules:
- **Benefits-first** = the first sentence names the outcome or use case, not the
  SKU or a spec. "Keeps drinks cold for 24 hours on a full-day hike" beats
  "Double-wall vacuum-insulated 500ml bottle."
- **Uniqueness** — if >70% of the description matches the manufacturer copy or
  another retailer's PDP for the same product, score the uniqueness check 0.
  (Duplicate description across >5 of your own products is a GATE.)
- **Scannability** — a wall of prose with no bullets caps this at 1/3. Specs and
  features belong in bullets or a table; prose carries the story.
- **Buying-decision clarity** — the copy must answer: who is this for, what
  problem does it solve, what's in the box, and how does it compare. Missing 2+
  of these caps the check at 1/3.

## Category 2 — SEO + Commercial Intent (25)

- **Title tag** — front-load the primary keyword; `{Brand} {Product} {Key
  Attribute} | {Site}` within ~60 chars. Avoid stuffing multiple keywords.
- **Variant canonical (critical for PDPs)** — Shopify emits `?variant=` URLs.
  Every variant URL must canonical to the clean product URL, or you split ranking
  signal across near-duplicate pages. A variant URL that self-canonicalizes is a
  High finding.
- **Image alt** — descriptive alt on the main images (feeds Google Images +
  accessibility). `IMG_1234`, empty, or the raw filename fails.
- **CTR benchmark** — configure per store; a reasonable default is ~3-5% at
  position 1-3, ~1.5-3% at 4-10. Below benchmark while ranking top-10 = title/meta
  drag → rewrite the snippet, not the ranking.
- **Intent leak** — if the ranking queries are informational ("how to clean X")
  rather than transactional ("buy X", "X price"), the PDP is competing with a
  blog surface; note it and route the informational demand to a blog post that
  links here.

## Category 3 — Product Schema + Technical (20)

This is the highest-leverage category for a PDP because it feeds **both** Google
Shopping/rich results **and** AI Overviews.

- **`Offer` must mirror the page.** The single most common Merchant-Center
  disapproval is `price` or `availability` in schema disagreeing with the visible
  buy box. Verify byte-for-byte. This is a GATE.
- **Identifiers.** For products from a known manufacturer, Google Shopping wants
  `gtin` (barcode) or `mpn`. Missing them risks feed rejection for that product.
  Private-label / handmade products are exempt (`identifier_exists: no`).
- **`AggregateRating`** — only emit it when real reviews exist; fabricated or
  hard-coded ratings are a policy violation. If reviews exist on-page but aren't
  in schema, that's a missed rich-result (star snippet) → High.
- **`additionalProperty`** — encode specs (dimensions, material, capacity,
  compatibility) as `PropertyValue`. This is what lets an AI answer "what are the
  dimensions of X" by citing you.

## Category 4 — Trust & Conversion (20)

These signals don't rank the page, they convert the visitor the ranking earned,
and several double as trust signals search engines read.

- **Reviews** — presence + visibility near the top. A PDP with zero reviews on a
  hero product is a conversion + rich-result gap (High).
- **Shipping & returns near the buy box** — a top cart-abandonment driver is
  hidden shipping cost/time. Visible or one-click-away scores full.
- **Images** — ≥4 covering angles, in-use, and scale; zoomable. A single stock
  image caps this at 1/3.
- **Specs table** — buyers of anything technical scan the table before the prose.
  Its absence also drops Cat 5 (nothing structured for AI to extract).

## Category 5 — GEO / AI-Citation Readiness (15)

AI engines cite PDPs for comparative and "best for" queries. Optimize for
extractability.

- **Q&A / FAQ** — 3-5 real buyer questions answered in 1-3 sentences each, with
  `FAQPage` schema. This is the single most-cited surface across ChatGPT and
  Perplexity.
- **Comparison content** — a short "how it compares" (to alternatives or to the
  next variant up) gives AI a citable passage for "X vs Y".
- **"Best for" framing** — one line stating the ideal user/use maps directly to
  long-tail "best X for Y" prompts.

---

## Tier Adjustments

Tiers don't change the max points; they change which failures are Critical vs
Medium and where partial credit applies.

- **hero** — schema completeness (Cat 3) and reviews (Cat 4.1) become Critical on
  failure. Highest expectations; partial credit misleads.
- **variant-parent** — variant canonical (Cat 2) and variant UX (Cat 4.8)
  weighted up; a self-canonicalizing variant URL is Critical here.
- **technical** — specs table (Cat 4.5) + `additionalProperty` (Cat 3.6) +
  comparison (Cat 5.2) weighted up. Copy uniqueness bar is high (spec sheets are
  easy to duplicate).
- **consumable** — relax the unique-copy bar (Cat 1.3 partial credit ok); weight
  price, availability, and reviews. Bundles/subscriptions get conversion credit.
- **new** (<30d) — `Product` schema missing is Critical; freshness weighted.
- **standard** — balanced.

## Gate Details

| Gate | Trigger | Why it's Critical |
|------|---------|-------------------|
| G1 | No `Product` JSON-LD, page indexable | No Shopping eligibility, no rich result, no AI-citation surface |
| G2 🛑 | Schema `price` ≠ visible price | Merchant Center disapproval; feed goes dark |
| G3 🛑 | Schema `availability` ≠ real stock | Disapproval + bad UX (shows buyable when OOS) |
| G4 🛑 | Missing `gtin`/`mpn`, known manufacturer | Shopping feed rejection for that item |
| G5 | 0 clicks, >500 impressions (90d) | Snippet drag: ranking exists, nobody clicks → rewrite title/meta |
| G6 | Description duplicated across >5 products | Thin/duplicate content; cannibalizes + gets discounted |
| G7 | `alt` missing on >50% of images | Image-search + accessibility loss |

🛑 = also a Merchant-Center feed risk; surface prominently for stores running
Google Shopping.

## Scoring Math

- Each check earns whole or half points up to its max.
- Category score = sum of its checks.
- Composite = sum of the 5 categories (0–100).
- `--strict`: N/A checks earn 0 (not partial), so a thin PDP scores its true low.
- A GATE never subtracts points directly; it forces a Critical recommendation and
  a top-of-report flag. A page can score 80 and still carry a 🛑 feed-risk gate —
  fix the gate first regardless of score.
