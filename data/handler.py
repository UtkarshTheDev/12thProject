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
    if not file_path:
        print("No file path provided. Exiting.")
        return

    sheet_name = input("Sheet name (press Enter for default/first sheet): ").strip() or None
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


