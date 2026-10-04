# Executive memo

## Finding

In the seeded demonstration, the typical procedure shows a max-to-min spread of roughly **2.7×** across published rates. The pipeline also surfaces hospital/procedure/payer rows materially above their peer benchmark.

## Decision use

Use the outlier queue to prioritize contract review or data-quality validation, then confirm that compared rates share the same service setting and rate type. Do not infer patient savings or market power from posted rates alone.

## Next evidence required

For a real Tennessee analysis, ingest current CMS-compliant hospital files, join facility identifiers to CMS Provider of Services and rural-urban classifications, and weight results with claims volume when available.
