import curses
import glob
import os
import shutil
import sys
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from thefuzz import process

# [[BANNER-CODE-START]]
# This section contains the title and footer banners.
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


def show_title():
    print(title)


def show_footer():
    print(footer)


# [[BANNER-CODE-END]]

# --- Curses compatibility check ---
CURSES_ENABLED = False
try:
    # Test if curses can be initialized. This will fail in IDEs like IDLE.
    if sys.stdout and hasattr(sys.stdout, "fileno"):
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
        if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"):
            return np.nan
        return float(s)
    except (ValueError, TypeError):
        return np.nan


def sanitize_for_path(name):
    return (
        str(name).strip().replace("/", "-").replace("\\", "-").replace(" ", "_")
        if name
        else "UNKNOWN"
    )


def find_row_with_text(df, text, max_rows=30):
    text_lower = text.lower()
    for i in range(min(max_rows, len(df))):
        if any(text_lower in str(v).lower() for v in df.iloc[i] if not pd.isna(v)):
            return i
    return None


def find_header_and_meta_rows(df):
    header_row = None
    for i in range(min(50, len(df))):
        row_vals = [str(v).strip().lower() for v in df.iloc[i].astype(str).fillna("")]
        if any(v in ("rollno", "roll no", "roll_no") for v in row_vals) and (
            "total" in row_vals
            or any(v in ("per", "%", "percent", "percentage") for v in row_vals)
        ):
            header_row = i
            break
    return (
        header_row,
        find_row_with_text(df, "CLASS :", 10),
        find_row_with_text(df, "NAME OF EXAMINATION", 10),
    )


def parse_exam_and_outof(df, exam_row):
    if exam_row is None:
        return None, None
    for val in (str(v) for v in df.iloc[exam_row] if not pd.isna(v)):
        if val.strip() and "NAME OF EXAMINATION" not in val:
            exam_name = val.strip()
            if "(" in exam_name and ")" in exam_name:
                start, end = exam_name.find("(") + 1, exam_name.find(")")
                try:
                    per_subject_out_of = int(float(exam_name[start:end].strip()))
                except (ValueError, TypeError):
                    per_subject_out_of = None
                return exam_name[: start - 1].strip(), per_subject_out_of
            return exam_name, None
    return None, None


def parse_class_name(df, class_row):
    if class_row is None:
        return None
    row = [str(v) for v in df.iloc[class_row] if not pd.isna(v)]
    for idx, val in enumerate(row):
        if (
            val.strip().upper().startswith("CLASS")
            and idx + 1 < len(row)
            and row[idx + 1].strip()
        ):
            return row[idx + 1].strip()
    for val in row[1:]:
        if val.strip():
            return val.strip()
    return None


def detect_subject_columns(df, header_row):
    headers = [
        str(v) if v is not None and not (isinstance(v, float) and np.isnan(v)) else ""
        for v in df.iloc[header_row]
    ]
    subjects, subject_to_cols, total_col, per_col = [], {}, None, None

    for ci, h in enumerate(headers):
        label = h.strip().upper()
        if label == "TOTAL":
            total_col = ci
        elif label in ("PER", "%", "PERCENT", "PERCENTAGE"):
            per_col = ci

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
    if isinstance(df, dict):
        df = next(iter(df.values()))
    header_row, class_row, exam_row = find_header_and_meta_rows(df)
    if header_row is None:
        raise ValueError("Header row not found.")
    exam_name, _ = parse_exam_and_outof(df, exam_row)
    per_subject_out_of = 100
    class_name = parse_class_name(df, class_row)
    subjects, subject_to_cols, total_col, per_col = detect_subject_columns(
        df, header_row
    )
    students = []
    for r in range(header_row + 1, len(df)):
        row = df.iloc[r]
        try:
            roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError):
            continue
        name = (
            str(row.iloc[1]).strip()
            if len(row) > 1 and not pd.isna(row.iloc[1])
            else ""
        )

        marks, subject_percentages = {}, {}
        for s in subjects:
            cols = subject_to_cols[s]
            marks_val = (
                coerce_number(row.iloc[cols.get("marks")])
                if cols.get("marks") is not None and cols.get("marks") < len(row)
                else np.nan
            )
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

    result = {
        "class_name": class_name,
        "exam_name": exam_name,
        "subjects": subjects,
        "per_subject_out_of": per_subject_out_of,
        "students": students,
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
        rows_r.append(row_r)
        rows_p.append(row_p)
    return pd.DataFrame(rows_r), pd.DataFrame(rows_p)


def save_results_to_csv(file_path, sheet_name=None, base_dir="user-data"):
    parsed = extract_class_results(file_path, sheet_name=sheet_name)
    out_dir = (
        Path(base_dir)
        / sanitize_for_path(parsed.get("class_name"))
        / sanitize_for_path(parsed.get("exam_name"))
    )
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
        except Exception as e:
            print("    Error:", e)
    return None


def display_df(df, title):
    # Create a copy to avoid modifying the original DataFrame
    df_display = df.copy()

    # Format float columns to integers
    for col in df_display.select_dtypes(include=["float64"]).columns:
        df_display[col] = df_display[col].apply(
            lambda x: str(int(round(x))) if pd.notna(x) else ""
        )

    # Convert all columns to string type for consistent width calculation
    for col in df_display.columns:
        df_display[col] = df_display[col].astype(str)

    # Calculate the maximum width for each column
    col_widths = {
        col: max(len(col), df_display[col].str.len().max())
        for col in df_display.columns
    }

    # Create the header string with padding and a separator
    header = " | ".join(
        f"{col.upper():<{col_widths[col]}}" for col in df_display.columns
    )
    separator = "-+-".join("-" * col_widths[col] for col in df_display.columns)

    # Print the title centered above the table
    table_width = len(header)
    print(f"\n    {title.upper().center(table_width)}")
    print(f"    {'=' * table_width}")

    # Print the header and separator
    print(f"    {header}")
    print(f"    {separator}")

    # Print each row with proper padding
    for _, row in df_display.iterrows():
        row_str = " | ".join(
            f"{row[col]:<{col_widths[col]}}" for col in df_display.columns
        )
        print(f"    {row_str}")

    # Print the bottom border of the table
    print(f"    {'=' * table_width}\n")


def draw_menu(stdscr, title, opts, idx, help_text):
    stdscr.clear()
    stdscr.addstr(1, 2, title)
    stdscr.addstr(2, 2, help_text)
    for i, opt in enumerate(opts):
        stdscr.addstr(4 + i, 2, f" {'>' if i == idx else ' '} {opt}")
    stdscr.refresh()


def select_from_list(stdscr, title, opts, help_text):
    idx = 0
    while True:
        draw_menu(stdscr, title, opts, idx, help_text)
        key = stdscr.getch()
        if key in (curses.KEY_UP, ord("k")):
            idx = (idx - 1) % len(opts)
        elif key in (curses.KEY_DOWN, ord("j")):
            idx = (idx + 1) % len(opts)
        elif key in (curses.KEY_ENTER, 10, 13):
            return opts[idx]
        elif key in (ord("q"), ord("Q")):
            return None


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


def select_from_list_no_curses(title, opts, help_text):
    print(f"\n    --- {title} ---")
    for i, opt in enumerate(opts):
        print(f"    {i + 1}. {opt}")
    print(f"    (Enter 'q' to quit)")

    while True:
        choice = input("    Select an option: ").strip().lower()
        if choice == "q":
            return None
        try:
            idx = int(choice) - 1
            if 0 <= idx < len(opts):
                return opts[idx]
            else:
                print("    Invalid number. Please try again.")
        except ValueError:
            print("    Please enter a number.")


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


def fuzzy_search_file_select_no_curses():
    search_term = ""
    while True:
        search_term = input(
            "\n    Enter search term to find Excel file (or 'q' to quit): "
        ).strip()
        if not search_term or search_term.lower() == "q":
            return None

        all_files = glob.glob("**/*.xlsx", recursive=True)
        if not all_files:
            print(
                "    No .xlsx files found in the current directory or subdirectories."
            )
            continue

        matches = process.extract(search_term, all_files, limit=10)
        search_results = [match[0] for match in matches if match[1] > 30]

        if not search_results:
            print("    No matches found.")
            continue

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


def select_class_exam(base_dir="user-data"):
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )
    if not classes:
        return None, None

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
    exams = sorted(
        [
            d
            for d in os.listdir(os.path.join(base_dir, s_class))
            if os.path.isdir(os.path.join(base_dir, s_class, d))
        ]
    )
    if not exams:
        return None, None

    if CURSES_ENABLED:
        s_exam = curses.wrapper(
            select_from_list, f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )
    else:
        s_exam = select_from_list_no_curses(
            f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit."
        )

    return s_class, s_exam


def group_by_percent(csv_path):
    df = pd.read_csv(csv_path)
    user_input = input("Custom grouping (e.g., 90,80,33) or Enter for default: ")
    thresholds = sorted(
        [int(t) for t in user_input.split(",")]
        if user_input
        else [90, 80, 70, 60, 50, 40, 33],
        reverse=True,
    )
    if 100 not in thresholds:
        thresholds.insert(0, 100)
    grouping = [
        [(thresholds[i + 1] + 1 if i + 1 < len(thresholds) else 0), thresholds[i]]
        for i in range(len(thresholds))
    ]
    subjects = [
        c[:-2] for c in df.columns if c.endswith("_%") and c != "Overall_Percentage"
    ]
    summary = []
    for subj in subjects:

        def get_group(score):
            if pd.isna(score):
                return "N/A"
            for low, high in grouping:
                if low <= score <= high:
                    return f"{low}-{high}"
            return "Other"

        summary.append(
            {
                "Subject": subj,
                **df[f"{subj}_%"].apply(get_group).value_counts().to_dict(),
            }
        )
    summary_df = pd.DataFrame(summary).fillna(0)
    display_df(summary_df, "Grouped Summary (counts)")
    return df, summary_df


def plot_chart(df, x, y, title, xl, yl, kind="bar", rot=45, figsize=(12, 6), **kwargs):
    plt.figure(figsize=figsize)
    if kind == "bar":
        plt.bar(df[x], df[y], **kwargs)
    elif kind == "line":
        plt.plot(df[x], df[y], marker="o", **kwargs)
    elif kind == "scatter":
        plt.scatter(df[x], df[y], **kwargs)
    plt.title(title, fontsize=14, fontweight="bold")
    plt.xlabel(xl, fontsize=12)
    plt.ylabel(yl, fontsize=12)
    plt.xticks(rotation=rot, ha="right")
    plt.ylim(0, 100)
    plt.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    plt.show()


def fuzzy_search_file_select(stdscr):
    search_term = ""
    selected_index = 0
    all_files = glob.glob("**/*.xlsx", recursive=True)
    search_results = []

    curses.curs_set(1)
    stdscr.nodelay(0)

    while True:
        stdscr.clear()

        # Display Title and Search Prompt
        stdscr.addstr(1, 2, "Search for an Excel File")
        stdscr.addstr(
            2, 2, "Type to search, Up/Down to navigate, Enter to select, 'q' to quit."
        )
        stdscr.addstr(4, 4, f"Search: {search_term}")

        # Perform search if search_term is not empty
        if search_term:
            matches = process.extract(search_term, all_files, limit=10)
            search_results = [match for match in matches if match[1] > 30]
        else:
            search_results = []

        # Display search results
        if search_results:
            display_line = 6
            for i, (file_path, score) in enumerate(search_results):
                filename = os.path.basename(file_path)
                display_text = f"{filename} ({score}%)"

                if i == selected_index:
                    stdscr.addstr(
                        display_line, 2, f"> {display_text}", curses.A_REVERSE
                    )
                else:
                    stdscr.addstr(display_line, 2, f"  {display_text}")
                display_line += 1
                stdscr.addstr(display_line, 6, f"Path: {file_path}")  # Indented path
                display_line += 2  # Extra line for spacing
        elif search_term:
            stdscr.addstr(6, 2, "  No matches found.")

        stdscr.move(4, 12 + len(search_term))  # Move cursor to end of search term
        stdscr.refresh()

        key = stdscr.getch()

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
        elif key in (ord("q"), ord("Q"), 27):  # 27 is escape key
            return None
        elif 32 <= key <= 126:  # Printable characters
            search_term += chr(key)
            selected_index = 0


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
        sheets = pd.ExcelFile(fpath).sheet_names
        print("    Sheets:", ", ".join(sheets))
        sheet = input("    Sheet name (Enter for first): ").strip() or 0
        s_dir = input("    Save directory ('user-data'): ").strip() or "user-data"
        out = save_results_to_csv(fpath, sheet_name=sheet, base_dir=s_dir)
        print(f"    Saved to: {out}")
    except Exception as e:
        print(f"    Error: {e}")


def group_by_percent_interactive():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    path = os.path.join("user-data", s_class, s_exam, "percentage.csv")
    if not os.path.isfile(path):
        print(f"    'percentage.csv' not found for {s_class} - {s_exam}.")
        return
    _, summary_df = group_by_percent(path)
    if not summary_df.empty:
        (Path(path).parent / "grouped.csv").write_text(summary_df.to_csv(index=False))
        export_df_to_excel(summary_df, fname="grouped.xlsx")


def view_data_flow():
    s_class, s_exam = select_class_exam("user-data")
    if not (s_class and s_exam):
        return
    base_path = os.path.join("user-data", s_class, s_exam)
    opts = ["Percentage", "Grouped", "Full Result", "All"]

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
    files = {
        "Percentage": ["percentage.csv"],
        "Grouped": ["grouped.csv"],
        "Full Result": ["result.csv"],
        "All": ["percentage.csv", "result.csv", "grouped.csv"],
    }
    for f in files.get(dtype, []):
        fpath = os.path.join(base_path, f)
        if os.path.isfile(fpath):
            display_df(pd.read_csv(fpath), f.replace(".csv", " Data").title())
        else:
            print(f"    {f} not available.")


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


def delete_data_flow(base_dir="user-data"):
    classes = sorted(
        [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
    )
    if not classes:
        print("    No classes found.")
        return

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


def main():
    # [[BANNER-CODE-START]]
    show_title()
    # [[BANNER-CODE-END]]

    # --- Create user-data directory if it doesn't exist ---
    if not os.path.exists("user-data"):
        os.makedirs("user-data")

    actions = {
        "1": upload_pipeline,
        "2": group_by_percent_interactive,
        "3": view_data_flow,
        "4": plot_graphs_flow,
        "5": delete_data_flow,
    }

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
        while True:
            print(menu_text)
            choice = input("\n    Enter your choice: ").strip().lower()
            if choice in actions:
                actions[choice]()
            elif choice == "clear":
                os.system("cls" if os.name == "nt" else "clear")
                # [[BANNER-CODE-START]]
                show_title()
                # [[BANNER-CODE-END]]
            elif choice in ("q", "quit"):
                break
            else:
                print("    Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\n    Operation cancelled by user.")
        pass
    finally:
        # [[BANNER-CODE-START]]
        show_footer()
        # [[BANNER-CODE-END]]


if __name__ == "__main__":
    main()
