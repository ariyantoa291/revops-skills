#!/usr/bin/env python3
"""
rename_columns.py

Renames a Salesforce CSV export to match the column names expected by the
revops-skills pack. Run this once after exporting from Salesforce, and the
skills will be able to read your data without manual editing.

Usage:
    python3 tools/rename_columns.py my_data/opportunities.csv
    python3 tools/rename_columns.py my_data/opportunities.csv --type opportunities
    python3 tools/rename_columns.py my_data/forecasts.csv --type forecast_history

The script:
  - Detects whether the file is an opportunity export or a forecast history export
  - Renames known Salesforce field names to the skill-expected names
  - Adds computed columns (days_since_last_activity) if missing
  - Writes the result back to the same file (with a .bak backup)
  - Prints a summary of what changed
"""

import argparse
import csv
import os
import shutil
import sys
from datetime import datetime, date


# Salesforce field name -> skill-expected column name
# Covers the standard Salesforce REST API field names and common variations
# from Reports, Data Loader, and Workbench exports.
OPPORTUNITY_MAPPING = {
    # Standard Salesforce field names
    "Id": "id",
    "Name": "name",
    "Account.Name": "account_name",
    "Account: Account Name": "account_name",
    "OwnerId": "owner_id",
    "Owner.Name": "owner_name",
    "Owner: Full Name": "owner_name",
    "Account.Segment__c": "segment",
    "Segment__c": "segment",
    "Segment": "segment",
    "Amount": "amount",
    "StageName": "stage",
    "Stage": "stage",
    "Probability": "probability",
    "Probability (%)": "probability",
    "ForecastCategoryName": "forecast_category",
    "Forecast Category": "forecast_category",
    "ForecastCategory": "forecast_category",
    "CloseDate": "close_date",
    "Close Date": "close_date",
    "CreatedDate": "created_date",
    "Created Date": "created_date",
    "LastActivityDate": "last_activity_date",
    "Last Activity": "last_activity_date",
    "Last Activity Date": "last_activity_date",
    "NextStep": "next_step",
    "Next Step": "next_step",
    "IsClosed": "is_closed",
    "Closed": "is_closed",
    "IsWon": "is_won",
    "Won": "is_won",
}

FORECAST_HISTORY_MAPPING = {
    "Rep__c": "rep_id",
    "RepId__c": "rep_id",
    "Rep Id": "rep_id",
    "RepId": "rep_id",
    "Rep_Name__c": "rep_name",
    "Rep Name": "rep_name",
    "RepName": "rep_name",
    "Week_Of__c": "week_of",
    "Week Of": "week_of",
    "WeekOf": "week_of",
    "Commit_Amount__c": "commit_amount",
    "Commit Amount": "commit_amount",
    "CommitAmount": "commit_amount",
    "BestCase_Amount__c": "bestcase_amount",
    "Best Case Amount": "bestcase_amount",
    "BestCaseAmount": "bestcase_amount",
    "Pipeline_Amount__c": "pipeline_amount",
    "Pipeline Amount": "pipeline_amount",
    "PipelineAmount": "pipeline_amount",
}

# Columns the skills expect to see in the final file
OPPORTUNITY_REQUIRED = [
    "id", "name", "account_name", "owner_id", "owner_name",
    "amount", "stage", "probability", "forecast_category",
    "close_date", "created_date", "last_activity_date",
    "is_closed", "is_won",
]

FORECAST_HISTORY_REQUIRED = [
    "rep_id", "rep_name", "week_of",
    "commit_amount", "bestcase_amount", "pipeline_amount",
]


def detect_file_type(headers):
    """Guess whether the file is opportunities or forecast_history based on headers."""
    lower_headers = [h.lower() for h in headers]
    opp_signals = ["stagename", "stage", "amount", "closedate", "close_date", "isclosed"]
    forecast_signals = ["commit_amount", "commitamount", "commit amount", "week_of", "week of"]

    opp_score = sum(1 for s in opp_signals if any(s in h for h in lower_headers))
    forecast_score = sum(1 for s in forecast_signals if any(s in h for h in lower_headers))

    if opp_score > forecast_score:
        return "opportunities"
    elif forecast_score > opp_score:
        return "forecast_history"
    else:
        return None


def rename_headers(headers, mapping):
    """Rename headers using the mapping. Returns (new_headers, rename_log)."""
    new_headers = []
    rename_log = []
    for h in headers:
        h_stripped = h.strip()
        if h_stripped in mapping:
            new_h = mapping[h_stripped]
            if new_h != h_stripped:
                rename_log.append((h_stripped, new_h))
            new_headers.append(new_h)
        else:
            # Try case-insensitive match as fallback
            match = None
            for k, v in mapping.items():
                if k.lower() == h_stripped.lower():
                    match = v
                    break
            if match:
                if match != h_stripped:
                    rename_log.append((h_stripped, match))
                new_headers.append(match)
            else:
                new_headers.append(h_stripped)
    return new_headers, rename_log


def normalize_booleans(row, headers):
    """Convert string boolean fields to True/False strings the skills expect."""
    for field in ("is_closed", "is_won"):
        if field in headers:
            idx = headers.index(field)
            val = row[idx].strip().lower()
            if val in ("true", "1", "yes", "y"):
                row[idx] = "True"
            elif val in ("false", "0", "no", "n", ""):
                row[idx] = "False"
    return row


def normalize_dates(row, headers):
    """Convert date fields to YYYY-MM-DD format if they aren't already."""
    date_fields = ("close_date", "created_date", "last_activity_date", "week_of")
    for field in date_fields:
        if field in headers:
            idx = headers.index(field)
            val = row[idx].strip()
            if not val:
                continue
            # Already ISO format
            if len(val) == 10 and val[4] == "-" and val[7] == "-":
                continue
            # Try common alternative formats
            for fmt in ("%m/%d/%Y", "%d/%m/%Y", "%Y/%m/%d", "%m-%d-%Y"):
                try:
                    parsed = datetime.strptime(val, fmt)
                    row[idx] = parsed.strftime("%Y-%m-%d")
                    break
                except ValueError:
                    continue
    return row


def add_computed_columns(rows, headers, today=None):
    """Add days_since_last_activity if not present and last_activity_date is."""
    if today is None:
        today = date.today()
    if "last_activity_date" in headers and "days_since_last_activity" not in headers:
        headers.append("days_since_last_activity")
        idx = headers.index("last_activity_date")
        for row in rows:
            try:
                last_act = datetime.strptime(row[idx].strip(), "%Y-%m-%d").date()
                row.append(str((today - last_act).days))
            except (ValueError, IndexError):
                row.append("")
    return rows, headers


def check_required(headers, required):
    """Return list of required columns missing from the file."""
    return [r for r in required if r not in headers]


def main():
    parser = argparse.ArgumentParser(
        description="Rename Salesforce export columns to match revops-skills schema.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("file", help="path to the CSV file to rename")
    parser.add_argument(
        "--type",
        choices=["opportunities", "forecast_history", "auto"],
        default="auto",
        help="file type (auto-detected by default)",
    )
    parser.add_argument(
        "--no-backup",
        action="store_true",
        help="do not create a .bak backup before writing",
    )
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: file not found: {args.file}", file=sys.stderr)
        sys.exit(1)

    # Read the file
    with open(args.file, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        headers = next(reader)
        rows = list(reader)

    # Detect type
    file_type = args.type
    if file_type == "auto":
        file_type = detect_file_type(headers)
        if file_type is None:
            print(
                "Error: could not auto-detect file type. "
                "Use --type opportunities or --type forecast_history.",
                file=sys.stderr,
            )
            sys.exit(1)
        print(f"Auto-detected file type: {file_type}")

    # Pick mapping
    if file_type == "opportunities":
        mapping = OPPORTUNITY_MAPPING
        required = OPPORTUNITY_REQUIRED
    else:
        mapping = FORECAST_HISTORY_MAPPING
        required = FORECAST_HISTORY_REQUIRED

    # Rename headers
    new_headers, rename_log = rename_headers(headers, mapping)

    if rename_log:
        print("\nColumn renames:")
        for old, new in rename_log:
            print(f"  {old}  ->  {new}")
    else:
        print("\nNo column renames needed; headers already match.")

    # Normalize each row
    normalized_rows = []
    for row in rows:
        # Pad short rows
        if len(row) < len(new_headers):
            row = row + [""] * (len(new_headers) - len(row))
        row = normalize_booleans(row, new_headers)
        row = normalize_dates(row, new_headers)
        normalized_rows.append(row)

    # Add computed columns for opportunities
    if file_type == "opportunities":
        normalized_rows, new_headers = add_computed_columns(normalized_rows, new_headers)

    # Check required columns
    missing = check_required(new_headers, required)
    if missing:
        print(f"\nWarning: missing required columns after rename: {missing}")
        print("The skills may produce incomplete output. Check your export and the column mapping in tools/rename_columns.py.")

    # Back up the original
    if not args.no_backup:
        backup_path = args.file + ".bak"
        shutil.copy2(args.file, backup_path)
        print(f"\nBackup written to {backup_path}")

    # Write the renamed file
    with open(args.file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(new_headers)
        writer.writerows(normalized_rows)

    print(f"\nDone. Renamed {len(normalized_rows)} rows in {args.file}.")
    print(f"Headers: {', '.join(new_headers)}")


if __name__ == "__main__":
    main()
