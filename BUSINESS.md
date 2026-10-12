# Jangkau business plan (inputs for cfo.ai)

> The model is built in cfo.ai (built through the cfo.ai MCP server from Claude Code):
> workspace page **Jangkau model**, with the tables Plan assumptions, Company assumptions,
> Customers and revenue, and P&L and cash, plus the scenarios Base, Growth and Downside.
> Live model: https://cfo.ai/s/eaPiXgVJ6eZosuDO (view-only, Base scenario). Results are in [the cfo.ai model](#the-cfoai-model) below.

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
Measured run (v4, claude-haiku, shop.html, 47 → 0 failing nodes): 16 LLM calls,
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

## The cfo.ai model

Monthly, Nov 2026 – Oct 2028. Customers by plan follow `customers[-1] × (1 − churn) + new per month × mix`.
MRR, inference COGS (customers × pages × cost per page) and 3% payment fees follow from that,
then fixed costs, net cash flow and the cash balance from $10k. New customers per month is
sized so customers reach the month-12 target in each scenario.

| | Base | Growth | Downside |
|---|---|---|---|
| New customers / month | 10.4 | 31 | 4.13 |
| Cost per page | $0.10 | $0.10 | $0.50 |
| Customers, month 12 | ~100 | ~300 | ~40 |
| MRR, month 12 (Oct 2027) | $6.0k | $18.0k | $2.4k |
| MRR, month 24 (Oct 2028) | $9.7k | $29.0k | $3.9k |
| Gross margin | 82.8% | 82.8% | 26.2% |
| Lowest cash | $10k (never below start) | $10k | runs out **Aug 2027** |
| Cash, Oct 2028 | $65k | $296k | −$37k |

Base is cash-flow positive every month except May 2027 (−$88), when the founder salary starts.
The downside teaches the pricing rule: at $0.50 per page an Agency customer who uses all 600 pages costs
$300 on a $299 plan. If real-site cost per page rises, cap fair use or reprice Agency before
growing. Delaying the salary only moves the cash-out date.
