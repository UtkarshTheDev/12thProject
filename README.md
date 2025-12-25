# Student Result Management System (Class 12th CS Project)

A comprehensive Python application designed to analyze, manage, and visualize student examination results from Excel sheets. This project parses raw result data, organizes it, and provides tools for statistical analysis and graphical representation.

> Idea Given By Mam

## Features

- **📂 Excel Data Import:** Seamless parsing of result sheets with automatic detection of subjects, marks, and student details. Supports fuzzy search to quickly find Excel files in the directory.
- **📊 Data Visualization:** Generate insights using Bar Charts, Line Charts, and Scatter Plots to analyze class performance.
- **📈 Statistical Analysis:** Automatically calculates percentages and totals. Groups students based on custom or default percentage thresholds.
- **💾 Organized Storage:** Keeps processed data structured by Class and Exam name in a local `user-data` database (CSV format).
- **🖥️ Interactive Interface:** Features a user-friendly CLI menu with support for keyboard navigation (using `curses`) and a compatibility mode for standard terminals.
- **🗑️ Data Management:** Built-in tools to view and safely delete old class or exam records.

## Requirements

Ensure you have Python installed. The project relies on the following external libraries:

- `pandas` (Data manipulation)
- `numpy` (Numerical operations)
- `matplotlib` (Plotting graphs)
- `thefuzz` (Fuzzy string matching for file search)
- `openpyxl` (Excel file reading backend)

## Installation

1. Clone this repository or download the source code.
2. Install the required dependencies:

   ```bash
   pip install pandas numpy matplotlib thefuzz openpyxl
   ```

   *Note: Windows users might need `windows-curses` for the full UI experience, though the script includes a fallback mode.*

## Usage

1. Place your raw Result Excel files (`.xlsx`) in the project directory.
2. Run the main script:

   ```bash
   python merged_script.py
   ```

3. Follow the on-screen menu to:
   - **Upload:** Select and process an Excel file.
   - **Group:** Create summary statistics based on percentage ranges.
   - **View:** Display result tables in the terminal.
   - **Plot:** Visualize the data.
   - **Delete:** Remove unwanted data.

## Project Structure

- `merged_script.py`: The main application code containing logic for parsing, UI, and plotting.
- `user-data/`: Automatically generated directory where processed CSV files are stored, organized by Class and Exam.
