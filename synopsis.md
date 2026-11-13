# Synopsis — Fridge Court

**Ishdeep Singh · 12 November 2026**

## V2 interface release

A visual pantry and meal board.

- Ingredient cards, selected-lot use/waste actions and drag targets
- Editable receipt quantities and units before confirmation
- Diet and budget controls with a stock-feasible meal board
- Entered-date tracking and a kitchen event journal

Planning does not consume inventory automatically. Dates are user input, not food-safety advice. The underlying domain scope and research-extension boundaries below remain explicit.

## Implemented release

Runnable source: `lab/fridge.py`. Interface and backend are included. Tests and benchmark outputs accompany this distribution.

## Limits of the implemented release

Reviewed stock and integer meal planning. No validated food safety assessment or longitudinal waste-reduction study.

## Measured evaluation

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

## Original specification and proposed extensions

The material below preserves the design ambitions. Future-tense features and anticipated challenges are not completed-development claims.

Fridge Court

**Tagline:** The coriander has been summoned as a witness. Again.

### Concept, problem, and users

Fridge Court helps a household understand what food it has, what it is likely to use, and what it keeps wasting. Receipts record purchases, but they do not reveal exactly how much was eaten. The design therefore treats inventory as a reviewed estimate rather than perfect knowledge.

Target users are shared households and students managing limited grocery budgets. The main question is whether uncertainty-aware inventory and constrained meal planning reduce recorded waste compared with a simple expiry-reminder list.

### Proposed product and workflow

Scan a receipt or enter purchases manually, review product matches and quantities, and add items to the household inventory. Log consumption through quick actions or recipe preparation. A planner suggests meals that use available ingredients while respecting user-confirmed constraints. A weekly report highlights repeated waste and unnecessary repeat purchases.

Screens: receipt review, inventory, low-confidence stock checks, meal planner, shopping list, shared activity, and weekly report. Humour is optional: “You bought coriander three times; we should discuss your long-term intentions.” The user must be able to correct both the inventory and the joke settings.

### Data and system design

Records: `Household`, `Product`, `ReceiptLine`, `InventoryLot`, `StockEvent`, `Recipe`, `Constraint`, and `WasteEvent`. Stock changes are events, not unexplained overwrites. Store units and conversions explicitly; grams, packets, and pieces cannot be subtracted without a defined relationship.

Use permissioned household receipts and a small curated recipe collection. Open Food Facts is a possible product metadata integration, subject to its published data and image terms [R7]. It does not provide knowledge of what a particular household actually consumed. Dates must distinguish purchase date, user-entered expiry information, and forecasted usage.

### Algorithms and experiments

Baseline: manual stock and first-expiring-item reminders. Next: OCR plus product matching, probabilistic consumption forecasts, and constrained recipe selection. The planner's objective can balance likely waste, shopping cost, missing ingredients, and preference fit. Hard constraints must remain hard; a high preference score cannot compensate for violating a declared exclusion.

Start with daily usage estimates and explicit confidence. Request a quick stock check when uncertainty grows, rather than silently pretending the milk is still there. Forecasting data should be separated chronologically and, for generalization tests, by household.

Metrics: receipt-field accuracy after matching, inventory error against periodic manual counts, demand forecast error, constraint violations, and measured waste per household-period. A real waste-reduction study needs a comparable baseline period and consistent logging; a forecast of lower waste is not measured waste reduction. Ablate uncertainty prompts and consumption forecasting.

### Anticipated problems, in my voice

| What could go wrong | My likely reaction | Engineering response |
|---|---|---|
| Food disappears without a logged event | “Someone ate the evidence.” | Quick consumption actions and periodic stock confirmation |
| OCR confuses quantities or units | “Apparently I bought 400 onions. Financially concerning.” | Review low-confidence fields before committing stock |
| Meal suggestions ignore a declared constraint | “Great optimization, except the user cannot use the result.” | Validate every proposed plan against hard constraints |

### Demo, milestones, and limits

Scan a sample receipt, correct one uncertain line, plan a meal from near-expiry stock, and review a deliberately inaccurate inventory estimate. Milestones: manual event ledger; receipt review; recipe constraints; forecasting; household trial. Deliver reviewed inventory and planning reports. A photograph cannot establish that food is safe to eat, and forecasted dates must not be presented as safety guarantees.




## Problems actually encountered during the makeover

| The problem | In my voice | What changed |
|---|---|---|
| Sample B overwrote the file used by sample A | “Bro, this is an A/B test, why did B steal A’s identity?” | Recordings now get unique file names; a regression test checks both files remain distinct and unchanged. |
| A duplicate highlight followed row positions instead of duplicate evidence | “Apparently every third row had been arrested on vibes.” | Duplicate highlights now use exact record content and jump to a real duplicate. |
| The table displayed a rounded number that search did not match | “I copied the number from your own screen, my guy.” | Search checks both raw values and the formatted values visible in the table. |
| Graph labels became tiny on a phone | “Causal inference, now available to ants.” | Graph workspaces keep readable node widths and scroll within their own viewport. |
| Robot movement and the play button disagreed about whether it was running | “Gordon left the parking spot while the button was still contemplating life.” | The live flag is synchronized after accepted commands and remains off after rejected commands. |
| Fast screenshots caught an interface between renders | “The UI took a smoke break precisely when the camera arrived.” | Captures were inspected, incomplete frames replaced, and videos labelled as edited screenshots. |

These are observed build issues. Proposed research challenges in the original specifications remain proposed; this log does not invent months of model training or real deployments.
