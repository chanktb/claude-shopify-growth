# Schema.org Templates for Shopify Collection Pages

Reference for Category 4 (Technical + Schema, 15 points) in `SKILL.md`. JSON-LD
templates Shopify Liquid sites can drop into a layout file, and validation
notes for what Google currently understands.

---

## Why this matters

A Shopify collection page without proper JSON-LD loses:
- Rich-result eligibility (sitelinks, image carousel, product grid in SERP)
- AI citation surface (ChatGPT / Perplexity prefer pages with `ItemList`)
- Faceted-navigation safety (clear `mainEntity` declaration tells crawlers
  what the canonical page is)

Field lesson: a full-site blog audit once found that essentially all articles
had ZERO JSON-LD. Collection audits will likely show the same gap — site-wide
schema missing. Fix once, ship across all collections via Liquid template.

---

## Template 1 — `CollectionPage` (top-level)

Place inside `<head>`, ONE per collection page:

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": "{{ collection.title | escape }}",
  "description": "{{ collection.description | strip_html | strip_newlines | truncate: 250 | escape }}",
  "url": "{{ shop.url }}{{ collection.url }}",
  "image": "{{ collection.image | img_url: '1200x' }}",
  "isPartOf": {
    "@type": "WebSite",
    "name": "{{ shop.name }}",
    "url": "{{ shop.url }}"
  },
  "mainEntity": {
    "@type": "ItemList",
    "numberOfItems": {{ collection.products_count }},
    "itemListElement": [
      {% for product in collection.products limit: 30 %}
      {
        "@type": "ListItem",
        "position": {{ forloop.index }},
        "url": "{{ shop.url }}{{ product.url }}",
        "name": "{{ product.title | escape }}",
        "image": "{{ product.featured_image | img_url: '600x' }}"
      }{% unless forloop.last %},{% endunless %}
      {% endfor %}
    ]
  }
}
</script>
```

**Notes**:
- Limit `itemListElement` to 30 entries (Google's de-facto cap; more = silently
  truncated)
- If `collection.image` is null, omit the `image` field entirely (don't emit
  `"image": ""` — invalidates schema)
- `truncate: 250` keeps the description Google-friendly; full HTML body should
  go into visible page content, not the schema

---

## Template 2 — `BreadcrumbList`

Sits alongside the CollectionPage script (separate `<script>` block):

```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    {
      "@type": "ListItem",
      "position": 1,
      "name": "Home",
      "item": "{{ shop.url }}"
    },
    {
      "@type": "ListItem",
      "position": 2,
      "name": "Collections",
      "item": "{{ shop.url }}/collections"
    },
    {
      "@type": "ListItem",
      "position": 3,
      "name": "{{ collection.title | escape }}",
      "item": "{{ shop.url }}{{ collection.url }}"
    }
  ]
}
</script>
```

Must match the visible breadcrumb on the page. Mismatch → Google flags as
spam-pattern.

---

## Template 3 — `Product` schema (per PDP — for reference)

Collection cards link to PDPs. PDP schema is rendered there, not on the
collection. Audit Category 4.4 samples 3 PDPs and verifies they expose:

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{{ product.title }}",
  "image": [{{ product.images | join: '","' | prepend: '"' | append: '"' }}],
  "description": "{{ product.description | strip_html | truncate: 500 }}",
  "sku": "{{ product.selected_or_first_available_variant.sku }}",
  "brand": {
    "@type": "Brand",
    "name": "{{ product.vendor }}"
  },
  "offers": {
    "@type": "Offer",
    "url": "{{ shop.url }}{{ product.url }}",
    "priceCurrency": "{{ shop.currency }}",
    "price": "{{ product.selected_or_first_available_variant.price | money_without_currency }}",
    "availability": "{% if product.available %}https://schema.org/InStock{% else %}https://schema.org/OutOfStock{% endif %}"
  }
}
```

Bonus: add `aggregateRating` if the site uses a review app (Loox, Judge.me,
Stamped) that exposes structured data:

```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "{{ product.metafields.reviews.rating }}",
  "reviewCount": "{{ product.metafields.reviews.count }}"
}
```

---

## Validation

After deploying templates, validate with:
1. Google Rich Results Test: https://search.google.com/test/rich-results
2. Schema.org validator: https://validator.schema.org/
3. Shopify Theme Inspector (browser extension) — checks Liquid rendering

Common failures to watch for:
- Empty `image` field (Liquid renders `""` when `collection.image` null)
- HTML entities in description (`&amp;` should decode before injection)
- Missing `@context` (kills the entire script block)
- Duplicate `CollectionPage` blocks (one from theme, one from app) — pick one

---

## Where to drop these in a Shopify theme

| Theme location | What goes there |
|---|---|
| `templates/collection.json` → `main-collection` section | CollectionPage + BreadcrumbList scripts |
| `sections/main-collection-product-grid.liquid` | (Dawn theme) — drop scripts in `{% schema %}` neighbor `<script>` |
| `snippets/structured-data.liquid` | If theme already has a structured-data snippet, append to it (don't duplicate) |
| `layout/theme.liquid` `<head>` | Last resort fallback — but page-specific render fails here |

For a Dawn-based theme specifically: drop in
`sections/main-collection-product-grid.liquid` near the top of the section.

---

## Audit checklist (for the SKILL Step 4)

When the analyzer fetches the page — use `curl`, not a markdown fetch like
WebFetch (which drops `<script type="application/ld+json">`; see the
`collection-analyze` SKILL Step 1b warning) — look for:

| Schema block | Required for tier | Audit check |
|---|---|---|
| `CollectionPage` | hub, brand, new | `@type` field present and valid |
| `ItemList` | hub, brand | `numberOfItems` matches visible product count ± 10% |
| `BreadcrumbList` | all | Matches visible breadcrumb |
| `Product` (linked PDPs) | all | Sample 3 PDPs from collection, check Product schema there |
| `aggregateRating` on Products | bonus (+1 in 4.4 if present) | Sample shows real ratings (not placeholder) |
