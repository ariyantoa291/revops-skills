# Salesforce RevOps Audit, May 20, 2026

Run against the synthetic Northwind Cloud dataset (Q2 FY2027).

## Overall Health: B (87/100)

B grade overall. The pack is in reasonable shape. The Pipeline Health dimension is the limiting factor and should be addressed before the next forecast call.

## Dimensional Scores

| Dimension | Grade | Score | Weight |
|---|---|---:|---:|
| Pipeline Health | C | 75/100 | 25% |
| Data Quality | A | 90/100 | 20% |
| Forecast Hygiene | A | 100/100 | 25% |
| Deal Integrity | C | 75/100 | 20% |
| Process Integrity | A | 100/100 | 10% |

## What's driving the grade

### Pipeline Health: C
- Pipeline coverage is 4.9x committed forecast (healthy).
- 48% of pipeline value is in Discovery/Qualification, above the 30% healthy threshold.
- Aisha Okonkwo holds 28% of total pipeline value (single-rep concentration risk).
- Average opportunity age is 145 days.

### Data Quality: A
- 20% of open opportunities have stale activity (>14 days), above 15% threshold.
- 15% of late-stage opportunities have no next step (11 of 72).

### Forecast Hygiene: A
- Team commit varies +14.1% from historical model (within 15% threshold).
- 3 of 10 reps show variance above 20% from their personal historical pattern.

### Deal Integrity: C
- No large opportunities have 3+ compounding risk flags.
- Diego Marquez holds 28% of late-stage pipeline value.
- 7 opportunities in Commit category with stale activity beyond 21 days.

### Process Integrity: A
- Probability-stage alignment is healthy (0% mismatch rate).
- Forecast category and stage alignment is clean (0% mismatch).

## Remediation queue, in order

The audit recommends running these skills in this sequence. Each skill targets the lowest-scoring dimension and produces a concrete deliverable.

1. **pipeline-hygiene-audit** addresses Pipeline Health. Potential lift: roughly 25 points on the dimension score if the recommended issues are remediated.

2. **deal-investigator** addresses Deal Integrity. Potential lift: roughly 20 points on the dimension score if the recommended issues are remediated.

## What the audit cannot tell you

This audit measures system health based on data already in Salesforce. It cannot diagnose:

- Activity capture failures (Einstein Activity Capture, Outreach sync gaps). A dedicated `activity-capture-diagnostic` skill is planned for v0.2.
- Lead routing logic issues (LeanData, Salesforce Assignment Rules). Planned for v0.2.
- Compensation calculation errors. Planned for v0.2.
- Whether reps actually know how to use the system. Human conversation only.

## Re-run cadence

Re-run this audit quarterly as a recurring health check. Also re-run after any major Salesforce migration or process change, when a new RevOps leader takes over the org, or before any sales planning cycle (annual or quarterly planning).
