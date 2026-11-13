# Model and simulator card — Fridge Court

## Intended use

A reviewed household stock ledger and feasible meal planner that keeps OCR estimates separate from confirmed inventory.

## Implemented methods

- Manual inventory with units, dates and consumption/waste events
- Receipt-text parsing with optional system Tesseract OCR
- Explicit review and confirmation before receipt stock changes
- Integer-constrained meal selection under stock, diet and budget
- Household-day controls and near-expiry prioritization

Some projects use deterministic simulators and rules rather than trained neural models. Those distinctions are retained in this card and the source.

## Evaluation

See `docs/EXPERIMENTS.md` and the machine-readable reports. No pretrained foundation-model weights or real-world efficacy certification are included. Parameters, splits and synthetic generators are visible in source.

## Limitations

Reviewed stock and integer meal planning. No validated food safety assessment or longitudinal waste-reduction study.

## Extensions not implemented in this release

- Consumption forecasting and uncertain-stock reconciliation
- Permissioned household trials measuring actual waste reduction
