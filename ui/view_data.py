import pandas as pd
import os
import curses
from .select_data import (
    select_class_exam,
    select_from_list,
    select_from_list_no_curses,
    CURSES_ENABLED,
)
from group.ByPercent import group_by_percent
from data.exporter import export_df_to_excel
from data.printer import display_df
from pathlib import Path


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
            if f == "grouped.csv":
                print(f"    {f} not available.")
                choice = (
                    input("    Would you like to generate grouped data now? [y/N]: ")
                    .strip()
                    .lower()
                )
                if choice == "y":
                    path = os.path.join(base_path, "percentage.csv")
                    if not os.path.isfile(path):
                        print(
                            f"    Error: 'percentage.csv' not found, cannot generate grouped data."
                        )
                        continue

                    _, summary_df = group_by_percent(path)

                    # Ask to save
                    save_choice = (
                        input(
                            "    Do you want to save this grouped data to Excel/CSV? [y/N]: "
                        )
                        .strip()
                        .lower()
                    )
                    if save_choice == "y":
                        (Path(path).parent / "grouped.csv").write_text(
                            summary_df.to_csv(index=False)
                        )
                        export_df_to_excel(summary_df, fname="grouped.xlsx")
                        print("    Saved grouped.csv and grouped.xlsx")
                else:
                    print(
                        "    You can generate it later using Option 2 (Group Data by Percentage)."
                    )
            else:
                print(f"    {f} not available.")
