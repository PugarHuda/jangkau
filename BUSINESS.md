# Jangkau business plan (inputs for cfo.ai)

> Draft numbers. Replace the cost per page with the measured tokens from
> `runs/*/report.md`, then build the model in cfo.ai and link it here.

## Customer
Small businesses, agencies and Shopify/WordPress sites that must meet WCAG 2.1 AA
(European Accessibility Act, ADA lawsuits) but cannot afford a manual audit,
which typically costs $1,000–5,000 per site.

## Pricing
| Plan | Price / month | Pages fixed / month |
|---|---|---|
| Starter | $29 | 25 |
| Pro | $99 | 150 |
| Agency | $299 | 600 |

## Cost per page (estimate, replace with measured value)
~10 rules × ~1.5 attempts × ~5k tokens ≈ 75k tokens per page
→ about **$0.25 per page** on a Sonnet-class model, plus about $0.01 of compute.

| Plan | Revenue | Inference cost (full usage) | Gross margin |
|---|---|---|---|
| Starter | $29 | $6.50 | 78% |
| Pro | $99 | $39 | 61% |
| Agency | $299 | $156 | 48% |

Lever: route simple rules (lang, title, alt) to a cheap model such as Nova and keep
the strong model for color contrast and layout. That should raise margins by 15–25 points.

## Scenarios for cfo.ai
- **Base:** 100 paying customers after 12 months (70 Starter / 25 Pro / 5 Agency) ≈ $6.0k MRR
- **Growth:** 300 customers, same mix ≈ $18k MRR
- Fixed costs: hosting $100/mo, tools $200/mo, founder salary $0 for the first 6 months
- Runway: model it against $10k starting cash
