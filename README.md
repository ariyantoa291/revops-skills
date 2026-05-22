# revops-skills

> A set of [Claude Agent Skills](https://www.anthropic.com/news/skills) built for the Salesforce-native RevOps systems work that Anthropic's [official sales plugin](https://github.com/anthropics/knowledge-work-plugins/tree/main/sales) does not cover. Where the Anthropic plugin targets the AE persona (account research, call prep, outreach drafting), this pack targets the RevOps practitioner who designs the system itself: pipeline hygiene, forecast call reconciliation, and deal-level pressure testing against historical patterns. Built on the synthetic Northwind Cloud dataset. Designed to run against any Salesforce MCP server, or against the bundled sample data with zero setup.

## What this is

Four Agent Skills that encode practitioner-level RevOps judgment as executable instructions Claude can follow. Each skill produces an executive-ready deliverable from a single prompt.

| Skill | Output | Status |
|---|---|---|
| [salesforce-revops-audit](skills/salesforce-revops-audit/) | Graded health report (A through F) across pipeline health, data quality, forecast hygiene, deal integrity, and process integrity, with a prioritized remediation queue | shipped |
| [forecast-call-prep](skills/forecast-call-prep/) | Weekly forecast call memo with variance, risks, and recommended position | shipped |
| [pipeline-hygiene-audit](skills/pipeline-hygiene-audit/) | Per-rep hygiene punchlist with severity-ranked issues | shipped |
| [deal-investigator](skills/deal-investigator/) | Structured deal review for a single opportunity, with risk indicators and a recommendation | shipped |
| activity-capture-diagnostic | Einstein Activity Capture and Outreach sync diagnostic with per-rep capture rates | planned |
| lead-routing-rule-analyzer | LeanData and Salesforce Assignment Rules diagnostic | planned |
| comp-plan-stress-test | Comp plan analyzer with historical attainment overlay | planned |

## Where to start

Run `salesforce-revops-audit` first. It's the entry point. The audit grades your org across five dimensions and recommends which of the remediation skills to run next, in what order. You can also run any of the remediation skills directly if you know exactly what you want to fix.

## What this is not

- A Salesforce MCP server. Salesforce already ships [several of those](https://developer.salesforce.com/blogs/2026/04/salesforce-hosted-mcp-servers-are-now-generally-available).
- A connector. These skills sit on top of any Salesforce MCP, HubSpot MCP, or local data.
- A product. This is open-source practitioner work under MIT license.

## How to use

### Without Salesforce (works immediately)

1. Clone this repo.
2. Open [Claude Desktop](https://claude.ai/download) or [Claude Code](https://docs.claude.com/en/docs/claude-code).
3. Point Claude at the skills folder.
4. Try: *"use forecast-call-prep on the Northwind sample data"*

You will get a [memo like this](skills/forecast-call-prep/examples/sample_output.md) in 30 seconds.

### With Salesforce

1. Configure a [Salesforce-hosted MCP](https://developer.salesforce.com/blogs/2026/04/salesforce-hosted-mcp-servers-are-now-generally-available) in your Claude client. Salesforce's docs cover this in 10 minutes.
2. Clone this repo and install the skills.
3. Try: *"use forecast-call-prep against my Salesforce data"*

The skill will use your live data, your live forecast history, and your real reps. Output is identical in shape to the sample.

## Why these specific skills

Six workflows that map to the actual day of a Director of Revenue Operations:

- **Monday**: forecast call prep
- **Tuesday**: pipeline hygiene
- **Wednesday**: deal review for a stuck opp
- **Quarterly**: QBR brief assembly, comp plan stress test
- **Ongoing**: rep calibration tracking

Each skill addresses a specific deliverable that currently requires 2 to 6 hours of manual work per occurrence. Together they cover roughly 60% of the recurring analytical work a RevOps lead does.

## Design principles

Every skill in this repo follows the same rules:

1. **Tool-agnostic**: works against Salesforce MCP, CSV, JSON, or sample data.
2. **Stateless**: no credentials, no API keys, no persistence on the maintainer's side.
3. **Director-level output**: produces deliverables a CRO would actually read, not raw analysis.
4. **Honest about limits**: degrades gracefully when data is missing, flags when confidence is low.
5. **Documented logic**: every threshold, every rule, every cutoff is in the SKILL.md, not buried in code.

## Synthetic dataset

The repo includes [Northwind Cloud](data/), a synthetic Series C SaaS company with:

- 10 sales reps with varied calibration profiles (sandbaggers, optimists, well-calibrated, wildcards)
- 242 opportunities across realistic stage distribution
- 12 weeks of forecast submission history per rep
- Intentional hygiene problems: stale activity, missing next steps, unrealistic close dates

Run `python data/generate_synthetic_data.py` to regenerate with the same seed. The dataset is deterministic.

## Roadmap

- **v0.1** (shipped): salesforce-revops-audit, forecast-call-prep, pipeline-hygiene-audit, deal-investigator
- **v0.2**: activity-capture-diagnostic, lead-routing-rule-analyzer
- **v0.3**: comp-plan-stress-test, compensation-dispute-investigator
- **v1.0**: All planned skills + companion evaluation suite ([RevOpsEval](https://revopseval.com))

## Contributing

Skills should encode practitioner judgment, not generic prompts. If you have an opinionated take on a RevOps workflow that produces a clear deliverable, open an issue first to discuss scope. PRs welcome.

## Author

Built by [Eli Jean Gilles](https://www.linkedin.com/in/eli-jean-gilles/). Nine years in revenue operations across SaaS, life sciences, and ad-tech. Currently Senior Sales Operations Manager at Zynga (Take-Two Interactive). Salesforce Certified Administrator. Nine Anthropic AI certifications including [MCP Advanced Topics](https://docs.claude.com/en/docs/mcp) and [Introduction to Agent Skills](https://www.anthropic.com/news/skills).

## License

MIT. Use it, fork it, modify it, ship it inside your org. Attribution appreciated but not required.
