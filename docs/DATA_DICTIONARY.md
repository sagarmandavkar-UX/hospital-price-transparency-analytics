# Data dictionary

| Field | Type | Definition |
|---|---|---|
| `hospital` | string | Reporting hospital or facility |
| `procedure_code` | string | Comparable billing/procedure code |
| `payer` | string | Standardized payer or cash category |
| `negotiated_rate` | string | Raw published rate before parsing |
| `rate` | numeric | Parsed positive negotiated rate |
| `rural` | boolean | Rural facility indicator from joined metadata |
| `beds` | integer | Licensed or staffed bed proxy |
| `relative_to_benchmark` | numeric | Rate divided by procedure/payer median |

The repository ships seeded demonstration data. Production use should retain original file URL, publication date, rate type, plan name, setting, code system, and ingestion timestamp.
