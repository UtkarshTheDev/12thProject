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
