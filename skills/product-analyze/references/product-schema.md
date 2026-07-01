# Product Schema: JSON-LD templates for PDPs

The `Product` schema bundle is the highest-leverage technical asset on a PDP: it
feeds Google Shopping / rich results (star snippet, price, availability) **and**
gives AI engines structured facts to cite. Emit it once per product page.

> **The golden rule: schema must mirror the visible page byte-for-byte.** The #1
> Merchant-Center disapproval is `price` or `availability` in schema disagreeing
> with the buy box. Never hard-code — bind to the theme's product/variant object.

---

## 1. Core `Product` + `Offer`

```json
{
  "@context": "https://schema.org",
  "@type": "Product",
  "name": "{Product name}",
  "image": ["{primary image url}", "{image 2}", "{image 3}"],
  "description": "{plain-text description, matches the page}",
  "sku": "{sku}",
  "mpn": "{mpn}",
  "gtin13": "{barcode}",
  "brand": { "@type": "Brand", "name": "{Brand}" },
  "offers": {
    "@type": "Offer",
    "url": "{canonical product url}",
    "priceCurrency": "{USD}",
    "price": "{visible price, no currency symbol}",
    "priceValidUntil": "{YYYY-12-31}",
    "availability": "https://schema.org/InStock",
    "itemCondition": "https://schema.org/NewCondition"
  }
}
```

`availability` values: `InStock`, `OutOfStock`, `BackOrder`, `PreOrder`,
`LimitedAvailability`. Bind to the variant's real inventory state.

### Variant products — `AggregateOffer`

When a product has variants at different prices, use `AggregateOffer` so the
snippet shows a range instead of one wrong price:

```json
"offers": {
  "@type": "AggregateOffer",
  "priceCurrency": "USD",
  "lowPrice": "{min variant price}",
  "highPrice": "{max variant price}",
  "offerCount": "{variant count}",
  "availability": "https://schema.org/InStock"
}
```

---

## 2. `AggregateRating` + `Review` (only when real reviews exist)

```json
"aggregateRating": {
  "@type": "AggregateRating",
  "ratingValue": "{4.6}",
  "reviewCount": "{128}",
  "bestRating": "5"
},
"review": [
  {
    "@type": "Review",
    "author": { "@type": "Person", "name": "{Reviewer}" },
    "datePublished": "{YYYY-MM-DD}",
    "reviewRating": { "@type": "Rating", "ratingValue": "{5}", "bestRating": "5" },
    "reviewBody": "{review text}"
  }
]
```

Never fabricate or hard-code ratings — that is a policy violation and a
disapproval risk. If your reviews app already injects rating schema, do NOT
double-emit; verify there's exactly one `AggregateRating` on the page.

---

## 3. `additionalProperty` — machine-readable specs

Encode the spec table as structured properties so rich results and AI engines can
extract them. This is what lets an assistant answer "what are the dimensions of
X" by citing your page.

```json
"additionalProperty": [
  { "@type": "PropertyValue", "name": "Material", "value": "{value}" },
  { "@type": "PropertyValue", "name": "Dimensions", "value": "{L x W x H}" },
  { "@type": "PropertyValue", "name": "Weight", "value": "{value}" },
  { "@type": "PropertyValue", "name": "Compatibility", "value": "{value}" }
]
```

Keep the visible spec table and these properties in sync (same names + values).

---

## 4. `BreadcrumbList`

Matches the visible breadcrumb: home → collection → product.

```json
{
  "@context": "https://schema.org",
  "@type": "BreadcrumbList",
  "itemListElement": [
    { "@type": "ListItem", "position": 1, "name": "Home", "item": "{home url}" },
    { "@type": "ListItem", "position": 2, "name": "{Collection}", "item": "{collection url}" },
    { "@type": "ListItem", "position": 3, "name": "{Product}", "item": "{product url}" }
  ]
}
```

---

## 5. `FAQPage` (for the PDP Q&A block — Cat 5)

Emit from a flat `[{q, a}]` data source, the same discipline as the collection
module. The theme builds the wrapper; you provide the flat data.

```json
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    { "@type": "Question", "name": "{q}",
      "acceptedAnswer": { "@type": "Answer", "text": "{a}" } }
  ]
}
```

---

## Validation checklist

- [ ] Exactly one `Product` block per PDP (no duplicates from apps + theme)
- [ ] `price` + `availability` match the visible buy box for the selected variant
- [ ] `gtin`/`mpn` present for known-manufacturer products (or `identifier_exists: no`)
- [ ] `AggregateRating` only when real reviews exist; not double-emitted
- [ ] `image` URLs are absolute, ≥ the minimum dimensions, and load (200)
- [ ] Passes Google's Rich Results Test + Merchant Center preview with no errors
- [ ] `additionalProperty` names/values match the visible spec table
