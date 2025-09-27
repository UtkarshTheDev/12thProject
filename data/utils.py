# Utility functions for parsing and handling data.

import pandas as pd
import numpy as np
from pathlib import Path

def coerce_number(x):
    # This function tries to convert a value to a number (float).
    # If it's empty or invalid like "NA", it returns NaN (not a number).
    try:
        if x is None:
            return np.nan
        s = str(x).strip()
        if s == "" or s.upper() in ("NA", "N/A", "#DIV/0!", "-", "AB", "A"):
            return np.nan
        return float(s)
    except:
        return np.nan

def sanitize_for_path(name):
    # This function cleans the name for use in file paths.
    # Replaces slashes with dashes to avoid path issues.
    if not name:
        return "UNKNOWN"
    return str(name).strip().replace("/", "-").replace("\\", "-")

def find_row_with_text(df, text_to_find, max_rows=30):
    # This function searches the first 'max_rows' rows for a row containing the 'text_to_find'.
    # It returns the row number (index) if found, otherwise None.
    # This is used to locate rows like the class name or exam name.
    text_lower = text_to_find.lower()
    for i in range(min(max_rows, len(df))):
        # Get the row and convert to strings, filling empty cells with ""
        row_vals = []
        for val in df.iloc[i]:
            # Handle NaN/None before converting to string
            row_vals.append("" if pd.isna(val) else str(val))
        # Check if any cell in this row contains the text (case insensitive)
        found = False
        for v in row_vals:
            if text_lower in v.lower():
                found = True
                break
        if found:
            return i
    return None

def find_header_and_meta_rows(df):
    # This function finds the key rows: header (with RollNo, Total, etc.), class name row, exam name row.
    # The header row has columns like RollNo, subject names, Total, Percentage.
    header_row = None
    # Search first 50 rows for a row that has 'RollNo' or similar, and 'Total' or 'Per'
    for i in range(min(50, len(df))):
        row_vals = df.iloc[i].astype(str).fillna("")
        # Check for roll number variations
        has_roll = False
        for v in row_vals:
            if v.strip().lower() in ("rollno", "roll no", "roll_no"):
                has_roll = True
                break
        # Check for total
        has_total = False
        for v in row_vals:
            if v.strip().lower() == "total":
                has_total = True
                break
        # Check for percentage
        has_per = False
        for v in row_vals:
            if v.strip().lower() in ("per", "%", "percent", "percentage"):
                has_per = True
                break
        if has_roll and (has_total or has_per):
            header_row = i
            break

    # Find the row with class name, like "CLASS : IIIB"
    class_row = find_row_with_text(df, "CLASS :", 10)
    # Find the row with exam name
    exam_row = find_row_with_text(df, "NAME OF EXAMINATION", 10)
    return header_row, class_row, exam_row

def parse_exam_and_outof(df, exam_row):
    # This function extracts the exam name and the marks out of per subject.
    # For example, "UNIT TEST 2(10)" means exam is "UNIT TEST 2" and each subject is out of 10.
    exam_name = None
    per_subject_out_of = None
    if exam_row is None:
        # If no exam row found, look in first 10 rows for common exam patterns like UT-1, PT-1, etc.
        import re
        # Pattern to match exam types followed by number
        pattern = re.compile(r"^(UT|PT|TERM|HALF YEARLY|ANNUAL|SA|FA)[ -]?\d*$", re.I)
        for i in range(min(10, len(df))):
            row = df.iloc[i].fillna("").astype(str)
            for val in row:
                v = val.strip()
                if not v:
                    continue
                # If it matches the pattern, use it as exam name
                if pattern.match(v):
                    return v, None
        return exam_name, per_subject_out_of
    # Get the exam row and look for the exam name and out-of marks
    row = df.iloc[exam_row].fillna("").astype(str)
    for val in row:
        if not val or val.strip() == "" or "NAME OF EXAMINATION" in val:
            continue
        exam_name = val.strip()
        # If it has parentheses, extract the number inside as out-of marks
        if "(" in exam_name and ")" in exam_name:
            inside = exam_name[exam_name.find("(") + 1 : exam_name.find(")")].strip()
            try:
                per_subject_out_of = int(float(inside))
            except:
                per_subject_out_of = None
        break
    # Remove the parentheses part from exam name
    if exam_name and "(" in exam_name and ")" in exam_name:
        exam_name = exam_name[: exam_name.find("(")].strip()
    return exam_name, per_subject_out_of

def parse_class_name(df, class_row):
    # This function extracts the class name from the class row.
    # The row might be like: CLASS : IIIB
    # So it looks for "CLASS" and then the next non-empty cell.
    if class_row is None:
        return None
    row = []
    for val in df.iloc[class_row]:
        # Handle NaN/None before converting to string
        row.append("" if pd.isna(val) else str(val))
    # First, look for a cell starting with "CLASS"
    for idx in range(len(row)):
        val = row[idx]
        if val.strip().upper().startswith("CLASS"):
            # Find the next non-empty cell after "CLASS"
            for j in range(idx + 1, len(row)):
                if row[j].strip() != "":
                    return row[j].strip()
    # If not found that way, just take the first non-empty cell after the first one
    for val in row[1:]:
        if val.strip() != "":
            return val.strip()
    return None

def excludeRollNoAndName(df):
    # This function removes the 'Roll No' column from the dataframe if it exists.
    # It keeps only numeric columns, but drops 'Roll No' since it's not a mark.
    df_numeric = df.select_dtypes(include='number')
    if 'Roll No' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Roll No'])
    return df_numeric