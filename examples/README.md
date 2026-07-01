# examples/

Sample outputs from the kit, so you can see what a run produces before you run
it. These are **sanitized, generic** examples — the numbers and findings are
representative of a real audit but the store and product are fictional.

- [`product-analyze-example.md`](product-analyze-example.md) — a `product-analyze`
  quality report for a typical un-optimized product page (manufacturer-boilerplate
  description, no `Product` schema, no reviews). Shows the composite score, the
  triggered GATES, and the prioritized fix list.

> How these were produced: run `/product-analyze <product-url>` against a live
> Shopify product. The skill pulls Shopify Admin data, `curl`s the live page for
> `<head>` + JSON-LD (WebFetch is unreliable for those), scores the 5 categories,
> and writes the report to `output/[site]/products/[handle]/`.
