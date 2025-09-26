# This script prints a summary of class results from an Excel file.
# You can run it from command line with options for file and sheet.

# Example usage:
# python tools/print_summary.py --file data/sample/subject-analysis.xlsx --sheet "CLASS IIIB "

import argparse
import sys
from pathlib import Path

# Add the project root to the path so we can import from data.handler
CURRENT_FILE = Path(__file__).resolve()
PROJECT_ROOT = CURRENT_FILE.parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from data.handler import print_class_results, save_and_report

def main():
    # Set up command line arguments
    parser = argparse.ArgumentParser(description="Print class results summary from Excel sheet")
    parser.add_argument("--file", required=False, default=str(PROJECT_ROOT / "data/sample/subject-analysis.xlsx"), help="Path to the Excel file")
    parser.add_argument("--sheet", required=False, default="CLASS IIIB ", help="Sheet name to parse (note: may include trailing space)")
    parser.add_argument("--save", action="store_true", help="Save parsed results to CSV under user-data/<Class>/<Exam>")
    parser.add_argument("--outdir", required=False, default="user-data", help="Base output directory for CSVs (default: user-data)")
    args = parser.parse_args()

    # Print the summary
    print_class_results(args.file, sheet_name=args.sheet)
    # If --save is used, also save to CSV
    if args.save:
        save_and_report(args.file, sheet_name=args.sheet, base_dir=args.outdir)

if __name__ == "__main__":
    main()
