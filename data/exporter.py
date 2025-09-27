"""
Simple export helpers to save a pandas DataFrame or a CSV file into an Excel file
at the project root (or another directory you pass). The functions keep things
beginner-friendly and prompt the user before saving.

Usage examples:

  from data.exporter import export_df_to_excel, export_csv_to_excel

  # Save an existing DataFrame
  path = export_df_to_excel(df, default_filename="grouped.xlsx")
  print(path)

  # Convert a CSV to Excel
  path = export_csv_to_excel("user-data/IIIB/UT-2/grouped.csv",
                             default_filename="UT2_grouped.xlsx")
  print(path)
"""

import os
import pandas as pd


def _ensure_xlsx(name):
    # Add .xlsx extension if user didn't include it
    if not name.lower().endswith(".xlsx"):
        return name + ".xlsx"
    return name


PROMPT_SAVE = "Do you want to save this to an Excel file? (y/n): "

def export_df_to_excel(df, default_filename="export.xlsx", project_root="."):
    """
    Ask user to confirm, then save the given DataFrame to an Excel file
    at the project root (or provided directory). Returns the full path
    that was written, or None if the user cancelled.
    """
    try:
        choice = input(PROMPT_SAVE).strip().lower()
    except Exception:
        choice = "n"
    if choice not in ("y", "yes"):  # User declined
        print("Cancelled. Not saved.")
        return None

    try:
        prompt = f"File name (press Enter for '{default_filename}'): "
        name = input(prompt).strip()
    except Exception:
        name = ""
    if name == "":
        name = default_filename
    name = _ensure_xlsx(name)

    # Build path and save
    out_path = os.path.join(project_root, name)
    try:
        # Use pandas to write to Excel
        df.to_excel(out_path, index=False)
        print("Saved Excel file:", out_path)
        return out_path
    except Exception as e:
        print("Could not save Excel file:", e)
        return None


def export_csv_to_excel(csv_path, default_filename=None, project_root="."):
    """
    Load a CSV into a DataFrame and save it to an Excel file. If default_filename
    is not provided, it is derived from the CSV name (e.g., grouped.csv -> grouped.xlsx).
    Returns the full path that was written, or None if the user cancelled or saving failed.
    """
    if not os.path.isfile(csv_path):
        print("CSV file not found:", csv_path)
        return None

    try:
        df = pd.read_csv(csv_path)
    except Exception as e:
        print("Could not read CSV:", e)
        return None

    if not default_filename:
        base = os.path.basename(csv_path)
        stem = base.rsplit(".", 1)[0]
        default_filename = stem + ".xlsx"

    return export_df_to_excel(df, default_filename=default_filename, project_root=project_root)
