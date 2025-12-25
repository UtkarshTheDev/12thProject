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

You can install the package directly from the source code.

1. Clone this repository or download the source code.
2. Navigate to the project directory.
3. Install using pip:

   ```bash
   pip install .
   ```

   For development (editable mode), use:
   ```bash
   pip install -e .
   ```

   *Note: Windows users might need `windows-curses` for the full UI experience.*

## Usage

Once installed, you can run the application from anywhere using the command:

```bash
student-result-manager
```

Alternatively, you can run it as a Python module:

```bash
python -m student_result_manager
```

1. Place your raw Result Excel files (`.xlsx`) in the directory where you are running the command.
2. Follow the on-screen menu to:
   - **Upload:** Select and process an Excel file.
   - **Group:** Create summary statistics based on percentage ranges.
   - **View:** Display result tables in the terminal.
   - **Plot:** Visualize the data.
   - **Delete:** Remove unwanted data.

## Project Structure

- `student_result_manager/`: The main package containing source code.
  - `main.py`: Entry point.
  - `data/`: Data parsing and handling logic.
  - `ui/`: User interface components.
  - `graphs/`: Plotting and visualization logic.
  - `group/`: Grouping logic.
- `user-data/`: Automatically generated directory where processed CSV files are stored, organized by Class and Exam.
