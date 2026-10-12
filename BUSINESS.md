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
Full fixing runs on four real pages, each with both models, cost as reported by the LiteLLM gateway
on every call (`x-litellm-response-cost`), not estimated from token counts. Every run ends at 0 failing
elements. Data: `runs/cost-bench/` (`python scripts/cost_bench.py`).

| Page | Failing elements | Haiku (escalates to Sonnet when stuck) | Sonnet 4.6 throughout |
|---|---|---|---|
| Coffee shop (demo) | 25 → 0 | $0.025 | $0.064 |
| Batik shop (demo) | 47 → 0 | $0.059 | $0.174 |
| StartBootstrap Freelancer | 33 → 0 | $0.115 | $0.234 |
| W3C inaccessible demo (live) | 81 → 0 | $0.159 | $0.410 |
| **Mean** | | **$0.090** | **$0.220** |

Haiku is the default: same result, 2.5× cheaper. Plus about $0.01 of compute per page (headless Chromium
for about a minute). `--max-cost` caps what one page may spend; rules run in impact order, so a capped
page still gets its critical and serious fixes first.

| Plan | Revenue | Inference cost (full usage, $0.09/page) | Gross margin |
|---|---|---|---|
| Starter | $29 | $2.25 | 92% |
| Pro | $99 | $13.50 | 86% |
| Agency | $299 | $54 | 82% |

## The cfo.ai model

Monthly, Nov 2026 – Oct 2028. Customers by plan follow `customers[-1] × (1 − churn) + new per month × mix`.
MRR, inference COGS (customers × pages × cost per page) and 3% payment fees follow from that,
then fixed costs, net cash flow and the cash balance from $10k. New customers per month is
sized so customers reach the month-12 target in each scenario.

| | Base | Growth | Downside |
|---|---|---|---|
| New customers / month | 10.4 | 31 | 4.13 |
| Cost per page (measured) | $0.09 (Haiku mean) | $0.09 | $0.41 (worst page, Sonnet) |
| Customers, month 12 | ~100 | ~300 | ~40 |
| MRR, month 12 (Oct 2027) | $6.0k | $18.0k | $2.4k |
| MRR, month 24 (Oct 2028) | $9.7k | $29.0k | $3.9k |
| Gross margin | 84.3% | 84.3% | 38.9% |
| Lowest cash | $10k (never below start) | $10k | runs out **Aug 2027** |
| Cash, Oct 2028 | $67k | $302k | −$29k |

Base is cash-flow positive every month except May 2027 (−$33), when the founder salary starts.
The downside teaches the pricing rule: at $0.41 per page an Agency customer who uses all 600 pages costs
$246 on a $299 plan, and with few customers the cash still runs out in Aug 2027. The product enforces the
answer: Haiku by default and a per-page `--max-cost` cap keep pages out of the Sonnet worst case.
Delaying the salary only moves the cash-out date.
