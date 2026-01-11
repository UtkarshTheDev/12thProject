# Import the 'curses' library, which is used to create text-based user interfaces (TUI)
# with windows and keyboard navigation in the terminal.
import curses

# Import 'glob' for finding all the pathnames matching a specified pattern (like *.xlsx).
import glob

# Import 'os' to interact with the operating system (e.g., creating folders, joining paths).
import os

# Import 'shutil' for high-level file operations, like deleting entire directory trees.
import shutil

# Import 'sys' to access system-specific parameters and functions, like stdout or arguments.
import sys

# From the 'pathlib' library, import the 'Path' class for an object-oriented way to handle file paths.
from pathlib import Path

# Import 'matplotlib.pyplot' as 'plt' to create graphs and charts.
import matplotlib.pyplot as plt

# Import 'numpy' as 'np' for numerical calculations and handling 'Not a Number' (NaN) values.
import numpy as np

# Import 'pandas' as 'pd' to handle and analyze data in table format (DataFrames).
import pandas as pd

# From 'thefuzz', import 'process' to perform fuzzy string matching (finding similar words).
from thefuzz import process

# [[BANNER-CODE-START]]
# This section defines the visual banners shown in the terminal.
# We use triple quotes (""") for multi-line strings (ASCII art).
title = """
    ██████╗ ███████╗███████╗██╗   ██╗██╗  ████████╗     █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗██╗███████╗
    ██╔══██╗██╔════╝██╔════╝██║   ██║██║  ╚══██╔══╝    ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝██╔════╝██║██╔════╝
    ██████╔╝█████╗  ███████╗██║   ██║██║     ██║       ███████║██╔██╗ ██║███████║██║   ╚████╔╝ ███████╗██║███████╗
    ██╔══██╗██╔══╝  ╚════██║██║   ██║██║     ██║       ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝  ╚════██║██║╚════██║
    ██║  ██║███████╗███████║╚██████╔╝███████╗██║       ██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████║██║███████║
    ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝       ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝╚══════╝
"""

footer = """

    d888888P dP                         dP          dP    dP
       88    88                         88          Y8.  .8P
       88    88d888b. .d8888b. 88d888b. 88  .dP      Y8aa8P  .d8888b. dP    dP
       88    88'  `88 88'  `88 88'  `88 88888"         88    88'  `88 88    88
       88    88    88 88.  .88 88    88 88  `8b.       88    88.  .88 88.  .88
       dP    dP    dP `88888P8 dP    dP dP   `YP       dP    `88888P' `88888P'
    ooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooo

"""


# Define a function to print the big title banner.
def show_title():
    # 'print' displays the content of the 'title' variable to the terminal.
    print(title)


# Define a function to print the big footer banner.
def show_footer():
    # 'print' displays the content of the 'footer' variable to the terminal.
    print(footer)


# [[BANNER-CODE-END]]

# --- Curses compatibility check ---
# This part checks if the user's terminal supports the 'curses' library (arrow keys menu).
# We start by assuming it is NOT enabled.
CURSES_ENABLED = False
try:
    # We check if we have a standard output and if it has a file descriptor.
    # This usually fails in simple IDEs like IDLE or some VS Code setups.
    if sys.stdout and hasattr(sys.stdout, "fileno"):
        # Try to initialize the curses screen.
        stdscr = curses.initscr()
        # Immediately end it; we are just testing if it works.
        curses.endwin()
        # Clean up the variable.
        del stdscr
        # If no error happened, we can use curses!
        CURSES_ENABLED = True
    else:
        # If stdout is weird, disable curses.
        CURSES_ENABLED = False
except (curses.error, AttributeError):
    # If any error happens during initialization, we fall back to a simple text menu.
    CURSES_ENABLED = False
# --- End Curses compatibility check ---


# This function converts any value into a float (number with decimals) or NaN (Not a Number).
def coerce_number(x):
    try:
        # Convert input to a string and remove leading/trailing spaces.
        s = str(x).strip()
        # If the string represents 'empty' or 'absent' marks, treat it as Not a Number.
        if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"):
            return np.nan
        # Otherwise, try to convert the string to a decimal number.
        return float(s)
    except (ValueError, TypeError):
        # If conversion fails (e.g., trying to convert a name to a number), return NaN.
        return np.nan


# This function cleans up a string so it can be safely used as a folder or file name.
def sanitize_for_path(name):
    return (
        # Remove spaces, replace slashes with dashes to avoid breaking folder paths.
        str(name).strip().replace("/", "-").replace("\\", "-").replace(" ", "_")
        if name
        else "UNKNOWN"
    )


# This function looks for a specific piece of text within the first few rows of a table.
def find_row_with_text(df, text, max_rows=30):
    # Convert search text to lowercase for a case-insensitive match.
    text_lower = text.lower()
    # Loop through each row up to 'max_rows'.
    for i in range(min(max_rows, len(df))):
        # Check if any cell in the current row contains our search text.
        if any(text_lower in str(v).lower() for v in df.iloc[i] if not pd.isna(v)):
            return i  # Return the index of the row where we found it.
    return None  # Return None if not found.


# This function tries to find where the headers (column names like 'Roll No') are in the Excel sheet.
def find_header_and_meta_rows(df):
    header_row = None
    # Look through the first 50 rows.
    for i in range(min(50, len(df))):
        # Clean up every value in the current row to compare easily.
        row_vals = [str(v).strip().lower() for v in df.iloc[i].astype(str).fillna("")]
        # We assume a row is a header if it has "roll no" and "total" or "%".
        if any(v in ("rollno", "roll no", "roll_no") for v in row_vals) and (
            "total" in row_vals
            or any(v in ("per", "%", "percent", "percentage") for v in row_vals)
        ):
            header_row = i
            break
    # Return the header row index, and try to find where 'Class' and 'Examination' names are.
    return (
        header_row,
        find_row_with_text(df, "CLASS :", 10),
        find_row_with_text(df, "NAME OF EXAMINATION", 10),
    )


# This function extracts the exam name and what the marks are 'out of' (e.g., 100).
def parse_exam_and_outof(df, exam_row):
    if exam_row is None:
        return None, None
    # Iterate through the values in the row where we found 'NAME OF EXAMINATION'.
    for val in (str(v) for v in df.iloc[exam_row] if not pd.isna(v)):
        # Skip the label itself and find the actual name.
        if val.strip() and "NAME OF EXAMINATION" not in val:
            exam_name = val.strip()
            # If the name contains parentheses like 'Unit Test (50)', extract the '50'.
            if "(" in exam_name and ")" in exam_name:
                start, end = exam_name.find("(") + 1, exam_name.find(")")
                try:
                    per_subject_out_of = int(float(exam_name[start:end].strip()))
                except (ValueError, TypeError):
                    per_subject_out_of = None
                return exam_name[: start - 1].strip(), per_subject_out_of
            return exam_name, None
    return None, None


# This function tries to find the name of the class (e.g., '12th A') in the sheet.
def parse_class_name(df, class_row):
    if class_row is None:
        return None
    # Get all values from the row where 'CLASS :' was found.
    row = [str(v) for v in df.iloc[class_row] if not pd.isna(v)]
    for idx, val in enumerate(row):
        # Look for the word 'CLASS' and take the value immediately following it.
        if (
            val.strip().upper().startswith("CLASS")
            and idx + 1 < len(row)
            and row[idx + 1].strip()
        ):
            return row[idx + 1].strip()
    # Fallback: just return the first non-empty value after the label.
    for val in row[1:]:
        if val.strip():
            return val.strip()
    return None


# This complex function identifies which columns contain subject marks and percentages.
def detect_subject_columns(df, header_row):
    # Extract the header row as a list of strings.
    headers = [
        str(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else ""
        for v in df.iloc[header_row]
    ]
    subjects, subject_to_cols, total_col, per_col = [], {}, None, None

    # First, find where 'TOTAL' and 'PERCENTAGE' columns are.
    for ci, h in enumerate(headers):
        label = h.strip().upper()
        if label == "TOTAL":
            total_col = ci
        elif label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci

    # We stop looking for subjects once we hit the 'Total' column.
    end_ci = total_col if total_col is not None else len(headers)
    # Start looking from column 2 (assuming col 0 is Roll No, col 1 is Name).
    ci = 2 if len(headers) > 2 else 0
    while ci < end_ci:
        name = headers[ci].strip()
        # If there's a subject name here...
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            marks_col = ci
            percent_col = None
            # Check if the next column is also the same subject (could be the percentage column).
            if ci + 1 < end_ci and headers[ci + 1].strip() == name:
                percent_col = ci + 1
                ci += 2
            # Or if the next column is empty, check if it contains numbers between 0 and 100.
            elif ci + 1 < end_ci and headers[ci + 1].strip() == "":
                numeric_like = 0
                for r in range(header_row + 1, min(header_row + 11, len(df))):
                    num = coerce_number(df.iat[r, ci + 1])
                    if not np.isnan(num) and 0 <= num <= 100:
                        numeric_like += 1
                # If it looks like percentages, assign it.
                if numeric_like >= 2:
                    percent_col = ci + 1
                    ci += 2
                else:
                    ci += 1
            else:
                ci += 1
            # Add the subject and its column indices to our dictionary.
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1
    return subjects, subject_to_cols, total_col, per_col


# This function reads an Excel file and extracts all student data into a structured dictionary.
def extract_class_results(file_path, sheet_name=None):
    # Read the Excel file. We use 'dtype=object' to keep the data raw initially.
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)
    # If it read multiple sheets (returned a dict), just take the first one.
    if isinstance(df, dict):
        df = next(iter(df.values()))

    # Locate headers and metadata.
    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None:
        raise ValueError("Header row not found.")

    # Parse metadata.
    exam_name, _ = parse_exam_and_outof(df, exam_row)
    per_subject_out_of = 100  # Defaulting to 100 for percentage calculations.
    class_name = parse_class_name(df, class_row)

    # Detect which columns belong to which subjects.
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(
        df, header_row
    )

    students = []
    # Loop through every row after the header row.
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        # Try to get the Roll No from the first column.
        try:
            roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError):
            # If the first column isn't a number, it's probably not a student row.
            continue

        # Get the student's Name from the second column.
        name = (
            str(row.iloc[1]).strip()
            if len(row) > 1 and not pd.isna(row.iloc[1])
            else ""
        )

        marks, subject_percentages = {}, {}
        # For each subject we detected earlier...
        for s in subjects:
            cols = subject_to_cols[s]
            # Get the marks value from the correct column.
            marks_val = (
                coerce_number(row.iloc[cols.get("marks")])
                if cols.get("marks") is not None and cols.get("marks") < len(row)
                else np.nan
            )
            marks[s] = marks_val

            # Calculate the percentage for this subject.
            percent_val = np.nan
            if not np.isnan(marks_val):
                percent_val = round((marks_val / per_subject_out_of) * 100, 2)
            subject_percentages[s] = percent_val

        # Calculate the total marks for this student.
        valid_marks_values = [m for m in marks.values() if not np.isnan(m)]
        total = np.nansum(valid_marks_values)

        # Count how many subjects the student actually has marks for.
        num_valid_subjects = len(valid_marks_values)

        # Calculate the overall percentage for the student.
        percent = np.nan
        if num_valid_subjects > 0:
            denom = per_subject_out_of * num_valid_subjects
            if denom > 0:
                percent = round((total / denom) * 100, 2)

        # Skip rows that seem to be empty.
        if not name and all(np.isnan(v) for v in marks.values()):
            continue

        # Add the student's data to our list.
        students.append(
            {
                "roll_no": roll_no,
                "name": name,
                "marks": marks,
                "subject_percentages": subject_percentages,
                "total": total,
                "percentage": percent,
            }
        )

    # Wrap everything into a result dictionary.
    result = {
        "class_name": class_name,
        "exam_name": exam_name,
        "subjects": subjects,
        "per_subject_out_of": per_subject_out_of,
        "students": students,
    }
    # Calculate the maximum possible total marks.
    if per_subject_out_of and subjects:
        num_subjects = len(subjects)
        result["total_out_of"] = per_subject_out_of * num_subjects
    return result


# This function converts the nested dictionary of results into two flat Pandas DataFrames.
def results_to_dfs(parsed):
    subjects = parsed.get("subjects", [])
    rows_r, rows_p = [], []
    # For each student in the list...
    for s in parsed.get("students", []):
        # Create a base dictionary with Roll No and Name.
        base = {"Roll No": s.get("roll_no"), "Name": s.get("name", "")}
        # Copy the base for marks (rows_r) and percentages (rows_p).
        row_r, row_p = base.copy(), base.copy()
        # Add marks/percentages for each subject as new keys.
        for subj in subjects:
            row_r[f"{subj}_Marks"] = s.get("marks", {}).get(subj)
            row_p[f"{subj}_%"] = s.get("subject_percentages", {}).get(subj)
        # Add the grand total and overall percentage.
        row_r["Total"], row_r["Percentage"] = s.get("total"), s.get("percentage")
        row_p["Overall_Percentage"] = s.get("percentage")
        # Add these flat dictionaries to our lists.
        rows_r.append(row_r)
        rows_p.append(row_p)
    # Convert lists of dictionaries into Pandas DataFrames.
    return pd.DataFrame(rows_r), pd.DataFrame(rows_p)


# This function handles saving the parsed data into CSV files inside organized folders.
def save_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    # Extract the data.
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    # Create a path like user-data/Class_12/Final_Exam.
    out_dir = (
        Path(base_dir)
        / sanitize_for_path(parsed.get("class_name"))
        / sanitize_for_path(parsed.get("exam_name"))
    )
    # Ensure all folders in the path exist (mkdir -p).
    out_dir.mkdir(parents=True, exist_ok=True)
    # Get the DataFrames.
    df_r, df_p = results_to_dfs(parsed)
    # Save them as CSV files.
    df_r.to_csv(out_dir / "result.csv", index=False)
    df_p.to_csv(out_dir / "percentage.csv", index=False)
    return out_dir


# This function asks the user if they want to export a table to a real Excel file.
def export_df_to_excel(df, fname="export.xlsx"):
    if input("    Save to Excel? (y/n): ").strip().lower() in ("y", "yes"):
        # Get the filename from the user.
        name = input(f"    Filename ('{fname}'): ").strip() or fname
        # Ensure it has the .xlsx extension.
        out_path = name if name.lower().endswith(".xlsx") else name + ".xlsx"
        try:
            # Use Pandas to write the Excel file.
            df.to_excel(out_path, index=False)
            print("    Saved:", out_path)
            return out_path
        except Exception as e:
            print("    Error:", e)
    return None


# This function prints a DataFrame in a nice, aligned table format in the terminal.
def display_df(df, title):
    # Create a copy to avoid modifying the original data.
    df_display = df.copy()

    # Convert decimal numbers to integers for cleaner display.
    for col in df_display.select_dtypes(include=["float64"]).columns:
        df_display[col] = df_display[col].apply(
            lambda x: str(int(round(x))) if pd.notna(x) else ""
        )

    # Ensure everything is a string so we can measure its length.
    for col in df_display.columns:
        df_display[col] = df_display[col].astype(str)

    # Find the widest value in each column to set column widths.
    col_widths = {
        col: max(len(col), df_display[col].str.len().max())
        for col in df_display.columns
    }

    # Create the top row (headers).
    header = " | ".join(
        f"{col.upper():<{col_widths[col]}}" for col in df_display.columns
    )
    # Create the separator line (---).
    separator = "-+-".join("-" * col_widths[col] for col in df_display.columns)

    # Print the title and table borders.
    table_width = len(header)
    print(f"\n    {title.upper().center(table_width)}")
    print(f"    {'=' * table_width}")

    # Print headers and separator.
    print(f"    {header}")
    print(f"    {separator}")

    # Print each student's data as a row.
    for _, row in df_display.iterrows():
        row_str = " | ".join(
            f"{row[col]:<{col_widths[col]}}" for col in df_display.columns
        )
        print(f"    {row_str}")

    # Print the bottom border.
    print(f"    {'=' * table_width}\n")


# Curses function to draw a menu on the screen.
def draw_menu(stdscr, title, opts, idx, help_text):
    stdscr.clear()  # Clear the terminal screen.
    stdscr.addstr(1, 2, title)  # Draw the title at row 1, col 2.
    stdscr.addstr(2, 2, help_text)  # Draw help text at row 2, col 2.
    for i, opt in enumerate(opts):
        # Draw each option. If it's the selected one, show a '>' arrow.
        stdscr.addstr(4 + i, 2, f" {'>' if i == idx else ' '} {opt}")
    stdscr.refresh()  # Update the physical screen.


# Curses function to let the user select an item using arrow keys.
def select_from_list(stdscr, title, opts, help_text):
    idx = 0  # Currently selected option index.
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()  # Wait for a key press.
        # Handle Up/K (move selection up).
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(opts)
        # Handle Down/J (move selection down).
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(opts)
        # Handle Enter (select current item).
        elif key in (curses.KEY_ENTER, 10, 13):
            return opts[idx]
        # Handle Q (quit/cancel).
        elif key in (ord("q"), ord("Q")):
            return None


# Curses function that also allows deleting an item with the 'd' key.
def select_with_delete(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13):
            return opts[idx], "select"
        elif key in (ord("d"), ord("D")):
            return opts[idx], "delete"
        elif key in (ord("q"), ord("Q")):
            return None, None


# Simple text-based menu for terminals that don't support curses.
def select_from_list_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    # Just print the list with numbers.
    for i, opt in enumerate(opts):
        print(f"    {i + 1}. {opt}")
    print(f"    (Enter 'q' to quit)")

    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == "q":
            return None
        try:
            # User types a number (1, 2, 3...)
            idx = int(choice) - 1
            if 0 <= idx < len(opts):
                return opts[idx]
            else:
                print("    Invalid number. Please try again.")
        except ValueError:
            print("    Please enter a number.")


# Simple text-based menu with delete capability.
def select_with_delete_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i + 1}. {opt}")
    print("    (Enter 'd<number>' to delete, e.g., 'd1')")
    print(f"    (Enter 'q' to quit)")

    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == "q":
            return None, None

        action = "select"
        item_choice = choice
        # If input starts with 'd', it's a delete request.
        if choice.startswith("d") and len(choice) > 1:
            action = "delete"
            item_choice = choice[1:]

        try:
            idx = int(item_choice) - 1
            if 0 <= idx < len(opts):
                return opts[idx], action
            else:
                print("    Invalid number. Please try again.")
        except ValueError:
            print("    Please enter a valid number or command.")


# This function searches for Excel files using partial/fuzzy matching in the terminal.
def fuzzy_search_file_select_no_curses():
    search_term = ""
    while True:
        search_term = input(
            "\n    Enter search term to find Excel file (or 'q' to quit): "
        ).strip()
        if not search_term or search_term.lower() == "q":
            return None

        # Find all .xlsx files in current and sub-folders.
        all_files = glob.glob("**/*.xlsx", recursive=True)
        if not all_files:
            print(
                "    No .xlsx files found in the current directory or subdirectories."
            )
            continue

        # Use 'thefuzz' to find files that match the search term.
        matches = process.extract(search_term, all_files, limit=10)
        # Only keep matches with a score better than 30.
        search_results = [match[0] for match in matches if match[1] > 30]

        if not search_results:
            print("    No matches found.")
            continue

        # Show the results for selection.
        print("\n    --- Select a File ---")
        for i, file_path in enumerate(search_results):
            print(f"    {i + 1}. {file_path}")

        choice = input("    Select a number (or 'r' to research): ").strip().lower()
        if choice == "r":
            continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(search_results):
                return search_results[idx]
            else:
                print("    Invalid number.")
        except ValueError:
            print("    Invalid input.")


# Function to navigate the 'user-data' folder and pick a specific class and exam.
def select_class_exam(base_dir="user-data"):
    # List all folders in user-data (each folder is a Class).
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )
    if not classes:
        return None, None

    # Pick a class.
    if CURSES_ENABLED:
        s_class = curses.wrapper(
            select_from_list, "Select Class", classes, "Up/Down, Enter, q to quit."
        )
    else:
        s_class = select_from_list_no_curses(
            "Select Class", classes, "Up/Down, Enter, q to quit."
        )

    if not s_class:
        return None, None

    # List all subfolders in the class folder (each subfolder is an Exam).
    exams = sorted(
        [
            d
            for d in os.listdir(os.path.join(base_dir, s_class))
            if os.path.isdir(os.path.join(base_dir, s_class, d))
        ]
    )
    if not exams:
        return None, None

    # Pick an exam.
    if CURSES_ENABLED:
        s_exam = curses.wrapper(
            select_from_list, f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )
    else:
        s_exam = select_from_list_no_curses(
            f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )

    return s_class, s_exam


# Statistical function to count how many students fall into percentage brackets (e.g., 90-100%).
def group_by_percent(csv_path):
    # Read the percentage data.
    df = pd.read_csv(csv_path)
    user_input = input("    Custom grouping (e.g., 90,80,33) or Enter for default: ")
    # Create the thresholds (e.g., [100, 90, 80...]).
    thresholds = sorted(
        [int(t) for t in user_input.split(",")]
        if user_input
        else [90, 80, 70, 60, 50, 40, 33],
        reverse=True,
    )
    if 100 not in thresholds:
        thresholds.insert(0, 100)

    # Create brackets like [[91, 100], [81, 90]...].
    grouping = [
        [(thresholds[i + 1] + 1 if i + 1 < len(thresholds) else 0), thresholds[i]]
        for i in range(len(thresholds))
    ]
    # Identify which columns are subject percentages.
    subjects = [
        c[:-2] for c in df.columns if c.endswith("_%") and c != "Overall_Percentage"
    ]
    summary = []
    for subj in subjects:
        # Helper function to find which bracket a score belongs to.
        def get_group(score):
            if pd.isna(score):
                return "N/A"
            for low, high in grouping:
                if low <= score <= high:
                    return f"{low}-{high}"
            return "Other"

        # Apply the grouping to the subject column and count occurrences.
        summary.append(
            {
                "Subject": subj,
                **df[f"{subj}_%"].apply(get_group).value_counts().to_dict(),
            }
        )
    # Convert result to a summary DataFrame.
    summary_df = pd.DataFrame(summary).fillna(0)
    display_df(summary_df, "Grouped Summary (counts)")
    return df, summary_df


# Function to draw charts using Matplotlib.
def plot_chart(df, x, y, title, xl, yl, kind="bar", rot=45, figsize=(12, 6), **kwargs):
    plt.figure(figsize=figsize)
    # Choose chart type based on 'kind' argument.
    if kind == "bar":
        plt.bar(df[x], df[y], **kwargs)
    elif kind == "line":
        plt.plot(df[x], df[y], marker="o", **kwargs)
    elif kind == "scatter":
        plt.scatter(df[x], df[y], **kwargs)

    # Add labels and title.
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xl, fontsize=12)
    plt.ylabel(yl, fontsize=12)
    # Rotate student names on the X-axis so they don't overlap.
    plt.xticks(rotation=rot, ha="right")
    # Set Y-axis scale from 0 to 100%.
    plt.ylim(0, 100)
    # Add subtle grid lines.
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()  # Pop up the graph window.


# Interactive Curses version of fuzzy file search.
def fuzzy_search_file_select(stdscr):
    search_term = ""
    selected_index = 0
    all_files = glob.glob("**/*.xlsx", recursive=True)
    search_results = []

    # Enable cursor and disable non-blocking mode.
    curses.curs_set(1)
    stdscr.nodelay(0)

    while True:
        stdscr.clear()

        # Display Title and Search Prompt.
        stdscr.addstr(1, 2, "Search for an Excel File")
        stdscr.addstr(
            2, 2, "Type to search, Up/Down to navigate, Enter to select, 'q' to quit."
        )
        stdscr.addstr(4, 4, f"Search: {search_term}")

        # Live search as the user types.
        if search_term:
            matches = process.extract(search_term, all_files, limit=10)
            search_results = [match for match in matches if match[1] > 30]
        else:
            search_results = []

        # Draw the search results.
        if search_results:
            display_line = 6
            for i, (file_path, score) in enumerate(search_results):
                filename = os.path.basename(file_path)
                display_text = f"{filename} ({score}%)"

                # Highlight the selected result.
                if i == selected_index:
                    stdscr.addstr(
                        display_line, 2, f"> {display_text}", curses.A_REVERSE
                    )
                else:
                    stdscr.addstr(display_line, 2, f"  {display_text}")
                display_line += 1
                stdscr.addstr(
                    display_line, 6, f"Path: {file_path}"
                )  # Show file location.
                display_line += 2
        elif search_term:
            stdscr.addstr(6, 2, "  No matches found.")

        # Keep the text cursor at the end of the search input string.
        stdscr.move(4, 12 + len(search_term))
        stdscr.refresh()

        key = stdscr.getch()

        # Logic for key presses: Enter to confirm, Arrow keys to move, Backspace to edit.
        if key in (curses.KEY_ENTER, 10, 13):
            if search_results:
                return search_results[selected_index][0]
        elif key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(search_results) - 1, selected_index + 1)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            search_term = search_term[:-1]
            selected_index = 0
        elif key in (ord("q"), ord("Q"), 27):  # Escape key or 'q'.
            return None
        elif 32 <= key <= 126:  # Normal typing (letters/numbers).
            search_term += chr(key)
            selected_index = 0


# Main flow for uploading and processing a new Excel file.
def upload_pipeline():
    if CURSES_ENABLED:
        fpath = curses.wrapper(fuzzy_search_file_select)
    else:
        fpath = fuzzy_search_file_select_no_curses()

    if not fpath:
        print("    File selection cancelled.")
        return

    print(f"    Selected file: {fpath}")

    try:
        # Check if the Excel file has multiple sheets.
        sheets = pd.ExcelFile(fpath).sheet_names
        print("    Sheets:", ", ".join(sheets))
        # Ask which sheet to process.
        sheet = input("    Sheet name (Enter for first): ").strip() or 0
        s_dir = "user-data"
        print("    Class data stored on the user-data folder")
        # Run the extraction and save logic.
        out = save_results_to_csv(fpath, sheet_name=sheet, base_dir=s_dir)
        print(f"    Saved to: {out}")
    except Exception as e:
        print(f"    Error: {e}")


# Interactive flow for grouping data.
def group_by_percent_interactive():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    path = os.path.join("user-data", s_class, s_exam, "percentage.csv")
    if not os.path.isfile(path):
        print(f"    'percentage.csv' not found for {s_class} - {s_exam}.")
        return
    # Calculate grouping.
    _, summary_df = group_by_percent(path)
    if not summary_df.empty:
        # Save the grouping results to a new CSV and offer Excel export.
        (Path(path).parent / "grouped.csv").write_text(summary_df.to_csv(index=False))
        export_df_to_excel(summary_df, fname="grouped.xlsx")


# Flow for viewing existing data in the terminal.
def view_data_flow():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    base_path = os.path.join("user-data", s_class, s_exam)
    opts = ["Percentage", "Grouped", "Full Result", "All"]

    # Ask the user what exactly they want to see.
    if CURSES_ENABLED:
        dtype = curses.wrapper(
            select_from_list, "Select Data to View", opts, "Up/Down, Enter, q to quit."
        )
    else:
        dtype = select_from_list_no_curses(
            "Select Data to View", opts, "Up/Down, Enter, q to quit."
        )

    if not dtype:
        return

    # Mapping of user choice to file names.
    files = {
        "Percentage": ["percentage.csv"],
        "Grouped": ["grouped.csv"],
        "Full Result": ["result.csv"],
        "All": ["percentage.csv", "result.csv", "grouped.csv"],
    }
    for f in files.get(dtype, []):
        fpath = os.path.join(base_path, f)
        if os.path.isfile(fpath):
            # Read and print the CSV as a table.
            display_df(pd.read_csv(fpath), f.replace(".csv", " Data").title())
        else:
            print(f"    {f} not available.")


# Flow for generating graphs.
def plot_graphs_flow(base_dir="user-data"):
    c_name, e_name = select_class_exam(base_dir)
    if not (c_name and e_name):
        return

    opts = ["Bar Chart", "Line Chart", "Scatter Plot"]
    if CURSES_ENABLED:
        g_type = curses.wrapper(
            select_from_list, "Select Graph Type", opts, "Up/Down, Enter, q to quit."
        )
    else:
        g_type = select_from_list_no_curses(
            "Select Graph Type", opts, "Up/Down, Enter, q to quit."
        )

    if not g_type:
        return

    csv_path = os.path.join(base_dir, c_name, e_name, "percentage.csv")
    if not os.path.isfile(csv_path):
        print(f"    percentage.csv not found for {c_name} - {e_name}")
        return

    df = pd.read_csv(csv_path)
    title = f"{g_type} - {c_name} - {e_name}"
    # Route to the plotting function with correct labels.
    if "Bar" in g_type:
        plot_chart(
            df,
            "Name",
            "Overall_Percentage",
            title,
            "Students",
            "Percentage (%)",
            kind="bar",
        )
    elif "Line" in g_type:
        plot_chart(
            df,
            "Name",
            "Overall_Percentage",
            title,
            "Students",
            "Percentage (%)",
            kind="line",
        )
    elif "Scatter" in g_type:
        plot_chart(
            df,
            "Roll No",
            "Overall_Percentage",
            title,
            "Roll Number",
            "Percentage (%)",
            kind="scatter",
        )


# Flow for deleting processed data.
def delete_data_flow(base_dir="user-data"):
    # List all folders in the base directory (each folder represents a Class).
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )

    # Note: Added a small safety check here in the commented version for clarity.
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )
    if not classes:
        print("    No classes found.")
        return

    # Select which class to deal with.
    if CURSES_ENABLED:
        selected_class, action = curses.wrapper(
            select_with_delete,
            "Select Class",
            classes,
            "Up/Down, Enter to view exams, d to delete class, q to quit.",
        )
    else:
        selected_class, action = select_with_delete_no_curses(
            "Select Class",
            classes,
            "Up/Down, Enter to view exams, d to delete class, q to quit.",
        )

    if not selected_class:
        return

    # If user pressed 'd', delete the whole class folder.
    if action == "delete":
        confirm = (
            input(
                f"    Are you sure you want to permanently delete all data for class '{selected_class}'? [y/N]: "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            try:
                shutil.rmtree(os.path.join(base_dir, selected_class))
                print(f"    Successfully deleted class '{selected_class}'.")
            except Exception as e:
                print(f"    Error deleting class '{selected_class}': {e}")
        else:
            print("    Deletion cancelled.")
        return

    # If user pressed 'Enter', show exams within that class.
    class_path = os.path.join(base_dir, selected_class)
    exams = sorted(
        [
            d
            for d in os.listdir(class_path)
            if os.path.isdir(os.path.join(class_path, d))
        ]
    )
    if not exams:
        print(f"    No exams found for class '{selected_class}'.")
        return

    if CURSES_ENABLED:
        selected_exam, action = curses.wrapper(
            select_with_delete,
            f"Exams for {selected_class}",
            exams,
            "Up/Down, d to delete exam, q to quit.",
        )
    else:
        selected_exam, action = select_with_delete_no_curses(
            f"Exams for {selected_class}",
            exams,
            "Up/Down, d to delete exam, q to quit.",
        )

    if not selected_exam:
        return

    # If user pressed 'd', delete just that specific exam folder.
    if action == "delete":
        confirm = (
            input(
                f"    Are you sure you want to permanently delete exam '{selected_exam}' for class '{selected_class}'? [y/N]: "
            )
            .strip()
            .lower()
        )
        if confirm == "y":
            try:
                shutil.rmtree(os.path.join(class_path, selected_exam))
                print(
                    f"    Successfully deleted exam '{selected_exam}' for class '{selected_class}'."
                )
            except Exception as e:
                print(f"    Error deleting exam '{selected_exam}': {e}")
        else:
            print("    Deletion cancelled.")


# The main entry point of the program.
def main():
    # Show the initial banner.
    # [[BANNER-CODE-START]]
    show_title()
    # [[BANNER-CODE-END]]

    # Ensure the storage directory exists.
    if not os.path.exists("user-data"):
        os.makedirs("user-data")

    # Mapping of menu numbers to the functions they trigger.
    actions = {
        "1": upload_pipeline,
        "2": group_by_percent_interactive,
        "3": view_data_flow,
        "4": plot_graphs_flow,
        "5": delete_data_flow,
    }

    # The ASCII-styled Main Menu.
    menu_text = (
        "\n"
        "    +---------------------------------------+\n"
        "    |               MAIN MENU               |\n"
        "    +---------------------------------------+\n"
        "    | 1. Upload New Excel File              |\n"
        "    | 2. Group Data by Percentage           |\n"
        "    | 3. View Class/Exam Data               |\n"
        "    | 4. Plot Graphs                        |\n"
        "    | 5. Delete Data                        |\n"
        "    +---------------------------------------+\n"
        "    | clear - Clear Screen                  |\n"
        "    | q     - Quit                          |\n"
        "    +---------------------------------------+"
    )

    try:
        # Loop until the user chooses to quit.
        while True:
            print(menu_text)
            choice = input("\n    Enter your choice: ").strip().lower()
            if choice in actions:
                # Call the mapped function.
                actions[choice]()
            elif choice == "clear":
                # Clear terminal screen (cls for Windows, clear for Linux/Mac).
                os.system("cls" if os.name == "nt" else "clear")
                # Show title again after clearing.
                # [[BANNER-CODE-START]]
                show_title()
                # [[BANNER-CODE-END]]
            elif choice in ("q", "quit"):
                # Exit the loop.
                break
            else:
                print("    Invalid choice. Please try again.")
    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully.
        print("\n    Operation cancelled by user.")
        pass
    finally:
        # Always show the footer before exiting.
        # [[BANNER-CODE-START]]
        show_footer()
        # [[BANNER-CODE-END]]


# This standard block ensures the main() function only runs if the script is executed directly,
# not if it is imported as a module in another script.
if __name__ == "__main__":
    main()
