# Functions for saving parsed data to CSV files.

import pandas as pd
from pathlib import Path

from .parser import extract_class_results
from .utils import sanitize_for_path

def results_to_dataframes(parsed):
    # This function creates two dataframes from the parsed results.
    # One for full results (marks, totals), one for percentages only.
    subjects = parsed.get("subjects", [])
    rows_result = []
    rows_percent = []
    for s in parsed.get("students", []):
        # Base columns: Roll No and Name
        base = {"Roll No": s.get("roll_no"), "Name": s.get("name") or ""}
        row_r = base.copy()  # For result.csv
        row_p = base.copy()  # For percentage.csv
        marks = s.get("marks", {})
        subj_perc = s.get("subject_percentages", {})
        for subj in subjects:
            row_r[f"{subj}_Marks"] = marks.get(subj)  # Like Math_Marks
            row_r[f"{subj}_%"] = subj_perc.get(subj)  # Like Math_%
            row_p[f"{subj}_%"] = subj_perc.get(subj)  # Only percentages
        row_r["Total"] = s.get("total")
        row_r["Percentage"] = s.get("percentage")
        row_p["Overall_Percentage"] = s.get("percentage")
        rows_result.append(row_r)
        rows_percent.append(row_p)

    result_df = pd.DataFrame(rows_result)
    percentage_df = pd.DataFrame(rows_percent)
    return result_df, percentage_df

def save_class_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    # This function parses the Excel and saves two CSV files.
    # One with all results, one with percentages.
    # Saves in a folder like user-data/ClassName/ExamName/
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    class_dir = sanitize_for_path(parsed.get("class_name"))
    exam_dir = sanitize_for_path(parsed.get("exam_name"))
    out_dir = Path(base_dir) / class_dir / exam_dir
    out_dir.mkdir(parents=True, exist_ok=True)  # Create directories if needed

    result_df, percentage_df = results_to_dataframes(parsed)

    result_csv = out_dir / "result.csv"
    percentage_csv = out_dir / "percentage.csv"
    result_df.to_csv(result_csv, index=False)  # Save without row indices
    percentage_df.to_csv(percentage_csv, index=False)
    return out_dir

def save_and_report(file_path, sheet_name=None, base_dir="user-data"):
    # This function saves the CSVs and prints where they were saved.
    out_dir = save_class_results_to_csv(file_path, sheet_name=sheet_name, base_dir=base_dir)
    print(f"Saved/updated CSVs in: {out_dir}")


def save_grouped_csv_for_source(source_csv_path, grouped_df):
    """
    Save the grouped summary DataFrame as grouped.csv in the same folder
    where the source CSV (e.g., percentage.csv) resides.
    Returns the written Path.
    """
    out_dir = Path(source_csv_path).parent
    out_path = out_dir / "grouped.csv"
    grouped_df.to_csv(out_path, index=False)
    return out_path