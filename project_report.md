## Project Title
Student Result Analysis and Visualization

## Project Overview
This project is a command-line application designed to automate the process of analyzing student academic performance. It reads student marks from Excel files, processes the data to calculate totals and percentages, and provides features for viewing, grouping, and visualizing the results. The main purpose is to provide an efficient tool for teachers and administrators to get insights into student performance for a class after an examination, without needing to manually calculate or format the data. Its real-world use is in schools and educational institutions where tracking and analyzing student results is a regular activity.

## Objectives of the Project
*   To parse student result data from unstructured Excel files automatically.
*   To calculate total marks and percentages for each student.
*   To save the processed data into clean, structured CSV files for future use.
*   To provide a user-friendly menu to view the processed data in different formats.
*   To group students based on their percentage scores to identify performance bands.
*   To generate various graphs and charts to visualize student performance.

## Scope of the Project
The project can currently process Excel files to extract student marks, given that the file contains some common keywords like "RollNo", "Total", and "CLASS". It provides a text-based interface for all its operations. The visualizations are displayed as separate windows using the `matplotlib` library. The scope is limited to a local machine and does not have web or network capabilities. Future enhancements could expand its capabilities to handle more data formats and provide more advanced analytics.

## Advantages of the Project
*   **Automation:** It automates the tedious task of manually entering and calculating student marks.
*   **Data Visualization:** It provides multiple types of charts, making it easy to understand performance trends.
*   **Flexibility:** The parser is designed to work even if the Excel sheet format is not strictly fixed.
*   **Data Management:** It organizes the processed data neatly into folders for each class and exam.
*   **Extensibility:** The modular structure of the code makes it easy to add new features or graph types in the future.
*   **User-Friendly:** The menu-driven interface is simple to navigate for non-technical users.

## Theoretical Background
### Python Programming Language
Python is a high-level, interpreted programming language known for its simple and readable syntax. It is an excellent choice for this project due to its extensive standard library and a rich ecosystem of third-party packages for data science and analysis. Libraries like `pandas` for data manipulation and `matplotlib` for plotting are powerful tools that make complex tasks like data processing and visualization straightforward. Python's cross-platform nature also ensures that the project can run on different operating systems like Windows, macOS, and Linux without modification.

### Libraries and Modules Used
*   **pandas:** A powerful library for data manipulation and analysis. It is used to read data from Excel files, process it, and store it in a structured format called a DataFrame.
*   **matplotlib:** A comprehensive library for creating static, animated, and interactive visualizations in Python. It is used to generate all the graphs and charts in this project, such as bar charts, line charts, and pie charts.
*   **numpy:** A fundamental package for scientific computing with Python. It is used for numerical operations, especially for handling missing values (`NaN`) and performing calculations.
*   **openpyxl:** A Python library to read/write Excel 2010 xlsx/xlsm/xltx/xltm files. It is used by `pandas` under the hood to interact with the Excel files.
*   **thefuzz:** A library for fuzzy string matching. It is used in the file search feature to find Excel files even if the user's search term is not an exact match.
*   **curses:** A library for creating text-based user interfaces (TUI) in the terminal. It is used to create interactive menus with arrow-key navigation.
*   **os, sys, shutil, glob, pathlib:** These are built-in Python modules used for interacting with the operating system, such as handling files and directories, managing system paths, and finding files matching a specific pattern.

## System Requirements
### Hardware Requirements
*   **Processor:** Intel Core i3 or equivalent
*   **RAM:** 4 GB
*   **Hard Disk:** 500 MB of free space

### Software Requirements
*   **Operating System:** Windows 10, macOS, or a modern Linux distribution
*   **Python:** Version 3.6 or higher
*   **Editor:** Any text editor like VS Code, Sublime Text, or IDLE
*   **Libraries:** `pandas`, `matplotlib`, `numpy`, `openpyxl`, `thefuzz`

## Project Design / Working
The project works in a step-by-step manner, guided by a main menu.

1.  **Main Menu (`index.py`):** When the program starts, it displays a menu with options to upload data, view grouped marks, view all data, or plot graphs.

2.  **Data Upload (`data/handler.py`):**
    *   The user selects the "Upload Excel data" option.
    *   The program prompts the user for the path to the Excel file and the sheet name.
    *   The `data/parser.py` module reads the Excel file. It intelligently finds the header row (containing "RollNo", "Total", etc.), the class name, and the exam name.
    *   The `data/subjects.py` module helps in identifying the columns that represent subjects.
    *   It then iterates through each student row, extracts their marks, and calculates the total and percentage if they are not already present.
    *   The processed data is then saved into two CSV files (`result.csv` and `percentage.csv`) inside a structured folder path like `user-data/CLASS_NAME/EXAM_NAME/`.

3.  **Viewing and Grouping Data:**
    *   The user can choose to view the saved data. The `ui/view_data.py` script provides a menu to select the class and exam, and then shows the data in a formatted table in the console.
    *   The "Group by Percentage" feature (`group/ByPercent.py`) reads the `percentage.csv` file, and groups students into percentage bands (e.g., 90-100%, 80-89%, etc.). It then displays a summary count of how many students fall into each band for each subject.

4.  **Plotting Graphs (`graphs/plot_data.py`):**
    *   The user selects the "Plot graphs" option.
    *   A menu (`graphs/select_graph.py`) allows the user to choose a class, an exam, and a type of graph (e.g., Bar Chart, Line Chart).
    *   The `graphs/plotter.py` module then reads the corresponding `percentage.csv` file and uses `matplotlib` to generate and display the selected graph in a new window.

The entire workflow is designed to be modular, with different files and modules handling specific tasks like parsing, saving, plotting, and user interface.

## Code Explanation (High-Level)
*   **`index.py`:** This is the main entry point of the application. It displays the main menu and calls functions from other modules based on the user's choice.
*   **`data/handler.py`:** This file orchestrates the data processing pipeline. It takes the file path from the user and calls the parser, printer, and saver modules in sequence.
*   **`data/parser.py`:** This is the core logic for reading and understanding the Excel file. The `extract_class_results` function is the most important one here, as it finds all the necessary data points from the sheet.
*   **`data/saver.py`:** This module is responsible for converting the parsed data into `pandas` DataFrames and saving them to CSV files.
*   **`graphs/plotter.py`:** This file contains a set of functions for creating different types of plots. Each function takes the path to a CSV file and uses `matplotlib` to generate a specific chart.
*   **`group/ByPercent.py`:** This module contains the logic for the "Group by Percentage" feature. It reads a `percentage.csv` file, categorizes students into performance bands, and prints a summary table.
*   **`ui/select_data.py`:** This provides a reusable text-based user interface component for selecting a class and exam using arrow keys.
*   **`merged_script.py`:** This is a single, standalone script that contains all the functionality of the entire project. It is useful for distribution or for running the project without managing multiple files.

## Complete Project Code
```python
# File: /home/utkarsh/development/12thProject/merged_script.py
import os, sys, shutil, curses, glob
from thefuzz import process
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# [[BANNER-CODE-START]]
# This section contains the title and footer banners.
title = '''
    ██████╗ ███████╗███████╗██╗   ██╗██╗  ████████╗     █████╗ ███╗   ██╗ █████╗ ██╗  ██╗   ██╗███████╗██╗███████╗
    ██╔══██╗██╔════╝██╔════╝██║   ██║██║  ╚══██╔══╝    ██╔══██╗████╗  ██║██╔══██╗██║  ╚██╗ ██╔╝██╔════╝██║██╔════╝
    ██████╔╝█████╗  ███████╗██║   ██║██║     ██║       ███████║██╔██╗ ██║███████║██║   ╚████╔╝ ███████╗██║███████╗
    ██╔══██╗██╔══╝  ╚════██║██║   ██║██║     ██║       ██╔══██║██║╚██╗██║██╔══██║██║    ╚██╔╝  ╚════██║██║╚════██║
    ██║  ██║███████╗███████║╚██████╔╝███████╗██║       ██║  ██║██║ ╚████║██║  ██║███████╗██║   ███████║██║███████║
    ╚═╝  ╚═╝╚══════╝╚══════╝ ╚═════╝ ╚══════╝╚═╝       ╚═╝  ╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝╚═╝   ╚══════╝╚═╝╚══════╝
'''

footer = '''
     /$$$$$$$$ /$$$$$$$$         /$$$$$$  /$$   /$$ /$$      /$$ /$$$$$$ /$$$$$$$$ /$$$$$$         /$$$$$$  /$$$$$$$   /$$$$$$  /$$$$$$$   /$$$$$$ 
    | $$_____/|__  $$__/        /$$__  $$| $$  | $$| $$$    /$$$|_  $$_/|__  $$__//$$__  $$       /$$__  $$| $$__  $$ /$$__  $$| $$__  $$ /$$__  $$
    | $$         | $$          | $$  \__/| $$  | $$| $$$$  /$$$$  | $$     | $$  | $$  \ $$      | $$  \ $$| $$  \ $$| $$  \ $$| $$  \ $$| $$  \ $$ 
    | $$$$$      | $$          |  $$$$$$ | $$  | $$| $$ $$/$$ $$  | $$     | $$  | $$$$$$$$      | $$$$$$$$| $$$$$$$/| $$  | $$| $$$$$$$/| $$$$$$$$
    | $$__/      | $$           \____  $$| $$  | $$| $$  $$$| $$  | $$     | $$  | $$__  $$      | $$__  $$| $$__  $$| $$  | $$| $$__  $$| $$__  $$
    | $$         | $$           /$$  \ $$| $$  | $$| $$\  $ | $$  | $$     | $$  | $$  | $$      | $$  | $$| $$  \ $$| $$  | $$| $$  \ $$| $$  | $$
    | $$         | $$ /$$      |  $$$$$$/|  $$$$$$/| $$ \/  | $$ /$$$$$$   | $$  | $$  | $$      | $$  | $$| $$  | $$|  $$$$$$/| $$  | $$| $$  | $$
    |__/         |__/|__/       \______/  \______/ |__/     |__/|______/   |__/  |__/  |__/      |__/  |__/|__/  |__/ \______/ |__/  |__/|__/  |__/
   
'''
def show_title(): print(title)
def show_footer(): print(footer)
# [[BANNER-CODE-END]]

# --- Curses compatibility check ---
CURSES_ENABLED = False
try:
    # Test if curses can be initialized. This will fail in IDEs like IDLE.
    if sys.stdout and hasattr(sys.stdout, 'fileno'):
        stdscr = curses.initscr()
        curses.endwin()
        del stdscr
        CURSES_ENABLED = True
    else:
        CURSES_ENABLED = False
except (curses.error, AttributeError):
    # Fallback for environments with a non-functional curses or no fileno.
    CURSES_ENABLED = False
# --- End Curses compatibility check ---


def coerce_number(x):
    try:
        s = str(x).strip()
        if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"): return np.nan
        return float(s)
    except (ValueError, TypeError): return np.nan

def sanitize_for_path(name):
    return str(name).strip().replace("/", "-").replace("\", "-").replace(" ", "_") if name else "UNKNOWN"

def find_row_with_text(df, text, max_rows=30):
    text_lower = text.lower()
    for i in range(min(max_rows, len(df))):
        if any(text_lower in str(v).lower() for v in df.iloc[i] if not pd.isna(v)): return i
    return None

def find_header_and_meta_rows(df):
    header_row = None
    for i in range(min(50, len(df))):
        row_vals = [str(v).strip().lower() for v in df.iloc[i].astype(str).fillna("")]
        if any(v in ("rollno", "roll no", "roll_no") for v in row_vals) and ("total" in row_vals or any(v in ("per", "%", "percent", "percentage") for v in row_vals)):
            header_row = i
            break
    return header_row, find_row_with_text(df, "CLASS :", 10), find_row_with_text(df, "NAME OF EXAMINATION", 10)

def parse_exam_and_outof(df, exam_row):
    if exam_row is None: return None, None
    for val in (str(v) for v in df.iloc[exam_row] if not pd.isna(v)):
        if val.strip() and "NAME OF EXAMINATION" not in val:
            exam_name = val.strip()
            if "(" in exam_name and ")" in exam_name:
                start, end = exam_name.find("(") + 1, exam_name.find(")")
                try: per_subject_out_of = int(float(exam_name[start:end].strip()))
                except (ValueError, TypeError): per_subject_out_of = None
                return exam_name[:start-1].strip(), per_subject_out_of
            return exam_name, None
    return None, None

def parse_class_name(df, class_row):
    if class_row is None: return None
    row = [str(v) for v in df.iloc[class_row] if not pd.isna(v)]
    for idx, val in enumerate(row):
        if val.strip().upper().startswith("CLASS") and idx + 1 < len(row) and row[idx + 1].strip(): return row[idx + 1].strip()
    for val in row[1:]:
        if val.strip(): return val.strip()
    return None

def detect_subject_columns(df, header_row):
    headers = [str(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else "" for v in df.iloc[header_row]]
    subjects, subject_to_cols, total_col, per_col = [], {}, None, None

    for ci, h in enumerate(headers):
        label = h.strip().upper()
        if label == "TOTAL": total_col = ci
        elif label in ("PER", "%", "PERCENT", "PERCENTAGE"): per_col = ci

    end_ci = total_col if total_col is not None else len(headers)
    ci = 2 if len(headers) > 2 else 0
    while ci < end_ci:
        name = headers[ci].strip()
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            marks_col = ci
            percent_col = None
            if ci + 1 < end_ci and headers[ci + 1].strip() == name:
                percent_col = ci + 1
                ci += 2
            elif ci + 1 < end_ci and headers[ci + 1].strip() == "":
                numeric_like = 0
                for r in range(header_row + 1, min(header_row + 11, len(df))):
                    num = coerce_number(df.iat[r, ci + 1])
                    if not np.isnan(num) and 0 <= num <= 100:
                        numeric_like += 1
                if numeric_like >= 2: 
                    percent_col = ci + 1
                    ci += 2
                else:
                    ci += 1
            else:
                ci += 1
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1
    return subjects, subject_to_cols, total_col, per_col

def extract_class_results(file_path, sheet_name=None):
    df = pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)
    if isinstance(df, dict): df = next(iter(df.values()))
    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None: raise ValueError("Header row not found.")
    exam_name, _ = parse_exam_and_outof(df, exam_row)
    per_subject_out_of = 100
    class_name = parse_class_name(df, class_row)
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(df, header_row)
    students = []
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        try:
            roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError):
            continue
        name = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else "" 
        marks, subject_percentages = {}, {}
        for s in subjects:
            cols = subject_to_cols[s]
            marks_val = coerce_number(row.iloc[cols.get("marks")]) if cols.get("marks") is not None and cols.get("marks") < len(row) else np.nan
            marks[s] = marks_val
            percent_val = np.nan
            if not np.isnan(marks_val):
                percent_val = round((marks_val / per_subject_out_of) * 100, 2)
            subject_percentages[s] = percent_val
        valid_marks_values = [m for m in marks.values() if not np.isnan(m)]
        total = np.nansum(valid_marks_values)
        num_valid_subjects = len(valid_marks_values)
        percent = np.nan
        if num_valid_subjects > 0:
            denom = per_subject_out_of * num_valid_subjects
            if denom > 0:
                percent = round((total / denom) * 100, 2)
        if not name and all(np.isnan(v) for v in marks.values()):
            continue
        students.append({
            "roll_no": roll_no, "name": name, "marks": marks,
            "subject_percentages": subject_percentages, "total": total, "percentage": percent
        })
    result = {
        "class_name": class_name, "exam_name": exam_name, "subjects": subjects,
        "per_subject_out_of": per_subject_out_of, "students": students
    }
    if per_subject_out_of and subjects:
        num_subjects = len(subjects)
        result["total_out_of"] = per_subject_out_of * num_subjects
    return result

def results_to_dfs(parsed):
    subjects = parsed.get("subjects", [])
    rows_r, rows_p = [], []
    for s in parsed.get("students", []):
        base = {"Roll No": s.get("roll_no"), "Name": s.get("name", "")}
        row_r, row_p = base.copy(), base.copy()
        for subj in subjects:
            row_r[f"{subj}_Marks"] = s.get("marks", {}).get(subj)
            row_p[f"{subj}_%"] = s.get("subject_percentages", {}).get(subj)
        row_r["Total"], row_r["Percentage"] = s.get("total"), s.get("percentage")
        row_p["Overall_Percentage"] = s.get("percentage")
        rows_r.append(row_r); rows_p.append(row_p)
    return pd.DataFrame(rows_r), pd.DataFrame(rows_p)

def save_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    out_dir = Path(base_dir) / sanitize_for_path(parsed.get("class_name")) / sanitize_for_path(parsed.get("exam_name"))
    out_dir.mkdir(parents=True, exist_ok=True)
    df_r, df_p = results_to_dfs(parsed)
    df_r.to_csv(out_dir / "result.csv", index=False)
    df_p.to_csv(out_dir / "percentage.csv", index=False)
    return out_dir

def export_df_to_excel(df, fname="export.xlsx"):
    if input("Save to Excel? (y/n): ").strip().lower() in ("y", "yes"): 
        name = input(f"Filename ('{fname}'): ").strip() or fname
        out_path = name if name.lower().endswith(".xlsx") else name + ".xlsx"
        try:
            df.to_excel(out_path, index=False)
            print("    Saved:", out_path)
            return out_path
        except Exception as e: print("    Error:", e)
    return None

def display_df(df, title):
    df_display = df.copy()
    for col in df_display.select_dtypes(include=['float64']).columns:
        df_display[col] = df_display[col].apply(lambda x: str(int(round(x))) if pd.notna(x) else "")
    for col in df_display.columns:
        df_display[col] = df_display[col].astype(str)
    col_widths = {col: max(len(col), df_display[col].str.len().max()) for col in df_display.columns}
    header = " | ".join(f"{col.upper():<{col_widths[col]}}" for col in df_display.columns)
    separator = "-+- ".join("-" * col_widths[col] for col in df_display.columns)
    table_width = len(header)
    print(f"\n    {title.upper().center(table_width)}")
    print(f"    {'=' * table_width}")
    print(f"    {header}")
    print(f"    {separator}")
    for _, row in df_display.iterrows():
        row_str = " | ".join(f"{row[col]:<{col_widths[col]}}" for col in df_display.columns)
        print(f"    {row_str}")
    print(f"    {'=' * table_width}\n")

def draw_menu(stdscr, title, opts, idx, help_text):
    stdscr.clear(); stdscr.addstr(1, 2, title); stdscr.addstr(2, 2, help_text)
    for i, opt in enumerate(opts): stdscr.addstr(4 + i, 2, f" {'>' if i == idx else ' '} {opt}")
    stdscr.refresh()

def select_from_list(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')): idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord('j')): idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13): return opts[idx]
        elif key in (ord('q'), ord('Q')): return None

def select_with_delete(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')): idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord('j')): idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13): return opts[idx], 'select'
        elif key in (ord('d'), ord('D')): return opts[idx], 'delete'
        elif key in (ord('q'), ord('Q')): return None, None

def select_from_list_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i+1}. {opt}")
    print(f"    (Enter 'q' to quit)")
    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == 'q':
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(opts): return opts[idx]
            else: print("    Invalid number. Please try again.")
        except ValueError: print("    Please enter a number.")

def select_with_delete_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i+1}. {opt}")
    print("    (Enter 'd<number>' to delete, e.g., 'd1')")
    print(f"    (Enter 'q' to quit)")
    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == 'q': return None, None
        action = 'select'
        item_choice = choice
        if choice.startswith('d') and len(choice) > 1:
            action = 'delete'
            item_choice = choice[1:]
        try:
            idx = int(item_choice) - 1
            if 0 <= idx < len(opts): return opts[idx], action
            else: print("    Invalid number. Please try again.")
        except ValueError: print("    Please enter a valid number or command.")

def fuzzy_search_file_select_no_curses():
    search_term = ""
    while True:
        search_term = input("\n    Enter search term to find Excel file (or 'q' to quit): ").strip()
        if not search_term or search_term.lower() == 'q': return None
        all_files = glob.glob("**/*.xlsx", recursive=True)
        if not all_files: print("    No .xlsx files found in the current directory or subdirectories."); continue
        matches = process.extract(search_term, all_files, limit=10)
        search_results = [match[0] for match in matches if match[1] > 30]
        if not search_results: print("    No matches found."); continue
        print("\n    --- Select a File ---")
        for i, file_path in enumerate(search_results):
            print(f"    {i+1}. {file_path}")
        choice = input("    Select a number (or 'r' to research): ").strip().lower()
        if choice == 'r': continue
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(search_results): return search_results[idx]
            else: print("    Invalid number.")
        except ValueError: print("    Invalid input.")

def select_class_exam(base_dir='user-data'):
    classes = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    if not classes: return None, None
    if CURSES_ENABLED:
        s_class = curses.wrapper(select_from_list, "Select Class", classes, "Up/Down, Enter, q to quit.")
    else:
        s_class = select_from_list_no_curses("Select Class", classes, "Up/Down, Enter, q to quit.")
    if not s_class: return None, None
    exams = sorted([d for d in os.listdir(os.path.join(base_dir, s_class)) if os.path.isdir(os.path.join(base_dir, s_class, d))])
    if not exams: return None, None
    if CURSES_ENABLED:
        s_exam = curses.wrapper(select_from_list, f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit.")
    else:
        s_exam = select_from_list_no_curses(f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit.")
    return s_class, s_exam

def group_by_percent(csv_path):
    df = pd.read_csv(csv_path)
    user_input = input("Custom grouping (e.g., 90,80,33) or Enter for default: ")
    thresholds = sorted([int(t) for t in user_input.split(',')] if user_input else [90,80,70,60,50,40,33], reverse=True)
    if 100 not in thresholds: thresholds.insert(0, 100)
    grouping = [[(thresholds[i+1] + 1 if i + 1 < len(thresholds) else 0), thresholds[i]] for i in range(len(thresholds))]
    subjects = [c[:-2] for c in df.columns if c.endswith('_%') and c != 'Overall_Percentage']
    summary = []
    for subj in subjects:
        def get_group(score):
            if pd.isna(score): return "N/A"
            for low, high in grouping:
                if low <= score <= high: return f"{low}-{high}"
            return "Other"
        summary.append({'Subject': subj, **df[f"{subj}_%"].apply(get_group).value_counts().to_dict()})
    summary_df = pd.DataFrame(summary).fillna(0)
    display_df(summary_df, "Grouped Summary (counts)")
    return df, summary_df

def plot_chart(df, x, y, title, xl, yl, kind='bar', rot=45, figsize=(12,6), **kwargs):
    plt.figure(figsize=figsize)
    if kind == 'bar': plt.bar(df[x], df[y], **kwargs)
    elif kind == 'line': plt.plot(df[x], df[y], marker='o', **kwargs)
    elif kind == 'scatter': plt.scatter(df[x], df[y], **kwargs)
    plt.title(title, fontsize=14, fontweight='bold'); plt.xlabel(xl, fontsize=12); plt.ylabel(yl, fontsize=12)
    plt.xticks(rotation=rot, ha='right'); plt.ylim(0, 100); plt.grid(axis='y', alpha=0.3)
    plt.tight_layout(); plt.show()

def fuzzy_search_file_select(stdscr):
    search_term = ""
    selected_index = 0
    all_files = glob.glob("**/*.xlsx", recursive=True)
    search_results = []
    curses.curs_set(1)
    stdscr.nodelay(0)
    while True:
        stdscr.clear()
        stdscr.addstr(1, 2, "Search for an Excel File")
        stdscr.addstr(2, 2, "Type to search, Up/Down to navigate, Enter to select, 'q' to quit.")
        stdscr.addstr(4, 4, f"Search: {search_term}")
        if search_term:
            matches = process.extract(search_term, all_files, limit=10)
            search_results = [match for match in matches if match[1] > 30]
        else:
            search_results = []
        if search_results:
            display_line = 6
            for i, (file_path, score) in enumerate(search_results):
                filename = os.path.basename(file_path)
                display_text = f"{filename} ({score}%)"
                if i == selected_index:
                    stdscr.addstr(display_line, 2, f"> {display_text}", curses.A_REVERSE)
                else:
                    stdscr.addstr(display_line, 2, f"  {display_text}")
                display_line += 1
                stdscr.addstr(display_line, 6, f"Path: {file_path}")
                display_line += 2
        elif search_term:
            stdscr.addstr(6, 2, "  No matches found.")
        stdscr.move(4, 12 + len(search_term))
        stdscr.refresh()
        key = stdscr.getch()
        if key in (curses.KEY_ENTER, 10, 13):
            if search_results: return search_results[selected_index][0]
        elif key == curses.KEY_UP:
            selected_index = max(0, selected_index - 1)
        elif key == curses.KEY_DOWN:
            selected_index = min(len(search_results) - 1, selected_index + 1)
        elif key in (curses.KEY_BACKSPACE, 127, 8):
            search_term = search_term[:-1]
            selected_index = 0
        elif key in (ord('q'), ord('Q'), 27): return None
        elif 32 <= key <= 126: search_term += chr(key); selected_index = 0

def upload_pipeline():
    if CURSES_ENABLED:
        fpath = curses.wrapper(fuzzy_search_file_select)
    else:
        fpath = fuzzy_search_file_select_no_curses()
    if not fpath: print("    File selection cancelled."); return
    print(f"    Selected file: {fpath}")
    try:
        sheets = pd.ExcelFile(fpath).sheet_names
        print("    Sheets:", ", ".join(sheets))
        sheet = input("    Sheet name (Enter for first): ").strip() or 0
        s_dir = input("    Save directory ('user-data'): ").strip() or "user-data"
        out = save_results_to_csv(fpath, sheet_name=sheet, base_dir=s_dir)
        print(f"    Saved to: {out}")
    except Exception as e: print(f"    Error: {e}")

def group_by_percent_interactive():
    s_class, s_exam = select_class_exam('user-data')
    if not (s_class and s_exam): return
    path = os.path.join('user-data', s_class, s_exam, 'percentage.csv')
    if not os.path.isfile(path): print(f"    'percentage.csv' not found for {s_class} - {s_exam}."); return
    _, summary_df = group_by_percent(path)
    if not summary_df.empty:
        (Path(path).parent / "grouped.csv").write_text(summary_df.to_csv(index=False))
        export_df_to_excel(summary_df, fname="grouped.xlsx")

def view_data_flow():
    s_class, s_exam = select_class_exam('user-data')
    if not (s_class and s_exam): return
    base_path = os.path.join('user-data', s_class, s_exam)
    opts = ["Percentage", "Grouped", "Full Result", "All"]
    if CURSES_ENABLED:
        dtype = curses.wrapper(select_from_list, "Select Data to View", opts, "Up/Down, Enter, q to quit.")
    else:
        dtype = select_from_list_no_curses("Select Data to View", opts, "Up/Down, Enter, q to quit.")
    if not dtype: return
    files = {"Percentage": ["percentage.csv"], "Grouped": ["grouped.csv"], "Full Result": ["result.csv"], "All": ["percentage.csv", "result.csv", "grouped.csv"]}
    for f in files.get(dtype, []):
        fpath = os.path.join(base_path, f)
        if os.path.isfile(fpath): display_df(pd.read_csv(fpath), f.replace('.csv', '').title())
        else: print(f"    {f} not available.")

def plot_graphs_flow(base_dir='user-data'):
    c_name, e_name = select_class_exam(base_dir)
    if not (c_name and e_name): return
    opts = ["Bar Chart", "Line Chart", "Scatter Plot"]
    if CURSES_ENABLED:
        g_type = curses.wrapper(select_from_list, "Select Graph Type", opts, "Up/Down, Enter, q to quit.")
    else:
        g_type = select_from_list_no_curses("Select Graph Type", opts, "Up/Down, Enter, q to quit.")
    if not g_type: return
    csv_path = os.path.join(base_dir, c_name, e_name, 'percentage.csv')
    if not os.path.isfile(csv_path): print(f"    percentage.csv not found for {c_name} - {e_name}"); return
    df = pd.read_csv(csv_path)
    title = f'{g_type} - {c_name} - {e_name}'
    if "Bar" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='bar')
    elif "Line" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='line')
    elif "Scatter" in g_type: plot_chart(df, 'Roll No', 'Overall_Percentage', title, 'Roll Number', 'Percentage (%)', kind='scatter')

def delete_data_flow(base_dir='user-data'):
    classes = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    if not classes: print("    No classes found."); return
    if CURSES_ENABLED:
        selected_class, action = curses.wrapper(select_with_delete, "Select Class", classes, "Up/Down, Enter to view exams, d to delete class, q to quit.")
    else:
        selected_class, action = select_with_delete_no_curses("Select Class", classes, "Up/Down, Enter to view exams, d to delete class, q to quit.")
    if not selected_class: return
    if action == 'delete':
        confirm = input(f"    Are you sure you want to permanently delete all data for class '{selected_class}'? [y/N]: ").strip().lower()
        if confirm == 'y':
            try:
                shutil.rmtree(os.path.join(base_dir, selected_class))
                print(f"    Successfully deleted class '{selected_class}'.")
            except Exception as e: print(f"    Error deleting class '{selected_class}': {e}")
        else: print("    Deletion cancelled.")
        return
    class_path = os.path.join(base_dir, selected_class)
    exams = sorted([d for d in os.listdir(class_path) if os.path.isdir(os.path.join(class_path, d))])
    if not exams: print(f"    No exams found for class '{selected_class}'."); return
    if CURSES_ENABLED:
        selected_exam, action = curses.wrapper(select_with_delete, f"Exams for {selected_class}", exams, "Up/Down, d to delete exam, q to quit.")
    else:
        selected_exam, action = select_with_delete_no_curses(f"Exams for {selected_class}", exams, "Up/Down, d to delete exam, q to quit.")
    if not selected_exam: return
    if action == 'delete':
        confirm = input(f"    Are you sure you want to permanently delete exam '{selected_exam}' for class '{selected_class}'? [y/N]: ").strip().lower()
        if confirm == 'y':
            try:
                shutil.rmtree(os.path.join(class_path, selected_exam))
                print(f"    Successfully deleted exam '{selected_exam}' for class '{selected_class}'.")
            except Exception as e: print(f"    Error deleting exam '{selected_exam}': {e}")
        else: print("    Deletion cancelled.")

def main():
    # [[BANNER-CODE-START]]
    show_title()
    # [[BANNER-CODE-END]]
    if not os.path.exists('user-data'): os.makedirs('user-data')
    actions = {'1': upload_pipeline, '2': group_by_percent_interactive, '3': view_data_flow, '4': plot_graphs_flow, '5': delete_data_flow}
    menu_text = (
        "\n"
        "    +---------------------------------------+"
        "    |               MAIN MENU               |"
        "    +---------------------------------------+"
        "    | 1. Upload New Excel File              |"
        "    | 2. Group Data by Percentage           |"
        "    | 3. View Class/Exam Data               |"
        "    | 4. Plot Graphs                        |"
        "    | 5. Delete Data                        |"
        "    +---------------------------------------+"
        "    | clear - Clear Screen                  |"
        "    | q     - Quit                          |"
        "    +---------------------------------------+"
    )
    try:
        while True:
            print(menu_text)
            choice = input("\n    Enter your choice: ").strip().lower()
            if choice in actions: actions[choice]()
            elif choice == "clear":
                os.system('cls' if os.name == 'nt' else 'clear')
                # [[BANNER-CODE-START]]
                show_title()
                # [[BANNER-CODE-END]]
            elif choice in ("q", "quit"): break
            else: print("    Invalid choice. Please try again.")
    except KeyboardInterrupt: print("\n    Operation cancelled by user."); pass
    finally:
        # [[BANNER-CODE-START]]
        print("\n    Credits:")
        show_footer()
        # [[BANNER-CODE-END]]

if __name__ == "__main__":
    main();

# File: /home/utkarsh/development/12thProject/data/exporter.py
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

# File: /home/utkarsh/development/12thProject/data/handler.py
# This file is the main entry point for handling Excel parsing.
# It imports functions from other modules for organization.

import pandas as pd
import numpy as np
from pathlib import Path

# Import from submodules
from .parser import extract_class_results, extractDataFromExcel
from .printer import print_parsed_summary, print_class_results
from .saver import results_to_dataframes, save_class_results_to_csv, save_and_report
from .utils import coerce_number, sanitize_for_path, excludeRollNoAndName

def run_pipeline():
    # This function runs the full pipeline: input file path, extract data, show summary, save to CSV, notify.
    print("Welcome to the Class Results Processor!")
    print("Please provide the path to your Excel file (e.g., data/sample/subject-analysis.xlsx):")
    file_path = input("Excel file path: ").strip()
    if not file_path: print("No file path provided. Exiting."); return

    # Try to display available sheet names to help the user choose
    try:
        xls = pd.ExcelFile(file_path)
        if xls.sheet_names:
            print("\nAvailable sheets in this workbook:")
            for i, nm in enumerate(xls.sheet_names, 1):
                print(f"  {i}. {nm}")
    except Exception as e:
        # Non-fatal; continue to prompt without listing
        print(f"(Could not read sheet names: {e})")

    raw_sheet = input("Sheet name or number (press Enter for first sheet): ").strip()
    sheet_name = None
    try:
        # If user typed a number, treat it as 1-based index
        if raw_sheet.isdigit() and 'xls' in locals():
            idx = int(raw_sheet) - 1
            if 0 <= idx < len(xls.sheet_names):
                sheet_name = xls.sheet_names[idx]
        elif raw_sheet and 'xls' in locals():
            # Try exact match
            if raw_sheet in xls.sheet_names:
                sheet_name = raw_sheet
            else:
                # Try trimmed/case-insensitive matches
                trimmed = raw_sheet.strip()
                lower_map = {s.lower(): s for s in xls.sheet_names}
                if trimmed.lower() in lower_map:
                    sheet_name = lower_map[trimmed.lower()]
                else:
                    # Try startswith (case-insensitive)
                    candidates = [s for s in xls.sheet_names if s.lower().startswith(trimmed.lower())]
                    if candidates:
                        sheet_name = candidates[0]
        # If still None and we have sheets, fall back to first
        if sheet_name is None and 'xls' in locals() and xls.sheet_names:
            print("No matching sheet found. Using first sheet.")
            sheet_name = xls.sheet_names[0]
    except Exception:
        # As a last resort, let pandas default to first sheet by passing None
        sheet_name = None
    base_dir = input("Base directory for saving CSVs (press Enter for 'user-data'): ").strip() or "user-data"

    try:
        # Extract data
        print("\nExtracting data from the Excel file...")
        parsed = extract_class_results(file_path, sheet_name=sheet_name)
        print("Data extracted successfully!")

        # Show summary
        print("\n--- Results Summary ---")
        print_parsed_summary(parsed)

        # Save to CSV
        print("\nSaving data to CSV files...")
        out_dir = save_class_results_to_csv(file_path, sheet_name=sheet_name, base_dir=base_dir)
        print(f"CSVs saved in: {out_dir}")

        # Notify
        class_name = parsed.get("class_name", "Unknown")
        exam_name = parsed.get("exam_name", "Unknown")
        print(f"\nData for class '{class_name}' and exam '{exam_name}' has been stored properly!")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    run_pipeline()


# File: /home/utkarsh/development/12thProject/data/parser.py
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
# File: /home/utkarsh/development/12thProject/data/printer.py
# Functions for printing parsed data summaries.

import pandas as pd
import numpy as np

from .parser import extract_class_results

def print_parsed_summary(data):
    # This function prints a summary of the parsed data.
    # It shows exam, class, subjects, and then each student's details.
    class_name = data.get("class_name")
    exam_name = data.get("exam_name")
    subjects = data.get("subjects", [])
    total_out_of = data.get("total_out_of")

    # Print header info
    header_parts = [
        f"Exam: {exam_name if exam_name else 'N/A'}",
        f"Class: {class_name if class_name else 'N/A'}",
        f"Subjects ({len(subjects)}): {', '.join(subjects) if subjects else 'N/A'}",
    ]
    if total_out_of is not None:
        header_parts.append(f"Total Out Of: {total_out_of}")
    print(" | ".join(header_parts))

    # Print each student
    for s in data.get("students", []):
        roll = s.get("roll_no")
        name = s.get("name") or ""
        marks = s.get("marks", {})
        subj_perc = s.get("subject_percentages", {})
        total = s.get("total")
        percent = s.get("percentage")

        def format_number(v):
            # Helper to format numbers nicely
            if v is None or (isinstance(v, float) and np.isnan(v)):
                return ""
            try:
                fv = float(v)
                if fv.is_integer():
                    return str(int(fv))
                else:
                    return f"{fv:.2f}"
            except:
                return str(v)

        # Build marks string like "Math:85 (85.00%), Science:90 (90.00%)"
        parts = []
        for subj in subjects:
            m = format_number(marks.get(subj))
            p = format_number(subj_perc.get(subj))
            if p != "":
                parts.append(f"{subj}:{m} ({p}%)")
            else:
                parts.append(f"{subj}:{m}")
        marks_str = ", ".join(parts)
        line = f"Roll:{roll}  Name:{name}  Marks: [{marks_str}]  Total:{format_number(total)}  %:{format_number(percent)}"
        print(line)

def print_class_results(file_path, sheet_name=None):
    # This function reads the Excel file, parses it, and prints the summary.
    # It's a shortcut to do both extraction and printing.
    data = extract_class_results(file_path, sheet_name=sheet_name)
    print_parsed_summary(data)
# File: /home/utkarsh/development/12thProject/data/sample/classData.py
# data/classdata.py

# Sample data

data = {
    "Roll No": ['OutOfMarks', 1, 2, 3, 4, 5],
    "Name": ['', "Alice", "Bob", "Charlie", "Diana", "Ethan"],
    "Math": [100, 88, 76, 95, 69, 85],
    "Science": [100, 91, 82, 89, 74, 90],
    "English": [80, 84, 79, 92, 81, 87],
    "History": [80, 78, 85, 88, 73, 80],
    "Computer Science": [50, 93, 89, 97, 88, 92]
}

# File: /home/utkarsh/development/12thProject/data/saver.py
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
# File: /home/utkarsh/development/12thProject/data/subjects.py
# Functions for detecting and handling subject columns in the Excel sheet.

import numpy as np

from .utils import coerce_number

def detect_subject_columns(df, header_row):
    # This function figures out which columns are for subjects, total, and percentage.
    # It looks at the header row and identifies subject names, their marks and percent columns.
    # Subjects are between RollNo (column 0-1) and Total.
    headers = []
    for val in df.iloc[header_row]:
        # Safely handle NaN/None before converting to string
        if val is None or (isinstance(val, float) and np.isnan(val)):
            headers.append("")
        else:
            headers.append(str(val))
    subjects = []
    # subject_to_cols will map subject name to its column indices for marks and percent
    subject_to_cols = {}
    total_col = None
    per_col = None

    # Find the column index for TOTAL
    for ci in range(len(headers)):
        label = headers[ci].strip().upper()
        if label == "TOTAL":
            total_col = ci
            break
    # Find the column index for PER or %
    for ci in range(len(headers)):
        label = headers[ci].strip().upper()
        if label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci
            break

    # Subjects start from column 2 (after RollNo and Name) up to TOTAL column
    end_ci = total_col if total_col is not None else len(headers)
    start_ci = 2 if len(headers) > 2 else 0

    ci = start_ci
    while ci < end_ci:
        name = headers[ci].strip()
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            # This is a subject column
            marks_col = ci
            percent_col = None
            # Check if the next column has the same name (for percent)
            if ci + 1 < end_ci and headers[ci + 1].strip() == name:
                percent_col = ci + 1
                ci += 2  # Skip next since it's percent
            else:
                # Sometimes the percent column is blank in header but has percent values
                if ci + 1 < end_ci and headers[ci + 1].strip() == "":
                    # Check a few rows below to see if values are 0-100 (percentages)
                    sample_rows = []
                    for r in range(header_row + 1, min(header_row + 1 + 10, len(df))):
                        sample_rows.append(r)
                    numeric_like = 0
                    for r in sample_rows:
                        val = df.iat[r, ci + 1]
                        num = coerce_number(val)
                        if not (isinstance(num, float) and np.isnan(num)):
                            if 0 <= num <= 100:
                                numeric_like += 1
                    if numeric_like >= 2:  # If at least 2 look like percentages
                        percent_col = ci + 1
                        ci += 2
                    else:
                        ci += 1
                else:
                    ci += 1
            # Add to the map
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1

    return subjects, subject_to_cols, total_col, per_col
# File: /home/utkarsh/development/12thProject/data/utils.py
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
    return str(name).strip().replace("/", "-").replace("\", "-")

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
# File: /home/utkarsh/development/12thProject/graphs/__init__.py
# Graphs module for plotting class exam data

# File: /home/utkarsh/development/12thProject/graphs/plot_data.py
"""Main script to run the plotting feature.
This script lets users select class, exam, and graph type, then displays the graph.
"""

import os
from graphs.select_graph import select_class_exam_and_graph
from graphs.plotter import (
    plot_bar_chart,
    plot_subject_comparison,
    plot_line_chart,
    plot_pie_chart,
    plot_horizontal_bar,
    plot_subject_average,
    plot_scatter,
    plot_box_plot
)


def run_plot_data(base_dir='user-data'):
    """Main function to run the plotting feature."""
    print("\n" + "="*60)
    print("         PLOT CLASS EXAM DATA")
    print("="*60)
    print("\nSelect class, exam, and graph type to visualize data.\n")
    
    # Get user selections
    class_name, exam_name, graph_type = select_class_exam_and_graph(base_dir)
    
    if not class_name or not exam_name or not graph_type:
        print("\nNo selection made. Exiting.")
        return
    
    # Build path to percentage.csv
    csv_path = os.path.join(base_dir, class_name, exam_name, 'percentage.csv')
    
    # Check if file exists
    if not os.path.isfile(csv_path):
        print(f"\nError: percentage.csv not found for {class_name} - {exam_name}")
        print(f"Expected path: {csv_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Class: {class_name}")
    print(f"Exam: {exam_name}")
    print(f"Graph: {graph_type}")
    print(f"{'='*60}\n")
    print("Loading data and generating graph...\n")
    
    # Call the appropriate plotting function based on selection
    try:
        if "Bar Chart" in graph_type:
            plot_bar_chart(csv_path, class_name, exam_name)
        
        elif "Subject Comparison" in graph_type:
            plot_subject_comparison(csv_path, class_name, exam_name)
        
        elif "Line Chart" in graph_type:
            plot_line_chart(csv_path, class_name, exam_name)
        
        elif "Pie Chart" in graph_type:
            plot_pie_chart(csv_path, class_name, exam_name)
        
        elif "Horizontal Bar" in graph_type:
            plot_horizontal_bar(csv_path, class_name, exam_name)
        
        elif "Subject Average" in graph_type:
            plot_subject_average(csv_path, class_name, exam_name)
        
        elif "Scatter Plot" in graph_type:
            plot_scatter(csv_path, class_name, exam_name)
        
        elif "Box Plot" in graph_type:
            plot_box_plot(csv_path, class_name, exam_name)
        
        else:
            print("Unknown graph type selected.")
        
        print("\nGraph displayed successfully!")
        
    except Exception as e:
        print(f"\nError generating graph: {e}")
        print("Please make sure the data file has the required columns.")


if __name__ == "__main__":
    run_plot_data()

# File: /home/utkarsh/development/12thProject/graphs/plotter.py
"""Simple plotting functions for class exam data.
This module provides easy-to-use functions to create different types of charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_bar_chart(csv_path, class_name, exam_name):
    """Create a bar chart showing overall percentage for each student."""
    df = pd.read_csv(csv_path)
    
    plt.figure(figsize=(12, 6))
    
    if 'Overall_Percentage' in df.columns:
        students = df['Name'].tolist()
        percentages = df['Overall_Percentage'].tolist()
        
        plt.bar(students, percentages, color='skyblue', edgecolor='navy')
        plt.xlabel('Students', fontsize=12)
        plt.ylabel('Percentage (%)', fontsize=12)
        plt.title(f'Student Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("Overall_Percentage column not found in data.")


def plot_subject_comparison(csv_path, class_name, exam_name):
    """Create a grouped bar chart comparing all students across subjects."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    students = df['Name'].tolist()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    bar_width = 0.8 / len(subject_cols)
    x_positions = range(len(students))
    
    for i, subject_col in enumerate(subject_cols):
        subject_name = subject_col.replace('_%', '')
        values = df[subject_col].tolist()
        offset = (i - len(subject_cols) / 2) * bar_width + bar_width / 2
        positions = [x + offset for x in x_positions]
        ax.bar(positions, values, bar_width, label=subject_name)
    
    ax.set_xlabel('Students', fontsize=12)
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.set_title(f'Subject-wise Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(students, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_line_chart(csv_path, class_name, exam_name):
    """Create a line chart showing student performance trends."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    students = df['Name'].tolist()
    percentages = df['Overall_Percentage'].tolist()
    
    plt.figure(figsize=(12, 6))
    plt.plot(students, percentages, marker='o', linewidth=2, markersize=8, color='green')
    plt.xlabel('Students', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Performance Trend - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_pie_chart(csv_path, class_name, exam_name):
    """Create a pie chart showing pass/fail distribution."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    pass_count = len(df[df['Overall_Percentage'] >= 35])
    fail_count = len(df[df['Overall_Percentage'] < 35])
    
    labels = ['Pass (>=35%)', 'Fail (<35%)']
    sizes = [pass_count, fail_count]
    colors = ['lightgreen', 'lightcoral']
    explode = (0.1, 0)
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 12})
    plt.title(f'Pass/Fail Distribution - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def plot_horizontal_bar(csv_path, class_name, exam_name):
    """Create a horizontal bar chart for easier reading of student names."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    df_sorted = df.sort_values('Overall_Percentage', ascending=True)
    students = df_sorted['Name'].tolist()
    percentages = df_sorted['Overall_Percentage'].tolist()
    
    colors = ['red' if p < 35 else 'orange' if p < 60 else 'green' for p in percentages]
    
    plt.figure(figsize=(10, 8))
    plt.barh(students, percentages, color=colors, edgecolor='black')
    plt.xlabel('Percentage (%)', fontsize=12)
    plt.ylabel('Students', fontsize=12)
    plt.title(f'Student Rankings - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xlim(0, 100)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_subject_average(csv_path, class_name, exam_name):
    """Create a bar chart showing average percentage for each subject."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    subject_names = []
    averages = []
    
    for col in subject_cols:
        subject_name = col.replace('_%', '')
        avg = df[col].mean()
        subject_names.append(subject_name)
        averages.append(avg)
    
    colors = ['red' if a < 35 else 'orange' if a < 60 else 'green' for a in averages]
    
    plt.figure(figsize=(10, 6))
    plt.bar(subject_names, averages, color=colors, edgecolor='black')
    plt.xlabel('Subjects', fontsize=12)
    plt.ylabel('Average Percentage (%)', fontsize=12)
    plt.title(f'Subject-wise Class Average - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(averages):
        plt.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def plot_scatter(csv_path, class_name, exam_name):
    """Create a scatter plot showing roll number vs percentage."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns or 'Roll No' not in df.columns:
        print("Required columns not found.")
        return
    
    roll_nos = df['Roll No'].tolist()
    percentages = df['Overall_Percentage'].tolist()
    
    colors = ['red' if p < 35 else 'orange' if p < 60 else 'green' for p in percentages]
    
    plt.figure(figsize=(12, 6))
    plt.scatter(roll_nos, percentages, c=colors, s=100, alpha=0.6, edgecolors='black')
    plt.xlabel('Roll Number', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Roll No vs Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_box_plot(csv_path, class_name, exam_name):
    """Create a box plot showing distribution of subject percentages."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    data_to_plot = []
    labels = []
    
    for col in subject_cols:
        subject_name = col.replace('_%', '')
        values = df[col].dropna().tolist()
        data_to_plot.append(values)
        labels.append(subject_name)
    
    plt.figure(figsize=(12, 6))
    box = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    for patch in box['boxes']:
        patch.set_facecolor('lightblue')
    
    plt.xlabel('Subjects', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Subject Performance Distribution - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()

# File: /home/utkarsh/development/12thProject/graphs/select_graph.py
"""Simple UI to select Class, Exam, and Graph Type for plotting.
- Uses arrow keys (Up/Down) to navigate, Enter to select, 'q' to quit.
- Follows the same pattern as ui/select_data.py
- User selects: Class -> Exam -> Graph Type -> Shows the graph
"""

import os
import curses
from ui.select_data import list_classes, list_exams


def draw_menu(stdscr, title, options, index):
    """Draw a simple menu with options."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, "Use Up/Down arrows and Enter. Press q to quit.")
    top = 4
    for i, opt in enumerate(options):
        marker = ">" if i == index else " "
        line = f" {marker} {opt}"
        if top + i < h - 1:
            stdscr.addstr(top + i, 2, line)
    stdscr.refresh()


def select_from_list(stdscr, title, options):
    """Let user select an option from a list using arrow keys."""
    if not options:
        return None
    index = 0
    while True:
        draw_menu(stdscr, title, options, index)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            index = (index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j')):
            index = (index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[index]
        elif key in (ord('q'), ord('Q')):
            return None


def get_graph_types():
    """Return list of available graph types."""
    return [
        "Bar Chart - Student Performance",
        "Subject Comparison - All Students",
        "Line Chart - Performance Trend",
        "Pie Chart - Pass/Fail Distribution",
        "Horizontal Bar - Student Rankings",
        "Subject Average - Class Performance",
        "Scatter Plot - Roll No vs Percentage",
        "Box Plot - Subject Distribution"
    ]


def select_class_exam_and_graph(base_dir='user-data'):
    """Main function to select class, exam, and graph type.
    Returns: (class_name, exam_name, graph_type) or (None, None, None) if cancelled.
    """
    
    # Step 1: Select Class
    classes = list_classes(base_dir)
    if not classes:
        print("No classes found in", base_dir)
        return None, None, None
    
    selected_class = curses.wrapper(select_from_list, "Select Class", classes)
    if not selected_class:
        return None, None, None
    
    # Step 2: Select Exam
    exams = list_exams(base_dir, selected_class)
    if not exams:
        print("No exams found for class:", selected_class)
        return None, None, None
    
    selected_exam = curses.wrapper(select_from_list, f"Select Exam for {selected_class}", exams)
    if not selected_exam:
        return None, None, None
    
    # Step 3: Select Graph Type
    graph_types = get_graph_types()
    selected_graph = curses.wrapper(select_from_list, "Select Graph Type", graph_types)
    if not selected_graph:
        return None, None, None
    
    return selected_class, selected_exam, selected_graph


if __name__ == "__main__":
    class_name, exam_name, graph_type = select_class_exam_and_graph()
    if class_name and exam_name and graph_type:
        print(f"\nSelected:")
        print(f"  Class: {class_name}")
        print(f"  Exam: {exam_name}")
        print(f"  Graph: {graph_type}")
    else:
        print("No selection made.")

# File: /home/utkarsh/development/12thProject/group/ByPercent.py
import pandas as pd
from ui.select_data import get_data_file_path
from data.saver import save_grouped_csv_for_source
from data.exporter import export_df_to_excel

def create_grouping_ranges(thresholds):
    # This function creates ranges for grouping percentages.
    # For example, if thresholds are [90,80,70], it makes ranges like [90-100], [80-89], etc.
    # Thresholds should be in descending order.
    if not thresholds or thresholds[0] != 100:
        thresholds = [100] + thresholds  # Add 100 at the start

    # Sort descending and remove 0 if present
    thresholds = sorted([int(t) for t in thresholds if t != 0], reverse=True)

    ranges = []
    for i in range(len(thresholds)):
        if i == len(thresholds) - 1:
            # Last range is from 0 to this threshold
            ranges.append([0, thresholds[i]])
        else:
            # Range from next threshold +1 to this one
            ranges.append([thresholds[i+1] + 1, thresholds[i]])
    return ranges

def groupByPercent(csv_path):
    # This function loads the percentage.csv file and groups students by their percentages in each subject.
    # It asks the user for custom grouping or uses default.
    # Returns the original dataframe with added group columns, and a summary dataframe with counts.
    df = load_percentage_csv(csv_path)

    # Default groups: 90-100, 80-89, etc.
    default_grouping = [[90, 100], [80, 89], [70, 79], [60, 69], [50, 59], [40, 49], [33, 39], [0, 32]]
    print("\nCurrent default grouping:")
    for group in default_grouping:
        print(f"{group[0]} - {group[1]}")
    user_input = input("\nEnter custom grouping thresholds (comma-separated, e.g., 90,80,70,33 or press Enter for default): ")
    if user_input.strip() == "":
        grouping = default_grouping
    else:
        try:
            thresholds = [int(t.strip()) for t in user_input.split(",")]
            # Check if all are between 0 and 100
            valid = True
            for x in thresholds:
                if not (0 <= x <= 100):
                    valid = False
                    break
            if not valid:
                print("Warning: All values should be between 0 and 100. Using default grouping.")
                grouping = default_grouping
            else:
                grouping = create_grouping_ranges(thresholds)
                print("\nCustom grouping created:")
                for group in grouping:
                    print(f"{group[0]}-{group[1]}")
        except:
            print("Invalid input format. Using default grouping.")
            grouping = default_grouping

    def get_group(score):
        # This helper function assigns a group to a score.
        # For example, 85 goes to "80-89"
        if pd.isna(score):
            return "N/A"
        for group in grouping:
            if group[0] <= score <= group[1]:
                return f"{group[0]}-{group[1]}"
        return "Other"

    subjects = get_subjects_from_percentage_df(df)
    if not subjects:
        print("Warning: No subject percentage columns found (expected columns ending with '_%').")
        return df, pd.DataFrame()

    results = []
    for subject in subjects:
        col = f"{subject}_%"  # Column name like "Math_%"
        # Add a new column for the group
        df[f"{subject}_group"] = df[col].apply(get_group)
        # Count how many in each group
        group_counts = df[f"{subject}_group"].value_counts().sort_index(ascending=False)
        subject_result = {'Subject': subject}
        for group, count in group_counts.items():
            subject_result[group] = count
        results.append(subject_result)

    summary_df = pd.DataFrame(results).fillna(0)
    # Rename N/A bucket to Fail
    if 'N/A' in summary_df.columns:
        summary_df = summary_df.rename(columns={'N/A': 'Fail'})
    # Sort numeric band columns by descending start value and keep Fail (and any other non-band) at the end
    band_cols = []
    other_labels = []
    for col in summary_df.columns:
        if col == 'Subject': continue
        if '-' in col and col.split('-')[0].isdigit(): band_cols.append(col)
        else: other_labels.append(col)
    band_cols_sorted = sorted(band_cols, key=lambda x: int(x.split('-')[0]), reverse=True)
    # Ensure 'Fail' shows at the end if present
    tail_labels = [c for c in other_labels if c != 'Fail'] + (['Fail'] if 'Fail' in other_labels else [])
    summary_df = summary_df[['Subject'] + band_cols_sorted + tail_labels]

    # Print a clean, minimal table
    print("\nGrouped Summary (counts):")
    try:
        # Ensure integer-looking values don't show as floats
        display_df = summary_df.copy()
        for c in display_df.columns:
            if c != 'Subject': display_df[c] = display_df[c].astype(int)
        print(display_df.to_string(index=False))
    except Exception:
        # Fallback simple print
        print(summary_df.to_string(index=False))

    return df, summary_df


# Helpers for loading and getting subjects from the percentage CSV.

def load_percentage_csv(csv_path):
    # This function loads the CSV file into a pandas dataframe.
    return pd.read_csv(csv_path)

def get_subjects_from_percentage_df(df):
    # This function finds the subject names from the column names.
    subjects = []
    for col in df.columns:
        if col.endswith('_%') and col != 'Overall_Percentage':
            # Remove the "_%" to get subject name
            subjects.append(col[:-2])
    return subjects


def run_groupByPercent_interactive(base_dir='user-data', filename='percentage.csv'):
    """
    Open the arrow-key selector to choose Class and Exam, resolve the requested
    file path (default: percentage.csv), then run groupByPercent on it.

    """
    path = get_data_file_path(filename, base_dir=base_dir)
    if not path:
        print('No file selected or file not present.')
        return None, None
    # Compute grouping first
    df, summary_df = groupByPercent(path)
    # Auto-save grouped summary next to the source CSV
    try:
        if summary_df is not None and not summary_df.empty:
            out_path = save_grouped_csv_for_source(path, summary_df)
            print(f"Saved grouped summary to: {out_path}")
            export_df_to_excel(summary_df, default_filename="grouped.xlsx", project_root=".")
    except Exception as e:
        print("Could not save grouped.csv:", e)
    return df, summary_df
# File: /home/utkarsh/development/12thProject/index.py
import sys
from typing import Optional, Tuple

# Import the two main flows
try:
    from data.handler import run_pipeline as run_upload_pipeline
except Exception as e:
    print("Warning: Could not import upload pipeline from data/handler.py:", e)
    run_upload_pipeline = None

try:
    from group.ByPercent import run_groupByPercent_interactive
except Exception as e:
    print("Warning: Could not import grouped marks flow from group/ByPercent.py:", e)
    run_groupByPercent_interactive = None

try:
    from ui.view_data import run_view_data
except Exception as e:
    print("Warning: Could not import view data flow from ui/view_data.py:", e)
    run_view_data = None

try:
    from graphs.plot_data import run_plot_data
except Exception as e:
    print("Warning: Could not import plot data flow from graphs/plot_data.py:", e)
    run_plot_data = None


WELCOME = (
    "\n=== Welcome to the Class Results CLI ===\n"
    "This tool helps you:\n"
    "  1) Upload/parse Excel data and save CSV outputs\n"
    "  2) View grouped marks (by percentage)\n"
    "  3) View class data (percentage/grouped/results)\n"
    "  4) Plot graphs and charts from class exam data\n"
)

MENU = (
    "\nMain Menu:\n"
    "  [1] Upload Excel data (run data/handler.py pipeline)\n"
    "  [2] See grouped marks data (run group/ByPercent.py interactive)\n"
    "  [3] View class data (percentage/grouped/results)\n"
    "  [4] Plot graphs and charts (visualize exam data)\n"
    "  [q] Quit\n"
)


def prompt_choice() -> str:
    try:
        choice = input("Enter your choice (1/2/3/4 or q to quit): ").strip().lower()
        # Treat 'esc' as going back to menu (same as pressing Enter here)
        if choice == "esc":
            return ""
        return choice
    except EOFError:
        return "q"
    except KeyboardInterrupt:
        print("\nExiting...")
        return "q"


def run_upload_flow():
    if run_upload_pipeline is None:
        print("Upload pipeline is unavailable due to an import error.")
        return
    print("\n--- Upload/Parse Excel Data ---")
    run_upload_pipeline()
    print("\nUpload flow finished. Returning to main menu...")

def run_grouped_marks_flow():
    if run_groupByPercent_interactive is None:
        print("Grouped marks flow is unavailable due to an import error.")
        return
    print("\n--- Grouped Marks (By Percent) ---")
    df, summary = run_groupByPercent_interactive()
    # Whether or not a file was selected, we return to main menu afterwards.
    print("\nGrouped marks flow finished. Returning to main menu...")

def run_view_data_flow():
    if run_view_data is None:
        print("View data flow is unavailable due to an import error.")
        return
    run_view_data()
    print("\nView data flow finished. Returning to main menu...")

def run_plot_data_flow():
    if run_plot_data is None:
        print("Plot data flow is unavailable due to an import error.")
        return
    print("\n--- Plot Graphs and Charts ---")
    run_plot_data()
    print("\nPlot data flow finished. Returning to main menu...")

def main():
    print(WELCOME)
    while True:
        print(MENU)
        choice = prompt_choice()
        if choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        elif choice == "1":
            run_upload_flow()
        elif choice == "2":
            run_grouped_marks_flow()
        elif choice == "3":
            run_view_data_flow()
        elif choice == "4":
            run_plot_data_flow()
        elif choice == "":
            # Treat empty or 'esc' as re-show menu
            continue
        else:
            print("Invalid choice. Please select 1, 2, 3, 4, or q.")


if __name__ == "__main__":
    main()

# File: /home/utkarsh/development/12thProject/tools/print_summary.py
# This script prints a summary of class results from an Excel file.
# You can run it from command line with options for file and sheet.

# Example usage:
# python tools/print_summary.py --file data/sample/subject-analysis.xlsx --sheet "CLASS IIIB "

import argparse
import sys
from pathlib import Path

# Add the project root to the path so we can import from data.handler
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.handler import print_class_results, save_and_report

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Print class results summary from Excel sheet")
    parser.add_argument("--file", required=False, default=str(PROJECT_ROOT / "data/sample/subject-analysis.xlsx"), help="Path to the Excel file")
    parser.add_argument("--sheet", required=False, default="CLASS IIIB ", help="Sheet name to parse (note: may include trailing space)")
    parser.add_argument("--save", action="store_true", help="Save parsed results to CSV under user-data/<Class>/<Exam>")
    parser.add_argument("--outdir", required=False, default="user-data", help="Base output directory for CSVs (default: user-data)")
    args = parser.parse_args()

    # Print the summary
    print_class_results(args.file, sheet_name=args.sheet)
    # If --save is used, also save to CSV
    if args.save:
        save_and_report(args.file, sheet_name=args.sheet, base_dir=args.outdir)

if __name__ == "__main__":
    main()

# File: /home/utkarsh/development/12thProject/ui/select_data.py
"""Simple terminal UI to select Class and Exam and return the percentage.csv path.
- Uses arrow keys (Up/Down) to navigate, Enter to select, 'q' to quit.
- Press 'd' to delete selected exam data, 'D' (Shift+d) to delete entire class.
- Scans the folder structure: user-data/<Class>/<Exam>/percentage.csv
- Designed to be beginner-friendly and easy to read.

Run directly:
  python3 ui/select_data.py  # uses default base directory: user-data

Use from code:
  from ui.select_data import get_percentage_csv_path
  path = get_percentage_csv_path(base_dir="user-data")
  print(path)
"""

import os
import curses
import shutil


def list_classes(base_dir):
    items = []
    if os.path.isdir(base_dir):
        for name in sorted(os.listdir(base_dir)):
            full = os.path.join(base_dir, name)
            if os.path.isdir(full):
                items.append(name)
    return items


def list_exams(base_dir, class_name):
    root = os.path.join(base_dir, class_name)
    items = []
    if os.path.isdir(root):
        for name in sorted(os.listdir(root)):
            full = os.path.join(root, name)
            if os.path.isdir(full):
                items.append(name)
    return items


def draw_menu(stdscr, title, options, index, show_delete_help=False):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    title_str = title
    stdscr.addstr(1, 2, title_str)
    help_line = "Use Up/Down arrows and Enter. Press q to quit."
    if show_delete_help:
        help_line += " Press 'd' to delete."
    stdscr.addstr(2, 2, help_line)
    top = 4
    for i, opt in enumerate(options):
        marker = ">" if i == index else " "
        line = f" {marker} {opt}"
        if top + i < h - 1:
            stdscr.addstr(top + i, 2, line)
    stdscr.refresh()


def confirm_delete(stdscr, item_name, item_type):
    """Show confirmation dialog for deletion."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    msg1 = f"Are you sure you want to delete {item_type}: {item_name}?"
    msg2 = "This action cannot be undone!"
    msg3 = "Press 'y' to confirm, any other key to cancel."
    
    stdscr.addstr(h // 2 - 2, 2, msg1)
    stdscr.addstr(h // 2 - 1, 2, msg2)
    stdscr.addstr(h // 2 + 1, 2, msg3)
    stdscr.refresh()
    
    key = stdscr.getch()
    return key in (ord('y'), ord('Y'))


def delete_directory(path):
    """Delete a directory and all its contents."""
    try:
        if os.path.exists(path):
            shutil.rmtree(path)
            return True
    except Exception as e:
        print(f"Error deleting: {e}")
    return False


def select_from_list(stdscr, title, options, allow_delete=False, delete_callback=None):
    if not options:
        return None
    index = 0
    while True:
        draw_menu(stdscr, title, options, index, show_delete_help=allow_delete)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            index = (index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j')):
            index = (index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[index]
        elif key in (ord('q'), ord('Q')):
            return None
        elif allow_delete and key in (ord('d'), ord('D')):
            if delete_callback:
                item_to_delete = options[index]
                item_type = "class" if key == ord('D') else "exam"
                if confirm_delete(stdscr, item_to_delete, item_type):
                    success = delete_callback(item_to_delete)
                    if success:
                        options.pop(index)
                        if not options:
                            return None
                        if index >= len(options):
                            index = len(options) - 1


def _curses_select(base_dir):
    classes = list_classes(base_dir)
    if not classes:
        print("No classes found in", base_dir)
        return None

    # Delete callback for classes (Shift+D)
    def delete_class(class_name):
        class_path = os.path.join(base_dir, class_name)
        return delete_directory(class_path)

    selected_class = curses.wrapper(select_from_list, "Select Class (Press 'D' to delete class)", classes, 
                                   allow_delete=True, delete_callback=delete_class)
    if not selected_class:
        return None

    exams = list_exams(base_dir, selected_class)
    if not exams:
        print("No exams found for class:", selected_class)
        return None

    # Delete callback for exams (d)
    def delete_exam(exam_name):
        exam_path = os.path.join(base_dir, selected_class, exam_name)
        return delete_directory(exam_path)

    selected_exam = curses.wrapper(select_from_list, f"Select Exam for {selected_class} (Press 'd' to delete exam)", exams,
                                  allow_delete=True, delete_callback=delete_exam)
    if not selected_exam:
        return None

    return selected_class, selected_exam


def get_percentage_csv_path(base_dir="user-data"):
    # Backwards-compatible helper that delegates to the generic getter
    return get_data_file_path("percentage.csv", base_dir=base_dir)


def get_data_file_path(filename, base_dir="user-data"):
    """Same UI but returns the requested file under <Class>/<Exam>/filename.
    Prints a friendly message if the file is missing.
    """
    try:
        res = _curses_select(base_dir)
        if not res:
            return None
        selected_class, selected_exam = res
        fpath = os.path.join(base_dir, selected_class, selected_exam, filename)
        if not os.path.isfile(fpath):
            # Friendly message like: results data is not present for IIIB UT-2 exam
            name = filename.replace('.csv', '').replace('_', ' ')
            print(name, "data is not present for", selected_class, selected_exam)
            return None
        return fpath
    except Exception as e:
        # Fallback: manual input mode
        print("(Fallback mode) Error starting UI:", e)
        print("Enter selection manually.")
        classes = list_classes(base_dir)
        if not classes:
            print("No classes found.")
            return None
        print("Classes:")
        for i, c in enumerate(classes, 1):
            print(f"  {i}. {c}")
        try:
            ci = int(input("Select class number: ")) - 1
        except Exception:
            return None
        if ci < 0 or ci >= len(classes):
            return None
        selected_class = classes[ci]

        exams = list_exams(base_dir, selected_class)
        if not exams:
            print("No exams found for:", selected_class)
            return None
        print("Exams:")
        for i, e in enumerate(exams, 1):
            print(f"  {i}. {e}")
        try:
            ei = int(input("Select exam number: ")) - 1
        except Exception:
            return None
        if ei < 0 or ei >= len(exams):
            return None
        selected_exam = exams[ei]

        fpath = os.path.join(base_dir, selected_class, selected_exam, filename)
        if not os.path.isfile(fpath):
            name = filename.replace('.csv', '').replace('_', ' ')
            print(name, "data is not present for", selected_class, selected_exam)
            return None
        return fpath


if __name__ == "__main__":
    # Default to selecting percentage.csv; allow custom filename via env var SIMPLE_UI_FILE
    fname = os.environ.get("SIMPLE_UI_FILE", "percentage.csv")
    if fname == "percentage.csv":
        path = get_percentage_csv_path()
    else:
        path = get_data_file_path(fname)
    if path:
        print("Selected:", path)
    else:
        print("No selection.")

# File: /home/utkarsh/development/12thProject/ui/view_data.py
import pandas as pd
import os
import curses
from ui.select_data import list_classes, list_exams

def display_percentage_data(csv_path):
    df = pd.read_csv(csv_path)
    print("\n" + "="*80)
    print("PERCENTAGE DATA")
    print("="*80)
    
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    
    print(df.to_string(index=False))
    print("="*80 + "\n")

def display_grouped_data(csv_path):
    df = pd.read_csv(csv_path)
    print("\n" + "="*80)
    print("GROUPED DATA (Students per percentage range)")
    print("="*80)
    
    for col in df.columns:
        if col != 'Subject' and df[col].dtype == 'float64':
            df[col] = df[col].astype(int)
    
    print(df.to_string(index=False))
    print("="*80 + "\n")

def display_result_data(csv_path):
    df = pd.read_csv(csv_path)
    print("\n" + "="*80)
    print("FULL RESULT DATA")
    print("="*80)
    
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    
    print(df.to_string(index=False))
    print("="*80 + "\n")

def display_all_data(base_path):
    files = ['percentage.csv', 'result.csv', 'grouped.csv']
    
    for filename in files:
        filepath = os.path.join(base_path, filename)
        if os.path.isfile(filepath):
            if filename == 'percentage.csv': display_percentage_data(filepath)
            elif filename == 'result.csv': display_result_data(filepath)
            elif filename == 'grouped.csv': display_grouped_data(filepath)

def draw_menu(stdscr, title, options, index):
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, "Use Up/Down arrows and Enter. Press q to quit.")
    top = 4
    for i, opt in enumerate(options):
        marker = ">" if i == index else " "
        line = f" {marker} {opt}"
        if top + i < h - 1:
            stdscr.addstr(top + i, 2, line)
    stdscr.refresh()

def select_from_list(stdscr, title, options):
    if not options:
        return None
    index = 0
    while True:
        draw_menu(stdscr, title, options, index)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord('k')):
            index = (index - 1) % len(options)
        elif key in (curses.KEY_DOWN, ord('j')):
            index = (index + 1) % len(options)
        elif key in (curses.KEY_ENTER, 10, 13):
            return options[index]
        elif key in (ord('q'), ord('Q')):
            return None

def select_class_and_exam(base_dir='user-data'):
    classes = list_classes(base_dir)
    if not classes:
        print("No classes found in", base_dir)
        return None, None
    
    selected_class = curses.wrapper(select_from_list, "Select Class", classes)
    if not selected_class:
        return None, None
    
    exams = list_exams(base_dir, selected_class)
    if not exams:
        print("No exams found for class:", selected_class)
        return None, None
    
    selected_exam = curses.wrapper(select_from_list, f"Select Exam for {selected_class}", exams)
    if not selected_exam:
        return None, None
    
    return selected_class, selected_exam

def select_data_type():
    options = [
        "Percentage Data",
        "Grouped Data (by percentage ranges)",
        "Full Result Data (marks + percentages)",
        "All Available Data"
    ]
    
    selected = curses.wrapper(select_from_list, "Select Data Type to View", options)
    return selected

def run_view_data(base_dir='user-data'):
    print("\n--- View Class Data ---")
    
    selected_class, selected_exam = select_class_and_exam(base_dir)
    
    if not selected_class or not selected_exam:
        print("No class/exam selected.")
        return
    
    base_path = os.path.join(base_dir, selected_class, selected_exam)
    print(f"\nSelected: {selected_class} - {selected_exam}")
    
    data_type = select_data_type()
    
    if not data_type:
        print("No data type selected.")
        return
    
    if data_type == "Percentage Data":
        filepath = os.path.join(base_path, 'percentage.csv')
        if os.path.isfile(filepath): display_percentage_data(filepath)
        else: print("Percentage data not available for this exam.")
    
    elif data_type == "Grouped Data (by percentage ranges)":
        filepath = os.path.join(base_path, 'grouped.csv')
        if os.path.isfile(filepath): display_grouped_data(filepath)
        else: print("Grouped data not available for this exam.")
    
    elif data_type == "Full Result Data (marks + percentages)":
        filepath = os.path.join(base_path, 'result.csv')
        if os.path.isfile(filepath): display_result_data(filepath)
        else: print("Result data not available for this exam.")
    
    elif data_type == "All Available Data":
        display_all_data(base_path)
