# Salesforce RevOps Audit, May 22, 2026

Run against the synthetic Northwind Cloud dataset (Q2 FY2027, quarter ends 2026-06-30).

## Overall Health: B (84/100)

B grade overall. Forecast Hygiene and Process Integrity are clean, but Deal Integrity has dropped to D once the full deal-investigator rubric is applied — three large opportunities carry 3+ compounding risk flags. Pipeline Health remains the second drag and should be addressed before the next forecast call.

## Dimensional Scores

| Dimension | Grade | Score | Weight |
|---|---|---:|---:|
| Pipeline Health | C | 75/100 | 25% |
| Data Quality | A | 90/100 | 20% |
| Forecast Hygiene | A | 100/100 | 25% |
| Deal Integrity | D | 60/100 | 20% |
| Process Integrity | A | 100/100 | 10% |

## What's driving the grade

### Pipeline Health: C
- Pipeline coverage is 4.8x in-quarter BestCase+Commit ($21.2M open / $4.4M) — well above the 2.5x threshold.
- 47.9% of open pipeline value ($10.2M of $21.2M) sits in Discovery/Qualification, above the 30% healthy threshold.
- Aisha Okonkwo holds 28.3% of total open pipeline ($6.0M of $21.2M); Lakshmi Iyer is close behind at 26.6%. Single-rep concentration exceeds the 25% threshold.
- Average opportunity age is 147 days, above the 90-day healthy mark.
- Win rate over closed-this-quarter is 74.1% (20 of 27) — healthy.

### Data Quality: A
- 20.1% of open opportunities (45 of 224) have stale activity beyond 14 days — in the 15–25% band, costs 10 points.
- 15.3% of late-stage opportunities (11 of 72 in Negotiation/Verbal) lack a next step — below the 20% threshold.
- 0% of open opportunities have close dates in the past.
- 0% have probability values that mismatch their stage by 25+ points.

### Forecast Hygiene: A
- Team commit this week is $275.5K, -5.5% versus the 11-week historical mean of $291.5K — well inside the 15% band.
- 1 of 10 reps (Marcus Bell, +32% variance) is uncalibrated against their personal history. Below the >50% trip wire.
- Aisha Okonkwo accounts for 28.5% of total committed forecast — below the 40% single-rep concentration line.
- In-quarter pipeline-weighted forecast ($3.9M) far exceeds team commit ($275.5K), so the coverage-thinness check does not fire.

### Deal Integrity: D
- 3 opportunities over $100K carry 3+ compounding risk flags (deal-investigator rubric: stale activity, missing next step, amount above 2x comparable closed-deal median for the segment):
  - `opp_0024` LexCorp Logistics — Expansion, $361.5K, Discovery, owner Aisha Okonkwo
  - `opp_0029` Wernham Hogg Logistics — Expansion, $314.0K, Discovery, owner Diego Marquez
  - `opp_0216` Wernham Hogg Dynamics — Expansion, $434.0K, Proposal, owner Lakshmi Iyer
- Aisha Okonkwo holds 25.9% of late-stage pipeline value ($2.87M of $11.08M), above the 20% threshold. Diego Marquez and Lakshmi Iyer trail at 24.1% and 23.7%, so the concentration is real, not idiosyncratic.
- 7 opportunities in the Commit category have stale activity beyond 21 days, including `opp_0087` Stark Robotics — Platform ($87.5K, 42d stale, Tomas Lindgren) and `opp_0115` Massive Dynamic Networks — Expansion ($55K, 71d stale, Yuki Tanaka).
- Median time-in-stage for Verbal cannot be measured without stage-change history; days-since-last-activity for Verbal opps has a median of 9 days, so the deals appear to be moving even though no formal time-in-stage check is possible.

### Process Integrity: A
- Probability-stage mismatch rate is 0% — well under the 15% threshold.
- Forecast category and stage are aligned for 100% of open opportunities.
- Stage-progression-without-activity and dual-owner checks require event-level history that this dataset does not include; flagged as insufficient data, no deduction taken.

## Remediation queue, in order

The audit recommends running these skills in this sequence. Each skill targets the lowest-scoring dimension and produces a concrete deliverable.

1. **deal-investigator** addresses Deal Integrity. Run once per flagged opportunity: `opp_0024`, `opp_0029`, `opp_0216`. Potential lift: roughly 30–40 points on the dimension score if the three deals are pressure-tested, repriced or omitted, and the seven stale Commit-category deals are scrubbed.

2. **pipeline-hygiene-audit** addresses Pipeline Health and Data Quality together. Potential lift: roughly 25 points on Pipeline Health (early-stage concentration, single-rep concentration, opp age) and 10 points on Data Quality (45 stale-activity opps).

## What the audit cannot tell you

This audit measures system health based on data already in Salesforce. It cannot diagnose:

- Activity capture failures (Einstein Activity Capture, Outreach sync gaps). A dedicated `activity-capture-diagnostic` skill is planned for v0.2.
- Lead routing logic issues (LeanData, Salesforce Assignment Rules). Planned for v0.2.
- Compensation calculation errors. Planned for v0.2.
- Whether reps actually know how to use the system. Human conversation only.

Within this dataset specifically, stage-change history and per-stage time-in-stage averages are not present, so the Verbal time-in-stage and stage-progression-without-activity checks were flagged as insufficient data rather than scored — the true Deal Integrity and Process Integrity grades could be modestly worse than reported here.

## Re-run cadence

Re-run this audit quarterly as a recurring health check. Also re-run after any major Salesforce migration or process change, when a new RevOps leader takes over the org, or before any sales planning cycle (annual or quarterly planning).
