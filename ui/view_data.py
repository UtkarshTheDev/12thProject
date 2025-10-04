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
            if filename == 'percentage.csv':
                display_percentage_data(filepath)
            elif filename == 'result.csv':
                display_result_data(filepath)
            elif filename == 'grouped.csv':
                display_grouped_data(filepath)

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
        if os.path.isfile(filepath):
            display_percentage_data(filepath)
        else:
            print("Percentage data not available for this exam.")
    
    elif data_type == "Grouped Data (by percentage ranges)":
        filepath = os.path.join(base_path, 'grouped.csv')
        if os.path.isfile(filepath):
            display_grouped_data(filepath)
        else:
            print("Grouped data not available for this exam.")
    
    elif data_type == "Full Result Data (marks + percentages)":
        filepath = os.path.join(base_path, 'result.csv')
        if os.path.isfile(filepath):
            display_result_data(filepath)
        else:
            print("Result data not available for this exam.")
    
    elif data_type == "All Available Data":
        display_all_data(base_path)
