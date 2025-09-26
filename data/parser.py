# Functions for parsing Excel data into structured results.

import pandas as pd
import numpy as np

from .utils import (
    find_header_and_meta_rows,
    parse_exam_and_outof,
    parse_class_name,
    coerce_number,
)
from .subjects import detect_subject_columns

def extractDataFromExcel(file_path, sheet_name=None):
    # This function reads the Excel file without assuming any headers.
    # It reads all data as objects so we can parse it manually later.
    return pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)

def extract_class_results(file_path, sheet_name=None):
    # This is the main function to parse the Excel sheet for class results.
    # It reads the file, finds the important rows, extracts class name, exam name, subjects,
    # and then for each student: roll number, name, marks per subject, total, percentage.
    # If total or percentage is missing, it calculates them.
    df = extractDataFromExcel(file_path, sheet_name=sheet_name)
    if isinstance(df, dict):
        df = next(iter(df.values()))  # If multiple sheets, take the first one

    # Find the key rows: header, class, exam
    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None:
        raise ValueError("Could not locate header row with RollNo/Total/Per")

    # Get exam name and marks out of per subject
    exam_name, per_subject_out_of = parse_exam_and_outof(df, exam_row)
    if not per_subject_out_of:
        per_subject_out_of = 100  # Default if not found
    # Get class name
    class_name = parse_class_name(df, class_row)
    # Figure out subject columns
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(df, header_row)

    # Columns: 0 is roll, 1 is name
    roll_col = 0
    name_col = 1 if df.shape[1] > 1 else None

    students = []
    # Loop through rows after header
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        roll_val = row.iloc[roll_col]
        try:
            roll_no = int(float(str(roll_val)))  # Convert roll to integer
        except:
            continue  # Skip if not a valid roll number

        name_val = None
        if name_col is not None:
            nv = row.iloc[name_col]
            if not (pd.isna(nv) or str(nv).strip() == ""):
                name_val = str(nv).strip()

        # Get marks and percentages for each subject
        marks = {}
        subject_percents = {}
        for subj in subjects:
            cols = subject_to_cols[subj]
            mci = cols.get("marks")  # Column index for marks
            pci = cols.get("percent")  # Column index for percent
            mval = coerce_number(row.iloc[mci]) if mci is not None else np.nan
            pval = coerce_number(row.iloc[pci]) if (pci is not None and pci < len(row)) else np.nan
            marks[subj] = mval
            subject_percents[subj] = pval

        # Get total and percentage from columns if present
        total = coerce_number(row.iloc[total_col]) if total_col is not None else np.nan
        percent = coerce_number(row.iloc[per_col]) if per_col is not None else np.nan

        # If total is missing, sum the marks
        if np.isnan(total):
            total = float(np.nansum(list(marks.values())))
        # If percentage is missing, calculate it: (total / (out_of * num_subjects)) * 100
        if np.isnan(percent):
            if per_subject_out_of and per_subject_out_of > 0 and len(subjects) > 0:
                denom = per_subject_out_of * len(subjects)
                if denom > 0:
                    percent = round((total / denom) * 100, 2)
            else:
                percent = np.nan

        # Skip empty rows
        if (name_val is None or name_val == "") and all(np.isnan(v) for v in marks.values()):
            continue

        # Add student data
        students.append({
            "roll_no": roll_no,
            "name": name_val,
            "marks": marks,  # Dict of subject: mark
            "subject_percentages": subject_percents,  # Dict of subject: percent
            "total": total,
            "percentage": percent,
        })

    # Prepare the result dictionary
    result = {
        "class_name": class_name,
        "exam_name": exam_name,
        "subjects": subjects,  # List of subject names
        "per_subject_out_of": per_subject_out_of,  # Marks per subject
        "students": students,  # List of student dicts
    }
    if per_subject_out_of and len(subjects) > 0:
        result["total_out_of"] = per_subject_out_of * len(subjects)  # Total possible marks
    return result