import os, sys, shutil, curses
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
# [[BANNER-CODE-START]]
# This section imports and displays the title and footer banners.
# You can safely remove this entire block if you don't want the banners.
try:
    from banners import title, footer
    def show_title(): print(title)
    def show_footer(): print(footer)
except ImportError:
    def show_title(): print("\n    === Welcome to the Class Results CLI ===")
    def show_footer(): print("    Goodbye!")
# [[BANNER-CODE-END]]

def coerce_number(x):
    try:
        s = str(x).strip()
        if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"): return np.nan
        return float(s)
    except (ValueError, TypeError): return np.nan

def sanitize_for_path(name):
    return str(name).strip().replace("/", "-").replace("\\", "-").replace(" ", "_") if name else "UNKNOWN"

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
        name = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
        
        marks, subject_percentages = {}, {}
        for s in subjects:
            cols = subject_to_cols[s]
            marks[s] = coerce_number(row.iloc[cols.get("marks")]) if cols.get("marks") is not None else np.nan
            subject_percentages[s] = coerce_number(row.iloc[cols.get("percent")]) if cols.get("percent") is not None and cols.get("percent") < len(row) else np.nan

        total = coerce_number(row.iloc[total_col]) if total_col is not None else np.nan
        if np.isnan(total):
            total = np.nansum(list(marks.values()))

        percent = coerce_number(row.iloc[per_col]) if per_col is not None else np.nan
        if np.isnan(percent) and per_subject_out_of and subjects:
            denom = per_subject_out_of * len(subjects)
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
        result["total_out_of"] = per_subject_out_of * len(subjects)
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
    print(f"\n    {'='*80}\n    {title.upper()}\n    {'='*80}")
    for col in df.select_dtypes(include=['float64']).columns: df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    print("    " + df.to_string(index=False).replace("\n", "\n    "))
    print(f"    {'='*80}\n")

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

def select_class_exam(base_dir='user-data'):
    classes = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    if not classes: return None, None
    s_class = curses.wrapper(select_from_list, "Select Class", classes, "Up/Down, Enter, q to quit.")
    if not s_class: return None, None
    exams = sorted([d for d in os.listdir(os.path.join(base_dir, s_class)) if os.path.isdir(os.path.join(base_dir, s_class, d))])
    if not exams: return None, None
    return s_class, curses.wrapper(select_from_list, f"Exam for {s_class}", exams, "Up/Down, Enter, q to quit.")

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

def upload_pipeline():
    fpath = input("Excel file path: ").strip()
    if not fpath: return
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
    if not os.path.isfile(path):
        print(f"    'percentage.csv' not found for {s_class} - {s_exam}.")
        return
    _, summary_df = group_by_percent(path)
    if not summary_df.empty:
        (Path(path).parent / "grouped.csv").write_text(summary_df.to_csv(index=False))
        export_df_to_excel(summary_df, fname="grouped.xlsx")

def view_data_flow():
    s_class, s_exam = select_class_exam('user-data')
    if not (s_class and s_exam): return
    base_path = os.path.join('user-data', s_class, s_exam)
    opts = ["Percentage", "Grouped", "Full Result", "All"]
    dtype = curses.wrapper(select_from_list, "Select Data to View", opts, "Up/Down, Enter, q to quit.")
    if not dtype: return
    files = {"Percentage": ["percentage.csv"], "Grouped": ["grouped.csv"], "Full Result": ["result.csv"], "All": ["percentage.csv", "result.csv", "grouped.csv"]}
    for f in files.get(dtype, []):
        fpath = os.path.join(base_path, f)
        if os.path.isfile(fpath): display_df(pd.read_csv(fpath), f.replace('.csv', ' Data').title())
        else: print(f"    {f} not available.")

def plot_graphs_flow(base_dir='user-data'):
    c_name, e_name = select_class_exam(base_dir)
    if not (c_name and e_name): return
    g_type = curses.wrapper(select_from_list, "Select Graph Type", ["Bar Chart", "Line Chart", "Scatter Plot"], "Up/Down, Enter, q to quit.")
    if not g_type: return
    csv_path = os.path.join(base_dir, c_name, e_name, 'percentage.csv')
    if not os.path.isfile(csv_path):
        print(f"    percentage.csv not found for {c_name} - {e_name}")
        return
    df = pd.read_csv(csv_path)
    title = f'{g_type} - {c_name} - {e_name}'
    if "Bar" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='bar')
    elif "Line" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='line')
    elif "Scatter" in g_type: plot_chart(df, 'Roll No', 'Overall_Percentage', title, 'Roll Number', 'Percentage (%)', kind='scatter')

def delete_data_flow(base_dir='user-data'):
    classes = sorted([d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))])
    if not classes:
        print("    No classes found.")
        return

    selected_class, action = curses.wrapper(select_with_delete, "Select Class", classes, "Up/Down, Enter to view exams, d to delete class, q to quit.")
    if not selected_class:
        return

    if action == 'delete':
        confirm = input(f"    Are you sure you want to permanently delete all data for class '{selected_class}'? [y/N]: ").strip().lower()
        if confirm == 'y':
            try:
                shutil.rmtree(os.path.join(base_dir, selected_class))
                print(f"    Successfully deleted class '{selected_class}'.")
            except Exception as e:
                print(f"    Error deleting class '{selected_class}': {e}")
        else:
            print("    Deletion cancelled.")
        return

    class_path = os.path.join(base_dir, selected_class)
    exams = sorted([d for d in os.listdir(class_path) if os.path.isdir(os.path.join(class_path, d))])
    if not exams:
        print(f"    No exams found for class '{selected_class}'.")
        return

    selected_exam, action = curses.wrapper(select_with_delete, f"Exams for {selected_class}", exams, "Up/Down, d to delete exam, q to quit.")
    if not selected_exam:
        return

    if action == 'delete':
        confirm = input(f"    Are you sure you want to permanently delete exam '{selected_exam}' for class '{selected_class}'? [y/N]: ").strip().lower()
        if confirm == 'y':
            try:
                shutil.rmtree(os.path.join(class_path, selected_exam))
                print(f"    Successfully deleted exam '{selected_exam}' for class '{selected_class}'.")
            except Exception as e:
                print(f"    Error deleting exam '{selected_exam}': {e}")
        else:
            print("    Deletion cancelled.")

def main():
    # [[BANNER-CODE-START]]
    show_title()
    # [[BANNER-CODE-END]]
    actions = {'1': upload_pipeline, '2': group_by_percent_interactive, '3': view_data_flow, '4': plot_graphs_flow, '5': delete_data_flow}
    
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
                os.system('cls' if os.name == 'nt' else 'clear')
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
        print("\n    Credits:")
        show_footer()
        # [[BANNER-CODE-END]]

if __name__ == "__main__":
    main();
