# Collection Rubric — Full Per-Category Detail

Reference for the 100-point scoring system in `SKILL.md`. Each category below
expands on the summary table with decision rules, examples, and anti-patterns.
Examples below use a generic multi-brand Shopify store; adapt category names,
brands, and price tiers to your own catalog.

---

## Tier Adjustments

Before scoring, the auto-detected tier shifts per-check emphasis. The 100-point
budget does NOT change; only the bar-to-pass shifts:

| Check sensitive to tier | hub | brand | sub | tool | new |
|---|---|---|---|---|---|
| Above-grid copy length floor | 80w | 60w | 40w | 40w | 60w |
| Below-grid copy required? | YES | YES | no | no | YES |
| Hero image GATE? | YES | YES | no | no | YES |
| Schema CollectionPage GATE? | YES | YES | no | no | YES |
| Filter sidebar ≥3 facets required? | YES | YES | no | no | no |
| Curation price-tier strictness | normal | normal | normal | **strict ($100 floor)** | normal |

---

## Category 1 — Collection Copy Quality (20 points)

### 1.1 Above-grid intro copy (4 pts)

**Pass criteria**: 40–120 words placed BEFORE the product grid. Must:
- State who the collection is for (DIY/hobbyist, professional buyer, bulk/B2B buyer)
- Name 2–3 differentiators (price tier, brand exclusivity, application use-case)
- End on a buying-decision micro-cue ("Pick the starter set if you're new; pick the
  refill if you already own the base")

**Anti-patterns** (auto-deduct):
- "Welcome to our X collection. Shop our X today." (boilerplate)
- Copy-paste across multiple collections with only the noun swapped
- Pure keyword stuffing ("Buy Brand A widget widget Brand A widget")

### 1.2 Below-grid SEO copy (4 pts, hub/brand only)

**Pass criteria**: ≥150 words AFTER the product grid; covers 2+ supporting topics:
- How-to-use / how-to-pick
- "Which one is for me" (variant decision tree)
- FAQ block (3–5 questions)
- Compatibility notes (accessory pairings, spec requirements, etc.)

Optional but high-lift: a curated "Editor's Pick" mini-list with 3 SKU links
back into the collection.

### 1.3 Voice match BRAND.md (3 pts)

If `sites/[site]/BRAND.md` exists, sample 3–5 sentences from the body and check:
- Tone (B2B/bulk / pro vs DIY-friendly per site BRAND)
- Forbidden taboo phrases listed in BRAND.md
- First-person POV (if site uses "we")
- No AI-flavored hedging ("delve into", "in conclusion", "it's important to note")

If BRAND.md missing → neutral 2/3 score + advisory "create BRAND.md".

### 1.4 Buying-decision clarity (3 pts)

The copy must answer at least 2 of:
- Who is this for?
- What problem does it solve?
- How does it differ from the sibling collection?
- What's the entry-tier vs flagship pick?

### 1.5 Em-dash + AI-trigger compliance (3 pts)

Hard cap: em-dash ratio ≤ 0.3 per 100 words. Run a quick count:
- Body word count W
- Em-dash count E
- Ratio = E / W × 100
- If ratio > 0.3 → deduct 2 pts and recommend running an em-dash reduction
  pass (`scripts/reduce_emdash.py` or equivalent)

AI-trigger phrases (maintain your own list of banned boilerplate phrases):
- "delve into" / "navigate the landscape" / "in today's fast-paced"
- ≥3 instances → deduct 1 pt

### 1.6 Boilerplate similarity (3 pts)

For sites with ≥10 collections, sample 5 other collection body HTML and run a
token-Jaccard. If average similarity > 0.7 → boilerplate-flag, deduct 2 pts.

---

## Category 2 — SEO + Commercial Intent Match (25 points)

### 2.1 `<title>` format + length (4 pts)

Format priority order (sites can override in `sites/[site]/overrides.md`):
1. `{Brand} {Category} | {Site Brand}` — for brand collections
2. `{Category} | {Site Brand} – {USP}` — for hub collections
3. `{Collection Name} – {Site Brand}` — for sub/new

Length: 30–60 chars (Google SERP truncation 580px).
Primary keyword in first 30 chars. Brand name optional in title if domain is
brand-recognized (your-store.com → site-brand abbreviation optional).

### 2.2 Meta description (3 pts)

120–160 chars. Must include:
- Primary commercial keyword
- A specific number or detail (product count, brand count, free-ship threshold)
- Soft CTA ("Shop now" / "See all options" / "Bulk pricing for everyone")

### 2.3 H1 match user intent (3 pts)

H1 should equal the collection title OR a search-optimized rewrite.
- ✅ "Brand A Variants" → H1 = "Brand A Variants" (`<N>` products)
- ❌ "Brand B Premium Line **Colletion**" → typo in title cascades to H1

### 2.4 URL structure (2 pts)

`/collections/{kebab-handle}`. Penalize:
- Typos in handle (auto-Critical via GATES)
- >40-char handle
- Stray characters (`_`, capital letters)

### 2.5 Canonical (2 pts)

Self-canonical pointing to the clean collection URL. Common Shopify mis-config:
filter/sort query params not stripped → duplicate URLs in index. Check via
WebFetch the response with `?sort_by=...` to see canonical behavior.

### 2.6 Hreflang (2 pts)

If site is single-locale, this is N/A and full 2 pts.
If multi-locale, `<link rel="alternate" hreflang="...">` block must be correct.

### 2.7 GSC CTR signal (3 pts)

Pull 90d GSC data. Bands:

| Avg position | Expected CTR | Action if below |
|---|---|---|
| 1–3 | ≥ 10% | title/meta rewrite |
| 4–10 | ≥ 2.5% | title/meta tune + schema add for rich snippet |
| 11–20 | n/a | not a CTR problem |

If position 1–10 AND CTR < 1.5% → deduct 3 pts and add Critical fix.

### 2.8 GSC position vs intent (3 pts)

Pull top 10 queries. Score:
- 3 pts: top queries match collection intent (brand / category keywords)
- 2 pts: mixed — some long-tail PDP queries leaking up
- 1 pt: top queries are blog-intent ("how to apply X") — collection is ranking
  by accident; signals copy mismatch
- 0 pts: no commercial queries; collection should be merged or noindex'd

### 2.9 Internal links INTO collection (3 pts)

Count internal links pointing to the collection URL from elsewhere on the site.
Source signals:
- Blog post citations
- Cross-collection "Related categories" blocks
- Homepage featured-collection tiles
- PDP "Part of collection: X" links

Anchor-quality rule: anchors should be ≥3 unique variants and 2–5 words long.
No "click here" / "see more" anchors.

| Internal link count | Score |
|---|---|
| ≥ 10 with ≥3 unique anchors | 3 |
| 4–9 | 2 |
| 1–3 | 1 |
| 0 | 0 (Critical for hub/brand) |

---

## Category 3 — Product Curation Quality (20 points, warning-only)

See `references/curation-warning-rules.md` for the full warning ledger.
The 20 points are earned by *running* the check successfully (15/20 if skipped
with `--no-curation-check`), with warnings surfaced in a separate report
section. Field lesson: never fail composite for transient OOS or draft
products — those are operational noise, not content-quality failures.

---

## Category 4 — Technical + Schema (15 points)

### 4.1 `CollectionPage` JSON-LD (3 pts)

Template in `references/schema-collectionpage.md`. Must include:
```json
{
  "@type": "CollectionPage",
  "name": "Brand A Variants",
  "description": "...",
  "url": "https://your-store.com/collections/brand-a-variants",
  "mainEntity": { "@type": "ItemList", ... }
}
```

### 4.2 `ItemList` JSON-LD (3 pts)

Array of products with position + name + url + image:
```json
{
  "@type": "ItemList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "url": "...", "name": "...", "image": "..." }
  ]
}
```

Either inline products (preferred) OR Shopify auto-generated `BreadcrumbList`
with collection products as `ListItem` entries.

### 4.3 `BreadcrumbList` (2 pts)

`Home > Collections > {Collection Name}`. Must match visible breadcrumb on
page.

### 4.4 `Product` schema per card (2 pts)

Sample 3 product cards on the collection. Their PDPs (linked URLs) must expose
Product schema with at minimum `name`, `image`, `offers.price`,
`offers.priceCurrency`, `offers.availability`. Bonus if `aggregateRating`
present (lift in SERP CTR).

### 4.5 Pagination rel + canonical (2 pts)

For paginated collections:
- `rel="next"` / `rel="prev"` on page 2+
- OR canonical → page 1 (consolidate ranking signal)
- OR view-all canonical → ?view=all (Shopify supports this)

### 4.6 Mobile LCP (2 pts)

If PageSpeed Insights or CrUX field data accessible, LCP < 3.5s mobile.
Else neutral 1/2.

### 4.7 No mixed content / console errors (1 pt)

Optional. Skipped without browser automation.

---

## Category 5 — UX & Conversion Signals (20 points)

### 5.1 Hero image (3 pts)

**Hard rule**: hub + brand tier collections MUST have a non-null `image`.
The collection-card image surfaces in Shopify's own search, image search, and
3rd-party SEO tools' previews. `image=null` is a major lift gap.

For sub/tool/new tier: hero image is nice-to-have, 2/3 score if missing.

### 5.2 Price visible on cards (3 pts)

Compare-at + sale + savings badge if applicable. Bulk/wholesale-price badge if the
site runs a bulk or wholesale pricing model.

### 5.3 Stock indicator (2 pts)

Visible stock badge on cards (in-stock / low-stock / OOS). Cards for OOS should
be visually distinguished (greyscale, "Notify me" CTA).

### 5.4 Sort dropdown (2 pts)

Options should include: Best Selling, Price Low–High, Price High–Low, Newest,
A–Z. Shopify defaults are usually fine; flag if sort dropdown missing entirely.

### 5.5 Filter sidebar (3 pts)

For hub/brand: ≥3 facets (color, size, brand, type, price range).
For sub/tool/new: nice-to-have, 2/3 score if missing.

Examples:
- `{example-hub-collection}` (hub, `<N>` products) → MUST have Brand + Color/Option + Size filters
- `{example-sub-collection}` (sub, `<N>` products) → 1 facet ok

### 5.6 Social proof (2 pts)

Star rating + review count visible on ≥30% of product cards.

### 5.7 Mobile grid (2 pts)

2-column grid mobile, image+title+price visible without scroll, card height
uniform. Use `--mobile` flag with WebFetch (if browser available) or inspect
CSS media queries.

### 5.8 Sticky add-to-cart / quick-buy (2 pts)

Either hover-state "Quick add" button on desktop, OR mobile sticky cart pill.

### 5.9 Above-the-fold density (1 pt)

≥6 product cards visible above the fold on a 1440×900 desktop viewport.

---

## Cannibal Verdict Rules

When `--cannibal-pair` is set, after individual scoring compute these signals:

| Signal | Compute |
|---|---|
| Title token Jaccard | `tokens(title1) ∩ tokens(title2) / tokens(title1) ∪ tokens(title2)` |
| Handle token Jaccard | Same on handles (split on `-`) |
| GSC query Jaccard | Top 50 queries each, set Jaccard |
| Product GID overlap | `len(products1 ∩ products2) / min(len(products1), len(products2))` |

Verdict matrix:

| Title J | Query J | Product overlap | Verdict |
|---|---|---|---|
| ≥ 0.7 | ≥ 0.6 | ≥ 0.5 | **MERGE** — redirect 301 V1→V2 (or V2→V1, pick higher-traffic) |
| ≥ 0.5 | ≥ 0.4 | < 0.5 | **DIFFERENTIATE** — rewrite copy + title to split intent |
| < 0.5 | < 0.4 | any | **PARALLEL OK** — they serve different sub-intents |

Always include the GSC click counts of both pages — the merge direction goes
toward the higher-click page.

Example: `brand-a-premium-line-colletion` (V1, `<N>` products) vs
`brand-a-premium-line-2-collection` (V2 = "Version 2", `<N>` products). If V1
has more clicks/90d than V2 — merge V2 → V1. But ALSO fix the V1 handle typo
(`colletion` → `collection`) with a 301 redirect chain V1.old → V1.new.

---

## Re-audit cycle

After fixes are applied, re-run the skill to produce
`collection-quality-score-v2.md`. The new report should:
- Show before/after composite score
- List which Critical/High fixes were verified resolved
- Surface any newly-introduced issues (regression check)
