# Experiments and reproduction

Run `python scripts/evaluate_all.py` from this repository. The report is written to `reports/evaluation-results.json`. This executes real calculations; model quality is separate from test success.

## Recorded baseline

```json
{
  "checks": {
    "budget": true,
    "diet": true,
    "stock": true
  },
  "note": "Constraint checks, not a measured household waste-reduction study."
}
```

## Interpretation

Reviewed stock and integer meal planning. No validated food safety assessment or longitudinal waste-reduction study.

The raw reports describe whether measurements are synthetic benchmarks, controlled regression fixtures or invariants. Do not interpret regression-fixture accuracy as a held-out real-world score. Preserve seeds and splits when comparing changes.
