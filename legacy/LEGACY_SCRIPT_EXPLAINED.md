# Legacy Script: Line-by-Line Explanation

This document provides an exhaustive, line-by-line breakdown of the `legacy/merged_script.py` file. This script is a monolithic implementation of the Result Analysis tool, containing all logic for data parsing, terminal UI, and visualization in a single file.

---

## Imports (Lines 1-12)
- **Line 1 (`import curses`)**: Imports the `curses` library, which is used to create text-based user interfaces (TUI) in the terminal. It handles keyboard input (like arrow keys) and screen drawing.
- **Line 2 (`import glob`)**: Imports `glob`, a module used to find all the pathnames matching a specified pattern (e.g., finding all `.xlsx` files).
- **Line 3 (`import os`)**: Imports `os`, providing a way of using operating system dependent functionality like creating folders or joining paths.
- **Line 4 (`import shutil`)**: Imports `shutil`, which offers high-level file operations. Here, it's used to delete entire directory trees.
- **Line 5 (`import sys`)**: Imports `sys`, which provides access to some variables used or maintained by the interpreter and functions that interact strongly with the interpreter.
- **Line 6 (`from pathlib import Path`)**: Imports `Path` from `pathlib`, which offers an object-oriented approach to handling filesystem paths.
- **Line 8 (`import matplotlib.pyplot as plt`)**: Imports the plotting module of `matplotlib`, renamed to `plt` for brevity. This is used to generate graphs.
- **Line 9 (`import numpy as np`)**: Imports `numpy` as `np`. It is primarily used here for handling "Not a Number" (`nan`) values in datasets.
- **Line 10 (`import pandas as pd`)**: Imports `pandas` as `pd`. This is the core library used for reading Excel files, managing data tables, and saving CSVs.
- **Line 11 (`from thefuzz import process`)**: Imports `process` from `thefuzz`, used for fuzzy string matching (finding files even with typos).

---

## Banner Definitions (Lines 13-46)
- **Lines 15-22**: Defines the variable `title`. This is a multi-line string containing the ASCII art "RESULT ANALYSIS" that appears when the script starts.
- **Lines 24-34**: Defines the variable `footer`. This is a multi-line string containing ASCII art for "THANK YOU" that appears when the script exits.
- **Lines 37-38**: Defines `show_title()`, a simple function that prints the `title` banner to the console.
- **Lines 41-42**: Defines `show_footer()`, a simple function that prints the `footer` banner to the console.

---

## Curses Compatibility Check (Lines 47-61)
- **Line 48 (`CURSES_ENABLED = False`)**: Sets a default flag to `False`.
- **Line 49 (`try:`)**: Starts a block to test if the terminal supports `curses`.
- **Line 51 (`if sys.stdout and hasattr(sys.stdout, "fileno"):`)**: Checks if the output stream exists and has a file descriptor (required for `curses`).
- **Line 52 (`stdscr = curses.initscr()`)**: Tries to initialize the `curses` screen.
- **Line 53 (`curses.endwin()`)**: Immediately closes the `curses` screen if initialization succeeded.
- **Line 54 (`del stdscr`)**: Deletes the screen object from memory.
- **Line 55 (`CURSES_ENABLED = True`)**: If the above lines didn't crash, we know `curses` works.
- **Line 56-57**: If the check in line 51 fails, we keep `CURSES_ENABLED` as `False`.
- **Line 58-60**: If an error occurs during `curses.initscr()`, the `except` block catches it and ensures `CURSES_ENABLED` is `False`.

---

## Function: `coerce_number` (Lines 64-72)
*This function safely converts any input into a float or `NaN`.*
- **Line 64 (`def coerce_number(x):`)**: Defines the function with input `x`.
- **Line 65 (`try:`)**: Starts a block to handle conversion.
- **Line 66 (`s = str(x).strip()`)**: Converts the input to a string and removes any surrounding whitespace.
- **Line 67 (`if s.upper() in ("", "NA", "N/A", "#DIV/0!", "-", "AB", "A"):`)**: Checks if the value represents a common "empty" or "absent" indicator.
- **Line 68 (`return np.nan`)**: Returns `NaN` if the check in line 67 is true.
- **Line 69 (`return float(s)`)**: Tries to convert the cleaned string into a decimal number.
- **Line 70-71**: If `float(s)` fails (e.g., input was "Hello"), it returns `NaN`.

---

## Function: `sanitize_for_path` (Lines 74-80)
*This function cleans strings so they can be used as folder names.*
- **Line 74 (`def sanitize_for_path(name):`)**: Defines the function.
- **Lines 75-76**: Converts the name to a string, removes whitespace, and replaces slashes (`/`, `\`) with dashes and spaces with underscores.
- **Lines 77-78**: If `name` is empty or None, it returns the string "UNKNOWN".

---

## Function: `find_row_with_text` (Lines 82-88)
*Searches for a specific word in an Excel table.*
- **Line 82 (`def find_row_with_text(df, text, max_rows=30):`)**: Defines the function, searching up to 30 rows by default.
- **Line 83 (`text_lower = text.lower()`)**: Converts search text to lowercase for case-insensitive matching.
- **Line 84 (`for i in range(min(max_rows, len(df))):`)**: Loops through the first few rows of the DataFrame.
- **Line 85**: Checks every cell in the current row (`df.iloc[i]`). If the search text is found inside any cell, it enters the block.
- **Line 86 (`return i`)**: Returns the index of the row where the text was found.
- **Line 87 (`return None`)**: Returns `None` if the text was never found.

---

## Function: `find_header_and_meta_rows` (Lines 90-105)
*Locates important landmark rows in the Excel sheet.*
- **Line 91 (`header_row = None`)**: Initializes the variable.
- **Line 92 (`for i in range(min(50, len(df))):`)**: Searches the first 50 rows.
- **Line 93**: Extracts all values from the row, cleans them, and puts them in a list `row_vals`.
- **Lines 94-97**: Checks if the row contains "Roll No" AND either "Total" or a "Percentage" keyword. This identifies the main student table header.
- **Line 98 (`header_row = i`)**: Saves the row index.
- **Line 99 (`break`)**: Stops searching once found.
- **Lines 100-104**: Returns a tuple containing the header row index, the row index for "CLASS :", and the row index for "NAME OF EXAMINATION".

---

## Function: `parse_exam_and_outof` (Lines 107-122)
*Extracts the exam name and the maximum possible marks.*
- **Line 107**: Defines the function taking the DataFrame and the row index where exam info is.
- **Line 110**: Iterates through every cell in that row.
- **Line 111**: Skips the cell if it's empty or just contains the label "NAME OF EXAMINATION".
- **Line 112 (`exam_name = val.strip()`)**: Stores the cell content.
- **Line 113**: If the string has parentheses `(...)`, it might contain the "Out Of" value.
- **Lines 114-118**: Extracts the text inside the parentheses and tries to convert it to an integer (e.g., "(100)" becomes `100`).
- **Line 119**: Returns the exam name (everything before the parentheses) and the "out of" value.
- **Line 120-121**: Returns just the name if no parentheses exist, or `None` if nothing was found.

---

## Function: `parse_class_name` (Lines 124-139)
*Extracts the class name (e.g., 12th A) from the sheet.*
- **Lines 127-128**: Gets the row content and starts looping through it.
- **Lines 129-130**: If a cell starts with "CLASS", it checks the very next cell.
- **Line 134 (`return row[idx + 1].strip()`)**: Returns the content of the next cell as the class name.
- **Lines 135-137**: If the "CLASS" label wasn't found but the row has data, it returns the first non-empty cell after the first one.

---

## Function: `detect_subject_columns` (Lines 141-184)
*Identifies which columns belong to which subjects.*
- **Lines 142-145**: Gets the text from the header row.
- **Line 146**: Initializes lists and dictionaries to store results.
- **Lines 148-153**: Loops through headers to find the specific column index for "TOTAL" and "PERCENTAGE".
- **Line 155 (`end_ci = ...`)**: Determines where subjects end (usually before the Total column).
- **Line 156 (`ci = 2 ...`)**: Starts looking for subjects from the 3rd column (skipping Roll No and Name).
- **Line 158 (`name = headers[ci].strip()`)**: Gets the subject name.
- **Lines 162-164**: If the next column has the exact same name, it's assumed to be that subject's percentage column.
- **Lines 165-173**: If the next column is empty, it checks the next 10 students' data. If they look like percentages (0-100), it's treated as a percentage column.
- **Lines 179-180**: Stores the column indices for the subject's marks and (optional) percentage.

---

## Function: `extract_class_results` (Lines 186-262)
*The core parsing logic that reads every student.*
- **Line 187**: Reads the Excel file into a Pandas DataFrame.
- **Lines 190-198**: Calls the previous helper functions to find headers, class name, exam name, and subject columns.
- **Lines 200-201**: Loops through every row starting after the header.
- **Lines 202-205**: Tries to get the Roll Number. If it's not a number, it skips the row (likely the end of the table).
- **Lines 206-210**: Gets the student's name from the second column.
- **Lines 213-225**: For every subject detected, it gets the marks from the correct column and calculates a percentage based on `per_subject_out_of` (default 100).
- **Lines 227-236**: Calculates the sum of marks (Total) and the overall percentage for that student.
- **Lines 238-239**: If the name is missing and all marks are empty, it skips the student.
- **Lines 240-249**: Saves the student's details into a dictionary and adds it to the `students` list.
- **Lines 251-261**: Packages all findings (class name, subjects, students) into a final `result` dictionary.

---

## Function: `results_to_dfs` (Lines 264-278)
*Converts the parsed dictionary into Pandas DataFrames.*
- **Line 268**: Creates a base dictionary with Roll No and Name.
- **Lines 270-272**: Adds subject marks to one row and subject percentages to another.
- **Lines 273-274**: Adds the final Total and Overall Percentage.
- **Lines 275-276**: Appends these rows to lists.
- **Line 277**: Returns two DataFrames (one for raw marks, one for percentages).

---

## Function: `save_results_to_csv` (Lines 280-292)
*Saves the processed data into folders.*
- **Line 281**: Parses the file.
- **Lines 282-286**: Builds a folder path: `user-data/[Class]/[Exam]`.
- **Line 287**: Creates those folders if they don't exist.
- **Line 288**: Gets the DataFrames.
- **Lines 289-290**: Saves them as `result.csv` and `percentage.csv` in the new folder.

---

## Function: `export_df_to_excel` (Lines 294-305)
*Allows the user to save a table as an .xlsx file.*
- **Line 295**: Asks the user if they want to save to Excel.
- **Line 296**: Asks for a filename, providing a default.
- **Line 297**: Ensures the filename ends with `.xlsx`.
- **Line 299**: Uses Pandas to write the file.

---

## Function: `display_df` (Lines 307-351)
*Prints a DataFrame in a beautiful table format in the terminal.*
- **Line 309**: Makes a copy of the data.
- **Lines 312-315**: Rounds decimal numbers to integers for a cleaner look.
- **Lines 318-319**: Converts everything to strings to measure text width.
- **Lines 322-325**: Calculates the maximum width for every column so they align perfectly.
- **Lines 328-331**: Creates a header string and a separator line (e.g., `+---+---`).
- **Lines 333-336**: Prints the table title, centered and underlined.
- **Lines 343-347**: Loops through every row and prints the cells with proper spacing (`|` separators).

---

## Curses UI Functions (Lines 353-392)
- **`draw_menu` (353-360)**: Clears the screen and draws the menu options, highlighting the currently selected one with a `>`.
- **`select_from_list` (362-375)**: An interactive loop. It waits for the user to press Up/Down keys to change `idx`, or Enter to select the current option.
- **`select_with_delete` (377-392)**: Similar to `select_from_list`, but also listens for the 'd' key to indicate that the user wants to delete the selected item.

---

## Non-Curses UI Functions (Lines 394-440)
- **`select_from_list_no_curses` (394-412)**: A fallback menu. It prints a list of numbers and uses `input()` to get the user's choice.
- **`select_with_delete_no_curses` (414-440)**: Fallback for deletion. It tells users to type `d1` to delete item 1.

---

## Function: `fuzzy_search_file_select_no_curses` (Lines 442-480)
*Simple file search for terminals that don't support Curses.*
- **Line 445**: Asks for a search term.
- **Line 451**: Uses `glob` to find every `.xlsx` file in the project.
- **Line 458**: Uses `thefuzz` to compare the search term against all file paths.
- **Line 459**: Keeps only matches with a score higher than 30%.
- **Lines 465-475**: Shows the top 10 matches and asks the user to pick one by number.

---

## Function: `select_class_exam` (Lines 482-520)
*Lets the user pick a Class and then an Exam from the `user-data` folder.*
- **Lines 483-485**: Lists all folders in `user-data` (these are the Classes).
- **Lines 489-496**: Shows the class selection menu (using Curses if available, otherwise fallback).
- **Lines 500-506**: Lists all folders inside the selected Class folder (these are the Exams).
- **Lines 510-517**: Shows the exam selection menu.

---

## Function: `group_by_percent` (Lines 522-560)
*Calculates how many students fall into specific percentage ranges.*
- **Line 524**: Asks the user for custom ranges (e.g., "90,80,33").
- **Lines 525-532**: Turns that input into a sorted list of numbers, adding 100 at the top.
- **Lines 533-536**: Creates "ranges" (e.g., 91-100, 81-90).
- **Lines 541-556**: For every subject, it counts how many students are in each range using Pandas' `value_counts`.
- **Lines 557-558**: Displays the final summary table.

---

## Function: `plot_chart` (Lines 562-578)
*The engine that draws graphs.*
- **Line 563**: Creates a new blank figure (the canvas).
- **Lines 564-569**: Checks the `kind` variable. If it's "bar", it draws bars; if "line", it draws a line; if "scatter", it draws dots.
- **Lines 570-572**: Adds the title and labels to the X and Y axes.
- **Line 574**: Sets the Y-axis limit from 0 to 100.
- **Line 577**: Displays the window with the finished graph.

---

## Function: `fuzzy_search_file_select` (Lines 580-645)
*The advanced "Search-as-you-type" file selector.*
- **Line 586**: Shows the typing cursor.
- **Line 589**: Starts an infinite loop for the search interface.
- **Line 597**: Displays the current `search_term`.
- **Lines 600-602**: Whenever the user types a character, it recalculates the best matching files.
- **Lines 607-621**: Displays the results. The selected one is highlighted in reverse colors (`curses.A_REVERSE`).
- **Line 628**: Waits for a key press.
- **Line 630-644**: If it's Enter, return the file. If it's Backspace, remove a character. If it's a normal letter, add it to the search term.

---

## Functional Flows (Lines 647-862)
*These functions connect the UI to the logic.*
- **`upload_pipeline` (647-669)**: Runs the file search, asks for a sheet name, parses the Excel, and saves the CSVs.
- **`group_by_percent_interactive` (671-683)**: Lets the user pick an exam, calculates the groups, and offers to save the summary to Excel.
- **`view_data_flow` (685-715)**: Lets the user pick an exam and which file they want to see (Marks, Percentages, or Groups), then prints it.
- **`plot_graphs_flow` (717-770)**: Lets the user pick an exam and a graph type, then calls `plot_chart`.
- **`delete_data_flow` (772-862)**: Provides menus to select a Class or Exam and uses `shutil.rmtree` to permanently delete that folder from `user-data`.

---

## Main Function (Lines 864-919)
- **Lines 866**: Shows the title banner.
- **Lines 870-871**: Creates the `user-data` folder if it's missing so the script doesn't crash later.
- **Lines 873-879**: Maps the numbers "1" through "5" to the functions defined above.
- **Line 881-895**: Defines the text for the Main Menu box.
- **Line 898**: Starts the main program loop.
- **Line 900**: Asks for the user's choice.
- **Lines 901-902**: If the choice is 1-5, it runs that function.
- **Line 903-907**: If the user types "clear", it wipes the terminal screen and reshshows the title.
- **Line 908-909**: If "q", it exits the loop.
- **Lines 912-914**: Handles `Ctrl+C` (KeyboardInterrupt) gracefully.
- **Line 917**: Shows the footer "Thank You" banner before the program fully closes.

---

## Execution (Lines 921-922)
- **Line 921 (`if __name__ == "__main__":`)**: This is a Python standard. It ensures the `main()` function only runs if this script is executed directly, not if it's imported by another script.
- **Line 922 (`main()`)**: Calls the main function to start the program.
