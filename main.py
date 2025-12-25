import curses
import os
import shutil
import sys
import pandas as pd

from ui import banners
from ui.select_data import (
    select_with_delete,
    select_with_delete_no_curses,
    fuzzy_search_file_select,
    fuzzy_search_file_select_no_curses,
    CURSES_ENABLED,
)
from ui.view_data import view_data_flow
from data.saver import save_results_to_csv
from graphs.plot_data import plot_graphs_flow
from group.ByPercent import group_by_percent_interactive


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
        s_dir = "user-data"
        print("    Class data stored on the user-data folder")
        out = save_results_to_csv(fpath, sheet_name=sheet, base_dir=s_dir)
        print(f"    Saved to: {out}")
    except Exception as e:
        print(f"    Error: {e}")


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
    banners.show_title()

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
                banners.show_title()
            elif choice in ("q", "quit"):
                break
            else:
                print("    Invalid choice. Please try again.")
    except KeyboardInterrupt:
        print("\n    Operation cancelled by user.")
        pass
    finally:
        banners.show_footer()


if __name__ == "__main__":
    main()
