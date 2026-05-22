"""
Synthetic Data Generator for RevOps Skills Pack
================================================

Produces a realistic-looking fake B2B SaaS company dataset:
- 1 company (Northwind Cloud, fake)
- 10 sales reps with varied attributes
- ~250 opportunities across 6 stages with realistic distributions
- 12 weeks of historical forecast submissions per rep
- Activity history on each opportunity

Design notes:
- Deterministic via fixed seed so outputs are reproducible
- Calibrated to look like a Series C SaaS company doing ~$15M ARR
- Includes realistic forecast inaccuracy patterns: some reps are sandbaggers,
  some are commit-and-pray optimists, some are well-calibrated
- Pipeline includes intentional hygiene problems: stale opps, missing
  next steps, unrealistic close dates. These are the things the Skills
  will catch.

Run: python data/generate_synthetic_data.py
Outputs to: data/
"""

import json
import random
import csv
from datetime import datetime, timedelta
from pathlib import Path

SEED = 20260520
random.seed(SEED)

OUTPUT_DIR = Path(__file__).parent
TODAY = datetime(2026, 5, 20)
QUARTER_END = datetime(2026, 6, 30)

# ============================================================================
# COMPANY AND TEAM
# ============================================================================

COMPANY = {
    "name": "Northwind Cloud",
    "industry": "B2B SaaS",
    "stage": "Series C",
    "arr_usd": 15_400_000,
    "fiscal_year_end": "January 31",
    "current_quarter": "Q2 FY2027",
    "quarter_end": QUARTER_END.isoformat()[:10],
}

# 10 reps. Calibration profiles drive how their forecasts compare to reality.
# "sandbagger" reps consistently under-commit. "optimist" reps consistently
# over-commit. "calibrated" reps land within +/- 10% of actual.
REPS = [
    {"id": "rep_001", "name": "Aisha Okonkwo",     "segment": "Enterprise", "tenure_months": 38, "profile": "calibrated"},
    {"id": "rep_002", "name": "Diego Marquez",     "segment": "Enterprise", "tenure_months": 22, "profile": "optimist"},
    {"id": "rep_003", "name": "Priya Raman",       "segment": "Mid-Market", "tenure_months": 51, "profile": "sandbagger"},
    {"id": "rep_004", "name": "Tomas Lindgren",    "segment": "Mid-Market", "tenure_months": 14, "profile": "optimist"},
    {"id": "rep_005", "name": "Yuki Tanaka",       "segment": "Mid-Market", "tenure_months": 29, "profile": "calibrated"},
    {"id": "rep_006", "name": "Marcus Bell",       "segment": "Commercial", "tenure_months": 8,  "profile": "wildcard"},
    {"id": "rep_007", "name": "Sofia Restrepo",    "segment": "Commercial", "tenure_months": 19, "profile": "calibrated"},
    {"id": "rep_008", "name": "Hannes Vogel",      "segment": "Commercial", "tenure_months": 11, "profile": "optimist"},
    {"id": "rep_009", "name": "Lakshmi Iyer",      "segment": "Enterprise", "tenure_months": 44, "profile": "sandbagger"},
    {"id": "rep_010", "name": "Wei Chen",          "segment": "Commercial", "tenure_months": 5,  "profile": "wildcard"},
]

# ============================================================================
# OPPORTUNITY GENERATION
# ============================================================================

STAGES = [
    {"name": "Discovery",     "order": 1, "default_probability": 10},
    {"name": "Qualification", "order": 2, "default_probability": 20},
    {"name": "Proposal",      "order": 3, "default_probability": 40},
    {"name": "Negotiation",   "order": 4, "default_probability": 65},
    {"name": "Verbal",        "order": 5, "default_probability": 85},
    {"name": "Closed Won",    "order": 6, "default_probability": 100},
    {"name": "Closed Lost",   "order": 7, "default_probability": 0},
]

FORECAST_CATEGORIES = ["Pipeline", "BestCase", "Commit", "Closed", "Omitted"]

DEAL_SIZE_BY_SEGMENT = {
    "Enterprise": (75_000, 450_000),
    "Mid-Market": (18_000, 95_000),
    "Commercial": (5_000, 28_000),
}

# Fake account names. Designed to be obviously synthetic (no real companies).
ACCOUNT_PREFIXES = [
    "Acme", "Globex", "Initech", "Umbrella", "Soylent", "Hooli", "Pied Piper",
    "Wonka", "Cyberdyne", "Tyrell", "Wayne", "Stark", "Oscorp", "LexCorp",
    "Massive Dynamic", "Buy n Large", "Vandelay", "Pendant Publishing",
    "Dunder Mifflin", "Sterling Cooper", "Pied Piper", "Aviato", "Hooli XYZ",
    "Bluth", "Sudden Valley", "Wernham Hogg", "Bluestar", "Anaconda Realty",
    "Mooby", "Quick Stop", "Krusty Krab", "Planet Express", "Mom's Friendly",
]
ACCOUNT_SUFFIXES = [
    "Industries", "Holdings", "Systems", "Technologies", "Solutions",
    "Corp", "Group", "Logistics", "Partners", "Capital", "Robotics",
    "Networks", "Dynamics", "Analytics", "Labs", "Health", "Bio",
]

def generate_account_name():
    return f"{random.choice(ACCOUNT_PREFIXES)} {random.choice(ACCOUNT_SUFFIXES)}"

def days_offset(days):
    """Return ISO date string for today + days."""
    return (TODAY + timedelta(days=days)).isoformat()[:10]

def generate_opportunity(opp_id, rep, force_problems=False):
    """
    Generate one opportunity. If force_problems=True, intentionally inject
    a hygiene issue (stale activity, unrealistic close date, missing field, etc).
    """
    segment = rep["segment"]
    size_min, size_max = DEAL_SIZE_BY_SEGMENT[segment]
    amount = random.randint(size_min, size_max)
    amount = round(amount / 500) * 500  # round to nearest $500

    # Distribute stages with realistic weighting (more in early stages)
    stage_weights = [25, 22, 20, 15, 8, 6, 4]
    stage = random.choices(STAGES, weights=stage_weights)[0]

    # Close date logic
    if stage["name"] in ("Closed Won", "Closed Lost"):
        # Closed in the past, but AFTER created_date which we'll constrain below
        close_date_offset = random.randint(-30, -1)
    elif stage["name"] == "Verbal":
        close_date_offset = random.randint(3, 25)
    elif stage["name"] == "Negotiation":
        close_date_offset = random.randint(10, 60)
    elif stage["name"] == "Proposal":
        close_date_offset = random.randint(20, 90)
    else:
        close_date_offset = random.randint(30, 180)

    # Last activity (most healthy = recent, some are stale)
    if force_problems and random.random() < 0.7:
        last_activity_days_ago = random.randint(21, 90)  # stale
    else:
        last_activity_days_ago = random.randint(0, 14)  # healthy

    # Next step
    next_steps = [
        "Schedule security review with their CISO",
        "Follow up on pricing after Friday's call",
        "Send revised SOW reflecting reduced scope",
        "Get verbal commit on close date from buyer",
        "Confirm budget approval from CFO",
        "Loop in their legal team on MSA redlines",
        "Demo the API integration to their eng team",
        "Send mutual close plan for sign-off",
    ]
    next_step = "" if force_problems and random.random() < 0.5 else random.choice(next_steps)

    # Forecast category based on stage + rep profile
    if stage["name"] in ("Closed Won", "Closed Lost"):
        forecast_cat = "Closed"
    elif stage["name"] == "Verbal":
        forecast_cat = "Commit"
    elif stage["name"] == "Negotiation":
        # Optimists commit too early, sandbaggers undercommit
        if rep["profile"] == "optimist":
            forecast_cat = "Commit"
        elif rep["profile"] == "sandbagger":
            forecast_cat = "BestCase"
        else:
            forecast_cat = random.choice(["Commit", "BestCase"])
    elif stage["name"] == "Proposal":
        if rep["profile"] == "optimist":
            forecast_cat = "BestCase"
        else:
            forecast_cat = "Pipeline"
    else:
        forecast_cat = "Pipeline"

    # Created date: must be before close date for closed deals to make cycle math sensible
    if stage["name"] in ("Closed Won", "Closed Lost"):
        close_date_actual_offset = close_date_offset
        created_offset = close_date_actual_offset - random.randint(30, 240)
    else:
        created_offset = -random.randint(30, 240)

    account_name = generate_account_name()
    deal_type = random.choice(['Platform', 'Expansion', 'Renewal', 'New Logo', 'Upsell'])

    return {
        "id": opp_id,
        "name": f"{account_name} - {deal_type}",
        "account_name": account_name,
        "owner_id": rep["id"],
        "owner_name": rep["name"],
        "segment": segment,
        "amount": amount,
        "stage": stage["name"],
        "stage_order": stage["order"],
        "probability": stage["default_probability"],
        "forecast_category": forecast_cat,
        "close_date": days_offset(close_date_offset),
        "created_date": days_offset(created_offset),
        "last_activity_date": days_offset(-last_activity_days_ago),
        "next_step": next_step,
        "days_since_last_activity": last_activity_days_ago,
        "is_closed": stage["name"] in ("Closed Won", "Closed Lost"),
        "is_won": stage["name"] == "Closed Won",
    }

# ============================================================================
# GENERATE OPPORTUNITIES
# ============================================================================

def generate_pipeline():
    opportunities = []
    opp_counter = 1
    # Each rep gets 20-30 opps, with ~25% having hygiene problems
    for rep in REPS:
        opp_count = random.randint(20, 30)
        for _ in range(opp_count):
            opp_id = f"opp_{opp_counter:04d}"
            force_problems = random.random() < 0.25
            opportunities.append(generate_opportunity(opp_id, rep, force_problems))
            opp_counter += 1
    return opportunities

# ============================================================================
# FORECAST HISTORY
# ============================================================================

def generate_forecast_history(opportunities):
    """
    Generate 12 weeks of historical forecast submissions per rep.
    Each rep's submissions reflect their calibration profile.
    """
    history = []
    for rep in REPS:
        rep_opps_closed = [o for o in opportunities if o["owner_id"] == rep["id"] and o["is_closed"]]
        actual_closed_won = sum(o["amount"] for o in rep_opps_closed if o["is_won"])

        for week_offset in range(12, 0, -1):
            week_date = TODAY - timedelta(weeks=week_offset)
            # Profile-driven commit accuracy
            if rep["profile"] == "calibrated":
                commit_multiplier = random.uniform(0.92, 1.08)
            elif rep["profile"] == "optimist":
                commit_multiplier = random.uniform(1.15, 1.45)
            elif rep["profile"] == "sandbagger":
                commit_multiplier = random.uniform(0.55, 0.78)
            else:  # wildcard
                commit_multiplier = random.uniform(0.4, 1.6)

            # Best case is higher than commit
            bestcase_multiplier = commit_multiplier * random.uniform(1.15, 1.35)

            # Quarterly forecast (simulated - rep commits a $ amount for the quarter)
            base_commit = actual_closed_won / 4 if actual_closed_won > 0 else random.randint(20_000, 80_000)

            history.append({
                "rep_id": rep["id"],
                "rep_name": rep["name"],
                "week_of": week_date.isoformat()[:10],
                "commit_amount": round(base_commit * commit_multiplier / 500) * 500,
                "bestcase_amount": round(base_commit * bestcase_multiplier / 500) * 500,
                "pipeline_amount": round(base_commit * bestcase_multiplier * 1.5 / 500) * 500,
            })
    return history

# ============================================================================
# QUARTERLY ACTUALS
# ============================================================================

def generate_quarterly_actuals(opportunities):
    """Per-rep summary of actual closed-won this quarter."""
    actuals = []
    for rep in REPS:
        rep_opps = [o for o in opportunities if o["owner_id"] == rep["id"]]
        won = [o for o in rep_opps if o["is_won"]]
        lost = [o for o in rep_opps if o["stage"] == "Closed Lost"]
        open_opps = [o for o in rep_opps if not o["is_closed"]]
        actuals.append({
            "rep_id": rep["id"],
            "rep_name": rep["name"],
            "profile": rep["profile"],
            "segment": rep["segment"],
            "tenure_months": rep["tenure_months"],
            "closed_won_amount": sum(o["amount"] for o in won),
            "closed_won_count": len(won),
            "closed_lost_amount": sum(o["amount"] for o in lost),
            "closed_lost_count": len(lost),
            "open_pipeline_amount": sum(o["amount"] for o in open_opps),
            "open_pipeline_count": len(open_opps),
        })
    return actuals

# ============================================================================
# MAIN
# ============================================================================

def main():
    print("Generating Northwind Cloud synthetic dataset...")

    opportunities = generate_pipeline()
    forecast_history = generate_forecast_history(opportunities)
    actuals = generate_quarterly_actuals(opportunities)

    # Write company.json
    with open(OUTPUT_DIR / "company.json", "w") as f:
        json.dump({"company": COMPANY, "reps": REPS}, f, indent=2)

    # Write opportunities.json + opportunities.csv (both formats for flexibility)
    with open(OUTPUT_DIR / "opportunities.json", "w") as f:
        json.dump(opportunities, f, indent=2)

    with open(OUTPUT_DIR / "opportunities.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=opportunities[0].keys())
        writer.writeheader()
        writer.writerows(opportunities)

    # Write forecast history
    with open(OUTPUT_DIR / "forecast_history.json", "w") as f:
        json.dump(forecast_history, f, indent=2)

    with open(OUTPUT_DIR / "forecast_history.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=forecast_history[0].keys())
        writer.writeheader()
        writer.writerows(forecast_history)

    # Write quarterly actuals
    with open(OUTPUT_DIR / "quarterly_actuals.json", "w") as f:
        json.dump(actuals, f, indent=2)

    # Summary
    print(f"  Reps:                 {len(REPS)}")
    print(f"  Opportunities:        {len(opportunities)}")
    print(f"  Open pipeline value:  ${sum(o['amount'] for o in opportunities if not o['is_closed']):,}")
    print(f"  Closed won (qtd):     ${sum(o['amount'] for o in opportunities if o['is_won']):,}")
    print(f"  Forecast history:     {len(forecast_history)} weekly submissions")
    print(f"  Output:               {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
