# Theme Patch: rendering the metafields + brand-suffix opt-out

This workflow assumes the theme renders four collection metafields and one
boolean. The patches below were developed against a Stiletto-style theme but the
concepts port to any Shopify 2.0 theme (Dawn included) — adjust selector/section
names to your theme.

You only need to do this ONCE per theme. After that, every optimized collection
just sets its metafields and (optionally) a per-collection template.

> **Push to a DUPLICATE theme first.** `themeFilesUpsert` on the live/main theme
> is frequently blocked by the MCP safelist, and you should preview theme edits
> before publishing anyway. Duplicate → edit → preview → publish manually.

---

## 1. Brand-suffix opt-out (Gate 2: title ≤60ch)

Many themes append ` – {shop.name}` to the `<title>` unless the page title
already contains the shop name. That suffix eats keyword budget. Honor a
per-collection metafield `custom.suppress_brand_suffix` so specific collections
can claim the full 55-60ch for keywords.

In `layout/theme.liquid`, find the block that builds the page title suffix and
replace it with:

```liquid
{%- assign escaped_page_title = page_title | escape -%}
{%- assign suppress_brand = false -%}
{%- if request.page_type == 'collection' and collection.metafields.custom.suppress_brand_suffix == true -%}
  {%- assign suppress_brand = true -%}
{%- endif -%}
{%- unless escaped_page_title contains shop.name or suppress_brand -%}
  &ndash; {{ shop.name }}
{%- endunless -%}
```

Metafield definition to create (Settings → Custom data → Collections):
- Namespace/key: `custom.suppress_brand_suffix`
- Type: `Boolean`

---

## 2. Deep content section (`sections/collection-content.liquid`)

Renders the `custom.deep_content_html` metafield below the product grid.

```liquid
{%- assign body = collection.metafields.custom.deep_content_html -%}
{%- if body != blank -%}
  <div class="collection-content rte page-width">
    {{ body }}
  </div>
{%- endif -%}

{% schema %}
{ "name": "Collection content", "settings": [] }
{% endschema %}
```

Metafield: `custom.deep_content_html`, type `Multi-line text` (stores HTML).

---

## 3. FAQ accordion (`sections/collection-faq.liquid`)

Consumes the FLAT `custom.faq_jsonld` metafield: a JSON list of `{q, a}`
objects. **Never** a schema.org `FAQPage` wrapper — the loop below reads `q`/`a`
keys directly and a wrapper would render empty boxes.

```liquid
{%- assign faq = collection.metafields.custom.faq_jsonld.value -%}
{%- if faq != blank and faq.size > 0 -%}
  <section class="collection-faq page-width">
    <h2>Frequently asked questions</h2>
    {%- for item in faq -%}
      <details class="collection-faq__item">
        <summary class="collection-faq__question">
          <span class="collection-faq__question-text">{{ item.q }}</span>
        </summary>
        <div class="collection-faq__answer rte">{{ item.a }}</div>
      </details>
    {%- endfor -%}
  </section>
{%- endif -%}

{% schema %}
{ "name": "Collection FAQ", "settings": [] }
{% endschema %}
```

Metafield: `custom.faq_jsonld`, type `JSON`. Canonical value shape:

```json
[
  {"q": "What brands do you carry?", "a": "We stock ..."},
  {"q": "Is X compatible with Y?", "a": "Yes ..."}
]
```

The `collection-faq__question-text` class is what Gate 15 greps for on the live
page.

---

## 4. Sub-category nav (`sections/sub-category-nav.liquid`, Path B)

Renders the `custom.sub_categories` metafield (a JSON list of `{handle, title}`)
as a chip group. Only mega-hubs / brand-hubs set this metafield.

```liquid
{%- assign subs = collection.metafields.custom.sub_categories.value -%}
{%- if subs != blank and subs.size > 0 -%}
  <nav class="sub-category-nav page-width" aria-label="Sub-collections">
    {%- for s in subs -%}
      <a class="sub-category-nav__link" href="/collections/{{ s.handle }}">{{ s.title }}</a>
    {%- endfor -%}
  </nav>
{%- endif -%}

{% schema %}
{ "name": "Sub-category nav", "settings": [] }
{% endschema %}
```

Metafield: `custom.sub_categories`, type `JSON`. The `sub-category-nav__link`
class is what Gate 17 greps for.

---

## 5. Structured-data snippet (`snippets/collection-structured-data.liquid`)

Emits the 4-schema bundle (CollectionPage + ItemList nested in
`mainEntity` + BreadcrumbList + FAQPage). Include it once in the collection
template's `<head>` path. The theme builds the `FAQPage` wrapper FROM the flat
`custom.faq_jsonld` data — you only ever provide the flat `{q,a}` list.

```liquid
{%- capture ld -%}
{
  "@context": "https://schema.org",
  "@type": "CollectionPage",
  "name": {{ collection.title | json }},
  "url": {{ shop.url | append: collection.url | json }},
  "mainEntity": {
    "@type": "ItemList",
    "numberOfItems": {{ collection.products_count }},
    "itemListElement": [
      {%- for product in collection.products limit: 24 -%}
        {"@type": "ListItem", "position": {{ forloop.index }}, "url": {{ shop.url | append: product.url | json }}}{%- unless forloop.last -%},{%- endunless -%}
      {%- endfor -%}
    ]
  }
}
{%- endcapture -%}
<script type="application/ld+json">{{ ld }}</script>
```

Add BreadcrumbList and (when `custom.faq_jsonld` is present) a FAQPage block in
the same snippet.

---

## Checklist

- [ ] `custom.suppress_brand_suffix` (boolean) + `theme.liquid` patch
- [ ] `custom.deep_content_html` (multi-line text) + `collection-content` section
- [ ] `custom.faq_jsonld` (JSON) + `collection-faq` section
- [ ] `custom.sub_categories` (JSON) + `sub-category-nav` section (Path B only)
- [ ] `collection-structured-data` snippet wired into the collection `<head>`
- [ ] `global.title_tag` / `global.description_tag` honored by the theme's SEO meta
