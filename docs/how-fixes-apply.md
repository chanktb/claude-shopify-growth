# How fixes get applied: per-product data vs one-time theme

An audit tells you *what* is wrong. This doc is the mental model for *how* the
fix actually lands, because two very different mechanisms are involved — and
confusing them is the #1 reason store owners either over-work (rewriting the
same thing N times) or under-fix (never touching the theme).

## The one rule

> **Content is per-product DATA — you rewrite and push it per product.
> Structure/schema/render is the THEME — you fix it once and it applies to the
> whole catalog.**

## The map

| Problem the audit found | Where it actually lives | How you fix it | Scope |
|---|---|---|---|
| Boilerplate / thin description, weak title, meta, FAQ, spec values, image `alt` | **Data** on the product/collection object | Rewrite + push via the Admin API, per item | Per item (N times) |
| Missing / wrong `Product` · `Offer` · `AggregateRating` schema | **Theme** (a Liquid snippet renders it) | Fix the snippet **once** | Whole catalog, 1 change |
| Deep content saved but not rendering (custom template) | **Theme** (the custom template lacks the section) | Add the section to that template **once** | Per template, 1 change |
| Missing `gtin`/`mpn`, missing spec metafield values | **Data** (variant barcode / metafields) | Fill per item (or feed) | Per item (N times) |
| Title > 60 chars from a brand suffix | **Both**: a per-item metafield flag + a one-time `theme.liquid` patch | Set the metafield per item; patch the theme once | Mixed |

## Path 1 — content (per-product data)

The product/collection description, SEO title/description, FAQ, spec values, and
image alt text are **fields on the object**. Fixing them is a data write:

- `product-content-deep` / `collection-content-deep` write the new copy.
- `product-optimize` / `collection-mega-hub-optimize` push it (`descriptionHtml`,
  `seo`, metafields, `altText`) via the Admin API.
- Reversible: you can revert a description.
- **Scales by item count.** 500 weak descriptions = 500 rewrites. That's why the
  `*-audit-pipeline` skills rank by *traffic × gap* — fix the high-traffic weak
  pages first, not alphabetically.
- Near-identical items (e.g. the same product in different sizes) can share most
  of the copy; only the specs and the comparison must be unique per item.

## Path 2 — schema & render (one-time theme)

Structured data is **not per-product data you push** — the theme *renders* it
from a Liquid snippet (e.g. `snippets/product-structured-data.liquid`). So:

- If the theme emits no `Product` schema, you **fix the theme once** and every
  product gets it automatically. You never push schema per product.
- Bind the dynamic fields (`price`, `availability`, rating) to the live product /
  variant / reviews object so they self-update — never freeze a value. (See
  `skills/product-analyze/references/product-schema.md` §0.)
- The same applies to **rendering**: if a custom template saved deep content but
  doesn't display it, the fix is to add the section to that template — a theme
  change, not a content rewrite. The content already exists.

### Theme changes are production changes — handle them carefully

- Get the store owner's explicit approval first.
- Push to a **duplicate theme**, preview it, then let the owner publish. The
  Shopify MCP safelist commonly blocks writes to the live theme anyway.
- Log it (what / how / verify / revert). A theme edit is high-leverage *and*
  high-blast-radius: one snippet touches every page of that type.

## The nuance: schema often needs BOTH

Adding the theme snippet gives you the `Product`/`Offer` **wrapper**. But some
fields inside it come from **per-product data**: `gtin` (the variant barcode),
`mpn`, and spec `additionalProperty` values. So a complete schema fix can be:

1. **Theme (once)** — render the `Product` + `Offer` + `BreadcrumbList` bundle,
   bound to live objects.
2. **Data (per item)** — make sure the barcode/identifiers and spec metafields
   are actually populated (or set `identifier_exists: no` for private-label items
   that legitimately have no GTIN).

## Don't confuse the Google Shopping feed with on-page schema

A common trap: "I run Google Shopping, so my product structured data is covered."
It isn't. They are two different channels:

- **Merchant Center feed** — product data (price, availability, GTIN, category)
  sent to Google via the Shopping/Google channel. Powers **Shopping ads + free
  listings**. It does **not** put any JSON-LD on your web pages.
- **On-page schema** (JSON-LD in the page HTML) — powers **organic rich results**
  (the star/price snippet in blue-link search) and gives **AI engines** a
  structured surface to cite (AI Overviews, ChatGPT, Perplexity).

A store can have a healthy feed (Shopping ads running fine) and still emit **zero
`Product` schema on its product pages** — losing every organic rich result and
AI-citation opportunity. The feed and the theme are fixed in different places.
`product-analyze` checks the on-page schema specifically (via `curl` for the
JSON-LD — see the Step 1b note on why WebFetch is unreliable for this).

## TL;DR decision flow

1. Audit finds an issue → ask "is this **data** or **theme**?"
2. **Data** (copy, meta, specs, alt, identifiers) → rewrite/fill + push per item;
   prioritize by traffic × gap.
3. **Theme** (schema wrapper, a template not rendering) → fix once on a duplicate
   theme, get approval, publish. Highest leverage; most caution.
4. Schema not showing? Confirm with `curl … | grep '"@type"'`, not WebFetch.
