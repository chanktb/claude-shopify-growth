# Brand Mapping Queries: Shopify Sub-Collection Discovery

Every internal link in a mega-hub MUST be verified against live Shopify
inventory before you write it (Gate 1: URL inventory). This doc has the
GraphQL query patterns for discovering the sub-collections a hub should link
to, plus a template for recording the verified handle map for your own store.

Never write a `/collections/{handle}` link from memory. Query first, link second.

---

## Pattern A: Title-keyword search (multi-brand discovery)

Use when the hub spans multiple brands. Pull all related sub-collections in
one batched query (alias one field per brand, up to ~10 aliases per request).

```graphql
query MultiBrandSubCollections {
  brand1: collections(first: 15, query: "title:*<brand1>*") {
    edges { node { handle title productsCount { count } } }
  }
  brand2: collections(first: 15, query: "title:*<brand2>*") {
    edges { node { handle title productsCount { count } } }
  }
  brand3: collections(first: 15, query: "title:*<brand3>*") {
    edges { node { handle title productsCount { count } } }
  }
  # ... up to ~10 aliases per single query
}
```

**Tip**: Shopify `query:` syntax uses wildcards `*` around keywords. Watch out
for brand names with spaces or apostrophes: escape them and keep the space,
e.g. `title:*acme pro*` not `title:acmepro`.

---

## Pattern B: Vendor-based search (single-brand hubs)

Use when the hub is brand-anchored. Query by `vendor:` instead of `title:` for
cleaner results.

```graphql
query VendorSubCollections {
  collections(first: 25, query: "vendor:<BrandName>") {
    edges { node { handle title productsCount { count } } }
  }
}
```

---

## Pattern C: Tag-based search (category hub spanning brands)

When the hub is a category (e.g. a compliance or material category) whose
members are pulled from multiple brands via a smart-collection tag rule.

```graphql
query TagSubCollections {
  collections(first: 30, query: "tag:<Your_Tag>") {
    edges {
      node {
        handle title productsCount { count }
        ruleSet { rules { column relation condition } }
      }
    }
  }
}
```

---

## Recording your verified handle map (template)

After running the discovery queries above, record the results so Step 7
(internal linking) and Step 10 (sub-nav) can reuse verified handles. Keep this
map in `brand-mapping.json` in the per-hub output folder, and optionally
mirror a human-readable version here.

Fill in your OWN store's brands and handles. The rows below are placeholders
that show the shape, not real data:

### Brand A family
| Sub-line | Handle | Products |
|---|---|---|
| Core line | `brand-a-core` | `<count>` |
| Pro line | `brand-a-pro` | `<count>` |
| Accessories | `brand-a-accessories` | `<count>` |
| All Products (umbrella) | `brand-a-all-products` | `<count>` |

### Brand B family
| Sub-line | Handle | Products |
|---|---|---|
| Core line | `brand-b-core` | `<count>` |
| Premium line | `brand-b-premium` | `<count>` |
| All Products (umbrella) | `brand-b-all-products` | `<count>` |

### Cross-hub categories (linkable from any brand-hub)
| Category | Handle | Products |
|---|---|---|
| Best sellers | `best-sellers` | `<count>` |
| New arrivals | `new-arrivals` | `<count>` |
| Bundles & sets | `bundles-sets` | `<count>` |

---

## How to extend for a new hub

1. Identify the brand or category anchor of the new hub.
2. Run Pattern A, B, or C with all relevant brand names (max ~10 aliases).
3. Add the verified `{handle, title, count}` rows to your map.
4. Use only the verified handles in Step 7 internal linking and Step 10 sub-nav.
5. Cross-reference the "cross-hub categories" above for the
   "Related collections" section.

If a brand or category is NOT yet in your map, run a discovery query FIRST and
add it BEFORE writing any link in the deep content. A link you cannot find in
the map is a hallucinated link: it fails Gate 1 and blocks the push.
