# Curation Warning Rules — Product List Health Check

Reference for Category 3 (Product Curation Quality, 20 points) in
`SKILL.md`. By design, these checks emit **warnings only** — they never
reduce the composite score. The points are earned by running the check
successfully and surfacing the warnings in the report.

The 20-point allocation breaks down as:

| Sub-check | Max pts | How earned |
|---|---|---|
| Active status check ran successfully | 4 | Shopify connector returned product list; pass/fail count emitted |
| In-stock check ran successfully | 4 | Inventory level fetched per SKU; OOS list emitted |
| Price tier check ran successfully | 4 | Price tier matched against category floor table |
| Size health check ran successfully | 3 | Product count compared to tier expectation |
| Sort order check ran successfully | 3 | sortOrder field compared to intent expectation |
| Cross-brand contamination check ran successfully | 2 | Brand tag distribution computed |

Skip the curation category with `--no-curation-check` → 15/20 neutral.

---

## 1. Product status (active)

Pull product list via Shopify connector. For each:
- `status = ACTIVE` → green
- `status = DRAFT` → 🟡 warning (should not appear on storefront — likely a
  Shopify "publish to channel" misconfig)
- `status = ARCHIVED` → 🟠 warning (will appear cached but lead to 404 PDPs)

Report format:
```
Curation Watchlist — Active Status
  - <N> / <N> ACTIVE (<X>%)
  - 1 DRAFT: "Brand A Iceland - Polar Eskimo" (gid://shopify/Product/...)
  - 1 ARCHIVED: "Brand B DC Fall Sample" (gid://shopify/Product/...)
```

## 2. Inventory (in-stock)

For each product, sum inventory across locations.
- Total inventory > 0 → in stock
- Total = 0 AND last purchase < 60 days ago → 🟡 transient OOS (warn but ok)
- Total = 0 AND last purchase ≥ 60 days ago → 🟠 cold OOS (warn — discontinue
  or remove from collection)

Skip last-purchase check if order data not accessible; fall back to flat
in-stock / OOS report.

## 3. Category-appropriate price tier

Each product category should have a defined price floor/ceiling for your
store. Out-of-tier products in a collection break commercial intent. Define
your own table; example shape for a nail-supply store:

| Category | Floor | Ceiling | Notes |
|---|---|---|---|
| Tools / equipment / drills | `$<floor>` | open | High-value durable goods get a high floor |
| Core consumable (e.g. polish/color) | `$<floor>` | `$<ceiling>` | Premium brands can exceed |
| Bulk consumable (e.g. powder) | `$<floor>` | `$<ceiling>` | Premium lines priced at the top |
| Brushes / applicators | `$<floor>` | `$<ceiling>` | Pro sets at top |
| Small accessory (file, buffer, tip) | `$<floor>` | `$<ceiling>` | Bulk-pack at top |
| Specialty consumable | `$<floor>` | `$<ceiling>` | Per-unit varies |
| Gift sets / bundles | `$<floor>` | `$<ceiling>` | Wide range — usually exempt |
| Wholesale lots / kits | `$<floor>` | open | Exempt — bulk pricing |

Detection: pull first 50 product prices in the collection. Compare to category
floor (auto-detect category from collection title + tags).

- ≥ 90% in tier → ✅
- 70–89% in tier → 🟡 warning + list outliers
- < 70% in tier → 🟠 warning + suggest splitting collection

Example: a "tools" collection (`<N>` products, includes lamps + drills) has an
expected high price floor. If half the products fall below that floor, that's
a curation contamination — the collection is mixing cheap accessories with
higher-value tools.

## 4. Collection size health

| Tier | Min products | Max products | Notes |
|---|---|---|---|
| hub | 100 | ∞ | Sub-1000 is borderline hub |
| brand | 30 | 500 | Sweet spot 100–300 |
| sub | 10 | 100 | Seasonal / collection drop |
| tool | 20 | 80 | Tool sub-category |
| new | 5 | 100 | New launch baseline |

Outside range → 🟡 warning + recommendation:
- Too few → "promote to homepage if seasonal; OR merge with parent"
- Too many → "split by sub-attribute (color family / size / use-case)"

## 5. Sort order match intent

Expected sort by tier:
- **hub**: BEST_SELLING (lets traffic flow to winners)
- **brand**: MANUAL with curated top 12 (campaign control)
- **sub**: MANUAL or BEST_SELLING (small enough either works)
- **tool**: BEST_SELLING or PRICE (commercial intent strong)
- **new**: CREATED descending (new first)

If sortOrder mismatches expected → 🟡 warning + 1-click fix instruction
(Shopify admin URL deep-link to collection settings).

## 6. Cross-brand contamination

For brand collections (title starts with a brand name, e.g. "Brand A"),
inspect product vendor / brand tag:

- ≥ 95% products = same brand → ✅
- 80–94% → 🟡 minor leakage (likely tag misconfig on a few products)
- < 80% → 🟠 Critical (the collection is not truly brand-pure)
- < 60% → 🔴 GATE (force-flag in main report)

Exception: if collection title explicitly says "Brand A, Brand B, Brand C
Gel & Lacquer" (multi-brand bundle) — skip this check.

## How warnings are presented

In the main report, under a `## Curation Watchlist` section (after the Critical
/ High / Medium / Low fixes, before the GSC + Shopify snapshots):

```
## Curation Watchlist (warnings — does NOT affect composite score)

### Active status — <X>% pass
- 1 DRAFT product surfacing: "Brand A Iceland - Polar Eskimo"
- Fix: change status to ACTIVE in Shopify admin, OR remove from collection

### Price tier — <X>% in tier (category expected `$<floor>`–`$<ceiling>`)
- <N> products above ceiling:
  - "Brand B Builder Gel Mega Kit" — `$<price>` (kit, likely tier mismatch)
  - "Brand A Pro Studio Set" — `$<price>` (set, likely tier mismatch)
  - ...
- Suggestion: move kits/sets to a separate "Kits & Sets" collection

### Inventory — <X>% in stock
- <N> OOS, of which <N> cold (>60d no purchase)
- Cold OOS list: ...
```

This separation makes the report actionable without polluting the composite
score with transient signals.
