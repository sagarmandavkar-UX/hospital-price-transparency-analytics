# Methodology

## Analytical question

How much do negotiated hospital prices vary for comparable procedure codes, and which observable hospital or payer characteristics are associated with that variation?

## Pipeline

1. Enforce the required machine-readable-file schema.
2. Parse currency strings and quarantine invalid rates.
3. Standardize payer names and deduplicate hospital/procedure/payer rows.
4. Calculate procedure-level median, minimum, maximum, and max-to-min ratios.
5. Normalize rates by the within-procedure median for payer comparisons.
6. Fit an interpretable log-price model with rurality, log beds, procedure, and payer controls.
7. Produce a benchmark-relative outlier queue for operational review.

## Interpretation boundaries

The unit is a published negotiated rate, not a claim, patient, or service. Results are not utilization weighted. The model estimates associations; hospital size and rurality coefficients must not be interpreted as causal. Real hospital files also require payer-plan normalization, billing-code validation, and explicit handling of rate type and setting.
