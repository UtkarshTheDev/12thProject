import os
import sys
import shutil
import curses
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


# =====================================================================================
# HELPER FUNCTIONS (from data/utils.py)
# These are small functions that help with common tasks throughout the program.
# =====================================================================================

def coerce_number(x):
    """
    This function takes a value and tries to turn it into a number.
    If the value is empty or something like "NA", it returns a special "Not a Number" value.
    This is useful because data from Excel files can sometimes be messy.
    """
    try:
        if x is None:
            return np.nan
        s = str(x).strip()
        return float(s)
    except (ValueError, TypeError):
        return np.nan

def sanitize_for_path(name):
    """
    This function cleans up a name so it can be used in a file path.
    For example, it replaces "/" with "-" to avoid creating extra folders by mistake.
    """
    if not name:
        return "UNKNOWN"
    return str(name).strip().replace("/", "-").replace("\\", "-").replace(" ", "_")

def find_row_with_text(df, text_to_find, max_rows=30):
    """
    This function looks for a specific piece of text in the first few rows of our data.
    It helps us find important rows, like the one containing the class name or exam name.
    """
    text_lower = text_to_find.lower()
    for i in range(min(max_rows, len(df))):
        row_vals = [str(val) if not pd.isna(val) else "" for val in df.iloc[i]]
        for v in row_vals:
            if text_lower in v.lower():
                return i
    return None

def find_header_and_meta_rows(df):
    """
    This function finds the most important rows in our Excel sheet:
    1. The header row (which has titles like "RollNo", "Total").
    2. The row with the class name (e.g., "CLASS : IIIB").
    3. The row with the exam name (e.g., "NAME OF EXAMINATION").
    """
    header_row = None
    for i in range(min(50, len(df))):
        row_vals = [str(v).strip().lower() for v in df.iloc[i].astype(str).fillna("")]
        has_roll = any(v in ("rollno", "roll no", "roll_no") for v in row_vals)
        has_total = "total" in row_vals
        has_per = any(v in ("per", "%", "percent", "percentage") for v in row_vals)
        if has_roll and (has_total or has_per):
            header_row = i
            break

    class_row = find_row_with_text(df, "CLASS :", 10)
    exam_row = find_row_with_text(df, "NAME OF EXAMINATION", 10)
    return header_row, class_row, exam_row

def parse_exam_and_outof(df, exam_row):
    """
    This function figures out the exam name and the maximum marks for each subject.
    For example, from "UNIT TEST 2(10)", it extracts "UNIT TEST 2" as the name
    and 10 as the marks each subject is out of.
    """
    exam_name = None
    per_subject_out_of = None
    if exam_row is None:
        return None, None

    row = [str(v) if not pd.isna(v) else "" for v in df.iloc[exam_row]]
    for val in row:
        if val.strip() and "NAME OF EXAMINATION" not in val:
            exam_name = val.strip()
            if "(" in exam_name and ")" in exam_name:
                start = exam_name.find("(") + 1
                end = exam_name.find(")")
                inside = exam_name[start:end].strip()
                try:
                    per_subject_out_of = int(float(inside))
                except (ValueError, TypeError):
                    per_subject_out_of = None
                exam_name = exam_name[:start-1].strip()
            break
    return exam_name, per_subject_out_of

def parse_class_name(df, class_row):
    """
    This function finds and returns the class name from its specific row.
    It looks for the text "CLASS :" and then gets the value next to it.
    """
    if class_row is None:
        return None
    row = [str(v) if not pd.isna(v) else "" for v in df.iloc[class_row]]
    for idx, val in enumerate(row):
        if val.strip().upper().startswith("CLASS"):
            if idx + 1 < len(row) and row[idx + 1].strip():
                return row[idx + 1].strip()
    for val in row[1:]:
        if val.strip():
            return val.strip()
    return None


# =====================================================================================
# SUBJECT-RELATED FUNCTIONS (from data/subjects.py)
# These functions help us find the subject columns in the Excel file.
# =====================================================================================

def detect_subject_columns(df, header_row):
    """
    This function is a bit of a detective. It looks at the header row and figures out
    which columns are for subjects (like Math, Science), which one is for the total marks,
    and which one is for the overall percentage.
    """
    headers = [str(v) if v is not None else "" for v in df.iloc[header_row]]
    subjects = []
    subject_to_cols = {}
    total_col = None
    per_col = None

    for ci, header in enumerate(headers):
        label = header.strip().upper()
        if label == "TOTAL":
            total_col = ci
        elif label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci

    end_ci = total_col if total_col is not None else len(headers)
    start_ci = 2  # We assume Roll No and Name are the first two columns

    ci = start_ci
    while ci < end_ci:
        name = headers[ci].strip()
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            marks_col = ci
            percent_col = None
            # Check if the next column is for percentage (sometimes it has the same name or is blank)
            if ci + 1 < end_ci and (headers[ci + 1].strip() == name or headers[ci + 1].strip() == ""):
                percent_col = ci + 1
                ci += 2
            else:
                ci += 1
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": marks_col, "percent": percent_col}
                subjects.append(name)
        else:
            ci += 1
    return subjects, subject_to_cols, total_col, per_col


# =====================================================================================
# EXCEL PARSING FUNCTIONS (from data/parser.py)
# These functions are responsible for reading the Excel file and extracting the data.
# =====================================================================================

def extractDataFromExcel(file_path, sheet_name=None):
    """
    This function reads the data from an Excel file sheet.
    It reads everything as text so we can carefully convert it to numbers later.
    """
    return pd.read_excel(file_path, sheet_name=sheet_name, header=None, dtype=object)

def extract_class_results(file_path, sheet_name=None):
    """
    This is a major function that does the heavy lifting of parsing the Excel sheet.
    It finds all the important information: class name, exam name, subjects, and student marks.
    It also calculates the total and percentage if they are missing.
    """
    df = extractDataFromExcel(file_path, sheet_name=sheet_name)
    if isinstance(df, dict):
        df = next(iter(df.values()))

    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None:
        raise ValueError("Could not find the header row (the one with 'RollNo', 'Total', etc.).")

    exam_name, per_subject_out_of = parse_exam_and_outof(df, exam_row)
    per_subject_out_of = per_subject_out_of or 100
    class_name = parse_class_name(df, class_row)
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(df, header_row)

    students = []
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        try:
            roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError):
            continue

        name_val = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else ""

        marks = {subj: coerce_number(row.iloc[cols.get("marks")]) for subj, cols in subject_to_cols.items()}
        subject_percents = {subj: coerce_number(row.iloc[cols.get("percent")]) for subj, cols in subject_to_cols.items() if cols.get("percent") is not None}

        total = coerce_number(row.iloc[total_col]) if total_col is not None else np.nan
        percent = coerce_number(row.iloc[per_col]) if per_col is not None else np.nan

        if np.isnan(total):
            total = float(np.nansum(list(marks.values())))
        if np.isnan(percent) and per_subject_out_of and subjects:
            total_out_of = per_subject_out_of * len(subjects)
            if total_out_of > 0:
                percent = round((total / total_out_of) * 100, 2)

        if not name_val and all(np.isnan(v) for v in marks.values()):
            continue

        students.append({
            "roll_no": roll_no, "name": name_val, "marks": marks,
            "subject_percentages": subject_percents, "total": total, "percentage": percent,
        })

    result = {
        "class_name": class_name, "exam_name": exam_name, "subjects": subjects,
        "per_subject_out_of": per_subject_out_of, "students": students,
    }
    if per_subject_out_of and subjects:
        result["total_out_of"] = per_subject_out_of * len(subjects)
    return result


# =====================================================================================
# DATA SAVING FUNCTIONS (from data/saver.py and data/exporter.py)
# These functions handle saving our processed data into CSV and Excel files.
# =====================================================================================

def results_to_dataframes(parsed):
    """
    This function takes the parsed data and converts it into two tables (DataFrames):
    1. A full results table with marks, totals, and percentages.
    2. A simpler table with only the percentages for each subject.
    """
    subjects = parsed.get("subjects", [])
    rows_result, rows_percent = [], []
    for s in parsed.get("students", []):
        base = {"Roll No": s.get("roll_no"), "Name": s.get("name", "")}
        row_r, row_p = base.copy(), base.copy()
        for subj in subjects:
            row_r[f"{subj}_Marks"] = s.get("marks", {}).get(subj)
            row_r[f"{subj}_%"] = s.get("subject_percentages", {}).get(subj)
            row_p[f"{subj}_%"] = s.get("subject_percentages", {}).get(subj)
        row_r["Total"] = s.get("total")
        row_r["Percentage"] = s.get("percentage")
        row_p["Overall_Percentage"] = s.get("percentage")
        rows_result.append(row_r)
        rows_percent.append(row_p)
    return pd.DataFrame(rows_result), pd.DataFrame(rows_percent)

def save_class_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    """
    This function saves the processed student data into two CSV files.
    It creates a neat folder structure like "user-data/CLASS_NAME/EXAM_NAME/".
    """
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    class_dir = sanitize_for_path(parsed.get("class_name"))
    exam_dir = sanitize_for_path(parsed.get("exam_name"))
    out_dir = Path(base_dir) / class_dir / exam_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    result_df, percentage_df = results_to_dataframes(parsed)
    result_df.to_csv(out_dir / "result.csv", index=False)
    percentage_df.to_csv(out_dir / "percentage.csv", index=False)
    return out_dir

def export_df_to_excel(df, default_filename="export.xlsx", project_root="."):
    """
    This function asks the user for confirmation and then saves a data table to an Excel file.
    """
    choice = input("Do you want to save this to an Excel file? (y/n): ").strip().lower()
    if choice not in ("y", "yes"):
        print("Cancelled. Not saved.")
        return None

    name = input(f"File name (press Enter for '{default_filename}'): ").strip() or default_filename
    if not name.lower().endswith(".xlsx"):
        name += ".xlsx"

    out_path = os.path.join(project_root, name)
    try:
        df.to_excel(out_path, index=False)
        print("Saved Excel file:", out_path)
        return out_path
    except Exception as e:
        print("Could not save Excel file:", e)
        return None

def save_grouped_csv_for_source(source_csv_path, grouped_df):
    """
    This saves the "grouped" summary table in the same folder as the original data.
    """
    out_path = Path(source_csv_path).parent / "grouped.csv"
    grouped_df.to_csv(out_path, index=False)
    return out_path


# =====================================================================================
# DATA DISPLAY FUNCTIONS (from data/printer.py and ui/view_data.py)
# These functions are for showing the data to the user in a clean, readable format.
# =====================================================================================

def print_parsed_summary(data):
    """
    This function prints a nice summary of the data we extracted from the Excel file.
    """
    print(f"Exam: {data.get('exam_name', 'N/A')} | Class: {data.get('class_name', 'N/A')}")
    print(f"Subjects: {', '.join(data.get('subjects', []))}")
    for s in data.get("students", []):
        print(f"  Roll:{s.get('roll_no')} Name:{s.get('name', '')} Total:{s.get('total', ''):.2f} %:{s.get('percentage', ''):.2f}")

def display_dataframe_data(df, title):
    """A helper to print any data table with a nice title."""
    print("\n" + "="*80)
    print(title.upper())
    print("="*80)
    # Format numbers to two decimal places for a clean look
    for col in df.columns:
        if df[col].dtype == 'float64':
            df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    print(df.to_string(index=False))
    print("="*80 + "\n")


# =====================================================================================
# USER INTERFACE (UI) FUNCTIONS (from ui/select_data.py and ui/view_data.py)
# These functions create the interactive menus for the user to select options.
# =====================================================================================

def draw_menu(stdscr, title, options, index, help_text):
    """A function to draw a menu on the screen using the 'curses' library."""
    stdscr.clear()
    h, w = stdscr.getmaxyx()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, help_text)
    for i, opt in enumerate(options):
        marker = ">" if i == index else " "
        stdscr.addstr(4 + i, 2, f" {marker} {opt}")
    stdscr.refresh()

def select_from_list(stdscr, title, options, help_text):
    """Handles the logic for navigating a menu with arrow keys."""
    index = 0
    while True:
        draw_menu(stdscr, title, options, index, help_text)
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
    """Guides the user to select a class and then an exam from the available data."""
    classes = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    if not classes:
        print("No classes found in", base_dir)
        return None, None

    selected_class = curses.wrapper(select_from_list, "Select Class", classes, "Use Up/Down arrows and Enter. Press q to quit.")
    if not selected_class:
        return None, None

    exam_path = os.path.join(base_dir, selected_class)
    exams = sorted([d for d in os.listdir(exam_path) if os.path.isdir(os.path.join(exam_path, d))])
    if not exams:
        print("No exams found for class:", selected_class)
        return None, None

    selected_exam = curses.wrapper(select_from_list, f"Select Exam for {selected_class}", exams, "Use Up/Down arrows and Enter. Press q to quit.")
    return selected_class, selected_exam


# =====================================================================================
# DATA GROUPING FUNCTIONS (from group/ByPercent.py)
# These functions group students based on their percentage scores.
# =====================================================================================

def create_grouping_ranges(thresholds):
    """Creates percentage ranges like 90-100, 80-89, etc., from a list of numbers."""
    thresholds = sorted([int(t) for t in thresholds if 0 <= t <= 100], reverse=True)
    if 100 not in thresholds:
        thresholds.insert(0, 100)
    ranges = []
    for i in range(len(thresholds)):
        upper = thresholds[i]
        lower = thresholds[i+1] + 1 if i + 1 < len(thresholds) else 0
        ranges.append([lower, upper])
    return ranges

def groupByPercent(csv_path):
    """
    This function groups students into percentage bands (e.g., 90-100%, 80-89%, etc.).
    It asks the user if they want to use default bands or create their own.
    """
    df = pd.read_csv(csv_path)
    default_grouping = [[90, 100], [80, 89], [70, 79], [60, 69], [50, 59], [40, 49], [33, 39], [0, 32]]
    print("\nCurrent default grouping: 90-100, 80-89, 70-79, ...")
    user_input = input("Enter custom grouping thresholds (e.g., 90,80,70,33) or press Enter for default: ")
    grouping = default_grouping
    if user_input.strip():
        try:
            thresholds = [int(t.strip()) for t in user_input.split(",")]
            grouping = create_grouping_ranges(thresholds)
        except ValueError:
            print("Invalid input. Using default grouping.")

    subjects = [col[:-2] for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    summary_data = []
    for subject in subjects:
        col = f"{subject}_%"
        def get_group(score):
            if pd.isna(score): return "N/A"
            for low, high in grouping:
                if low <= score <= high:
                    return f"{low}-{high}"
            return "Other"
        group_counts = df[col].apply(get_group).value_counts()
        subject_result = {'Subject': subject, **group_counts.to_dict()}
        summary_data.append(subject_result)

    summary_df = pd.DataFrame(summary_data).fillna(0)
    display_dataframe_data(summary_df, "Grouped Summary (counts)")
    return df, summary_df


# =====================================================================================
# GRAPH PLOTTING FUNCTIONS (from graphs/plotter.py and graphs/select_graph.py)
# =====================================================================================

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

def select_class_exam_and_graph(base_dir='user-data'):
    """Main function to select class, exam, and graph type."""
    selected_class, selected_exam = select_class_and_exam(base_dir)
    if not selected_class or not selected_exam:
        return None, None, None
    
    graph_types = [
        "Bar Chart - Student Performance", "Subject Comparison - All Students",
        "Line Chart - Performance Trend", "Pie Chart - Pass/Fail Distribution",
        "Horizontal Bar - Student Rankings", "Subject Average - Class Performance",
        "Scatter Plot - Roll No vs Percentage", "Box Plot - Subject Distribution"
    ]
    selected_graph = curses.wrapper(select_from_list, "Select Graph Type", graph_types, "Use arrows and Enter to select.")
    if not selected_graph:
        return None, None, None
    
    return selected_class, selected_exam, selected_graph


# =====================================================================================
# MAIN WORKFLOWS (from index.py, data/handler.py, etc.)
# These functions tie everything together and represent the main actions the user can perform.
# =====================================================================================

def run_upload_pipeline():
    """Workflow #1: Upload and process a new Excel file."""
    print("\n--- Upload/Parse Excel Data ---")
    file_path = input("Please provide the path to your Excel file: ").strip()
    if not file_path:
        print("No file path provided. Returning to menu.")
        return

    try:
        xls = pd.ExcelFile(file_path)
        print("\nAvailable sheets:", ", ".join(xls.sheet_names))
    except Exception as e:
        print(f"(Could not read sheet names: {e})")

    sheet_name = input("Sheet name (press Enter for first sheet): ").strip()
    sheet_name = sheet_name if sheet_name else 0

    base_dir = input("Base directory for saving CSVs (press Enter for 'user-data'): ").strip() or "user-data"

    try:
        print("\nExtracting and saving data...")
        out_dir = save_class_results_to_csv(file_path, sheet_name=sheet_name, base_dir=base_dir)
        print(f"Data saved successfully in: {out_dir}")
    except Exception as e:
        print(f"An error occurred: {e}")
    print("\nUpload flow finished. Returning to main menu...")

def run_groupByPercent_interactive():
    """Workflow #2: View grouped marks for existing data."""
    print("\n--- Grouped Marks (By Percent) ---")
    selected_class, selected_exam = select_class_and_exam('user-data')
    if not (selected_class and selected_exam):
        print("No selection made. Returning to menu.")
        return

    path = os.path.join('user-data', selected_class, selected_exam, 'percentage.csv')
    if not os.path.isfile(path):
        print(f"The file 'percentage.csv' was not found for {selected_class} - {selected_exam}.")
        return

    _, summary_df = groupByPercent(path)
    if summary_df is not None and not summary_df.empty:
        save_grouped_csv_for_source(path, summary_df)
        export_df_to_excel(summary_df, default_filename="grouped.xlsx")
    print("\nGrouped marks flow finished. Returning to main menu...")

def run_view_data_flow():
    """Workflow #3: View different data tables (results, percentages, etc.)."""
    print("\n--- View Class Data ---")
    selected_class, selected_exam = select_class_and_exam('user-data')
    if not (selected_class and selected_exam):
        print("No selection made. Returning to menu.")
        return

    base_path = os.path.join('user-data', selected_class, selected_exam)
    print(f"\nSelected: {selected_class} - {selected_exam}")

    options = ["Percentage Data", "Grouped Data", "Full Result Data", "All Available Data"]
    data_type = curses.wrapper(select_from_list, "Select Data Type to View", options, "Use arrows and Enter to select.")

    if not data_type:
        print("No data type selected.")
        return

    files_to_display = {
        "Percentage Data": ["percentage.csv"],
        "Grouped Data": ["grouped.csv"],
        "Full Result Data": ["result.csv"],
        "All Available Data": ["percentage.csv", "result.csv", "grouped.csv"]
    }
    titles = {"percentage.csv": "Percentage Data", "grouped.csv": "Grouped Data", "result.csv": "Full Result Data"}

    for filename in files_to_display.get(data_type, []):
        filepath = os.path.join(base_path, filename)
        if os.path.isfile(filepath):
            df = pd.read_csv(filepath)
            display_dataframe_data(df, titles[filename])
        else:
            print(f"{titles[filename]} is not available for this exam.")
    print("\nView data flow finished. Returning to main menu...")

def run_plot_graphs_flow(base_dir='user-data'):
    """Workflow #4: Select and plot graphs for existing data."""
    print("\n--- Plot Graphs and Charts ---")
    class_name, exam_name, graph_type = select_class_exam_and_graph(base_dir)
    
    if not class_name or not exam_name or not graph_type:
        print("\nNo selection made. Exiting.")
        return
    
    csv_path = os.path.join(base_dir, class_name, exam_name, 'percentage.csv')
    
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
    print("\nPlot graphs flow finished. Returning to main menu...")


# =====================================================================================
# MAIN PROGRAM EXECUTION
# This is where the program starts. It shows the main menu and calls the correct workflow.
# =====================================================================================

def main():
    """The main function that runs the whole program."""
    print("\n=== Welcome to the Class Results CLI ===")
    while True:
        print("\nMain Menu:")
        print("  [1] Upload Excel data")
        print("  [2] See grouped marks data")
        print("  [3] View class data")
        print("  [4] Plot graphs and charts")
        print("  [clear] Clear screen")
        print("  [q] Quit")
        choice = input("Enter your choice (1/2/3/4, clear, or q): ").strip().lower()

        if choice == "1":
            run_upload_pipeline()
        elif choice == "2":
            run_groupByPercent_interactive()
        elif choice == "3":
            run_view_data_flow()
        elif choice == "4":
            run_plot_graphs_flow()
        elif choice == "clear":
            os.system('cls' if os.name == 'nt' else 'clear')
            print("\n=== Welcome to the Class Results CLI ===")
        elif choice in ("q", "quit", "exit"):
            print("Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")

# This line checks if the script is being run directly.
# If it is, it calls the main() function to start the program.
if __name__ == "__main__":
    main()