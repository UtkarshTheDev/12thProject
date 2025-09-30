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
