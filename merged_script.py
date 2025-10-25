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
    def show_title(): print("\n=== Welcome to the Class Results CLI ===")
    def show_footer(): print("Goodbye!")
# [[BANNER-CODE-END]]

def coerce_number(x):
    try:
        s = str(x).strip()
        return float(s) if s else np.nan
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
    headers = [str(v).strip() for v in df.iloc[header_row]]
    subjects, subject_to_cols, total_col, per_col = [], {}, None, None
    for ci, h in enumerate(headers):
        if h.upper() == "TOTAL": total_col = ci
        elif h.upper() in ("PER", "%", "PERCENT", "PERCENTAGE"): per_col = ci
    end_ci = total_col if total_col is not None else len(headers)
    ci = 2
    while ci < end_ci:
        name = headers[ci]
        if name and name.upper() not in ("ROLLNO", "ROLL NO", "TOTAL", "PER"):
            percent_col = ci + 1 if ci + 1 < end_ci and (headers[ci + 1] == name or headers[ci + 1] == "") else None
            if name not in subject_to_cols:
                subject_to_cols[name] = {"marks": ci, "percent": percent_col}
                subjects.append(name)
            ci += 2 if percent_col else 1
        else: ci += 1
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
        try: roll_no = int(float(str(row.iloc[0])))
        except (ValueError, TypeError, IndexError): continue
        name = str(row.iloc[1]).strip() if len(row) > 1 and not pd.isna(row.iloc[1]) else ""
        marks = {s: coerce_number(row.iloc[c.get("marks")]) for s, c in subject_to_cols.items()}
        total = coerce_number(row.iloc[total_col]) if total_col is not None else np.nansum(list(marks.values()))
        percent = coerce_number(row.iloc[per_col]) if per_col is not None else (round((total / (per_subject_out_of * len(subjects))) * 100, 2) if per_subject_out_of and subjects else np.nan)
        if not name and all(np.isnan(v) for v in marks.values()): continue
        students.append({"roll_no": roll_no, "name": name, "marks": marks, "total": total, "percentage": percent})
    result = {"class_name": class_name, "exam_name": exam_name, "subjects": subjects, "per_subject_out_of": per_subject_out_of, "students": students}
    if per_subject_out_of and subjects: result["total_out_of"] = per_subject_out_of * len(subjects)
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
            print("Saved:", out_path)
            return out_path
        except Exception as e: print("Error:", e)
    return None

def display_df(df, title):
    print(f"\n{'='*80}\n{title.upper()}\n{'='*80}")
    for col in df.select_dtypes(include=['float64']).columns: df[col] = df[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "")
    print(df.to_string(index=False))
    print(f"{ '='*80}\n")

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
    elif kind == 'pie': plt.pie(df[y], labels=df[x], autopct='%1.1f%%', **kwargs)
    elif kind == 'barh': plt.barh(df[x], df[y], **kwargs)
    elif kind == 'scatter': plt.scatter(df[x], df[y], **kwargs)
    plt.title(title, fontsize=14, fontweight='bold'); plt.xlabel(xl, fontsize=12); plt.ylabel(yl, fontsize=12)
    plt.xticks(rotation=rot, ha='right'); plt.ylim(0, 100); plt.grid(axis='y', alpha=0.3)
    plt.tight_layout(); plt.show()

def upload_pipeline():
    fpath = input("Excel file path: ").strip()
    if not fpath: return
    try:
        sheets = pd.ExcelFile(fpath).sheet_names
        print("Sheets:", ", ".join(sheets))
        sheet = input("Sheet name (Enter for first): ").strip() or 0
        s_dir = input("Save directory ('user-data'): ").strip() or "user-data"
        out = save_results_to_csv(fpath, sheet_name=sheet, base_dir=s_dir)
        print(f"Saved to: {out}")
    except Exception as e: print(f"Error: {e}")

def group_by_percent_interactive():
    s_class, s_exam = select_class_exam('user-data')
    if not (s_class and s_exam): return
    path = os.path.join('user-data', s_class, s_exam, 'percentage.csv')
    if not os.path.isfile(path):
        print(f"'percentage.csv' not found for {s_class} - {s_exam}.")
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
        else: print(f"{f} not available.")

def plot_graphs_flow(base_dir='user-data'):
    c_name, e_name = select_class_exam(base_dir)
    if not (c_name and e_name): return
    g_type = curses.wrapper(select_from_list, "Select Graph Type", ["Bar Chart", "Line Chart", "Pie Chart", "Horizontal Bar", "Scatter Plot"], "Up/Down, Enter, q to quit.")
    if not g_type: return
    csv_path = os.path.join(base_dir, c_name, e_name, 'percentage.csv')
    if not os.path.isfile(csv_path):
        print(f"percentage.csv not found for {c_name} - {e_name}")
        return
    df = pd.read_csv(csv_path)
    title = f'{g_type} - {c_name} - {e_name}'
    if "Bar" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='barh' if 'Horizontal' in g_type else 'bar')
    elif "Line" in g_type: plot_chart(df, 'Name', 'Overall_Percentage', title, 'Students', 'Percentage (%)', kind='line')
    elif "Pie" in g_type:
        pass_fail = pd.DataFrame({'Status': ['Pass (>=35%)', 'Fail (<35%)'], 'Count': [len(df[df['Overall_Percentage'] >= 35]), len(df[df['Overall_Percentage'] < 35])]})
        plot_chart(pass_fail, 'Status', 'Count', title, '', '', kind='pie', figsize=(8,8))
    elif "Scatter" in g_type: plot_chart(df, 'Roll No', 'Overall_Percentage', title, 'Roll Number', 'Percentage (%)', kind='scatter')

def main():
    # [[BANNER-CODE-START]]
    show_title()
    # [[BANNER-CODE-END]]
    actions = {'1': upload_pipeline, '2': group_by_percent_interactive, '3': view_data_flow, '4': plot_graphs_flow}
    try:
        while True:
            print("\nMenu:\n1.Upload 2.Group 3.View 4.Plot [clear, q]")
            choice = input("Choice: ").strip().lower()
            if choice in actions: actions[choice]()
            elif choice == "clear": os.system('cls' if os.name == 'nt' else 'clear')
            elif choice in ("q", "quit"): break
            else: print("Invalid choice.")
    except KeyboardInterrupt:
        pass
    finally:
        # [[BANNER-CODE-START]]
        print("Credits:")
        show_footer()
        # [[BANNER-CODE-END]]

if __name__ == "__main__":
    main();
