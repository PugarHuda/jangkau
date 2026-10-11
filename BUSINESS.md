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

## Cost per page (measured)
Measured run (v4, claude-haiku, toko.html, 47 → 0 failing nodes): 16 LLM calls,
33.1k input + 5.1k output tokens ≈ **$0.06 per page** (Haiku list price $1/$5 per M tokens),
plus about $0.01 of compute (one headless Chromium for about 70 s).
Budget conservatively with **$0.10 per page** (bigger real-world pages, retries).

| Plan | Revenue | Inference cost (full usage, $0.10/page) | Gross margin |
|---|---|---|---|
| Starter | $29 | $2.50 | 91% |
| Pro | $99 | $15 | 85% |
| Agency | $299 | $60 | 80% |

Risk: real sites are 10–50× larger than the demo pages. That needs chunking per section,
and cost per page could grow 3–5×. Margins stay above 50% even at $0.50 per page on Pro.

## Scenarios for cfo.ai
- **Base:** 100 paying customers after 12 months (70 Starter / 25 Pro / 5 Agency) ≈ $6.0k MRR
- **Growth:** 300 customers, same mix ≈ $18k MRR
- Fixed costs: hosting $100/mo, tools $200/mo, founder salary $0 for the first 6 months
- Runway: model it against $10k starting cash
