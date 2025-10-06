# Plotting Feature - Quick Start Guide

## Overview
This new feature allows you to visualize class exam data with 8 different types of graphs and charts!

## Installation

First, make sure you have the required packages installed:

```bash
pip install pandas matplotlib numpy openpyxl
```

Or use the requirements file:
```bash
pip install -r requirements.txt
```

## How to Use

### Method 1: From Main Menu (Recommended)

1. Run the main application:
   ```bash
   python index.py
   ```

2. Select option **[4] Plot graphs and charts**

3. Use arrow keys (Up/Down) to navigate through:
   - **Select Class** - Choose which class data to view
   - **Select Exam** - Choose which exam to visualize
   - **Select Graph Type** - Choose from 8 different graph types

4. The graph will be displayed in a new window

5. You can:
   - Zoom in/out
   - Pan around
   - Save the graph as an image
   - Close the window to return to the menu

### Method 2: Run Directly

```bash
python graphs/plot_data.py
```

## Available Graph Types

### 1. Bar Chart - Student Performance
- Shows each student's overall percentage
- Best for: Quick comparison of all students

### 2. Subject Comparison - All Students
- Grouped bars showing all students across all subjects
- Best for: Comparing performance across different subjects

### 3. Line Chart - Performance Trend
- Line graph connecting student performances
- Best for: Seeing overall class trends

### 4. Pie Chart - Pass/Fail Distribution
- Shows percentage of students who passed vs failed
- Best for: Quick overview of class success rate

### 5. Horizontal Bar - Student Rankings
- Students sorted by performance with color coding
- Best for: Easy reading of student names and rankings
- Colors: Red (<35%), Orange (35-60%), Green (>60%)

### 6. Subject Average - Class Performance
- Average marks for each subject
- Best for: Identifying strong and weak subjects
- Shows exact percentages on bars

### 7. Scatter Plot - Roll No vs Percentage
- Dots showing roll number against performance
- Best for: Spotting patterns or outliers

### 8. Box Plot - Subject Distribution
- Shows median, quartiles, and range for each subject
- Best for: Understanding mark distribution and spread

## Tips

- **Navigation**: Use Up/Down arrow keys or j/k keys to move
- **Select**: Press Enter to select an option
- **Quit**: Press 'q' at any time to go back or quit
- **Graph Window**: Close the graph window to return to the menu
- **Multiple Views**: You can view multiple graphs one after another

## Data Requirements

The plotting feature uses `percentage.csv` files from your data:
```
user-data/
  └── ClassName/
      └── ExamName/
          └── percentage.csv  ← This file is used
```

Make sure you have uploaded and processed Excel data first (Option 1 in main menu).

## Example Workflow

1. Upload Excel data (Option 1)
2. Process data to create CSVs
3. Plot graphs (Option 4)
4. Select class: "IIIA"
5. Select exam: "UT-1"
6. Select graph: "Bar Chart - Student Performance"
7. View and analyze the graph!

## Troubleshooting

**Problem**: "percentage.csv not found"
- **Solution**: Make sure you've uploaded and processed the Excel data first using Option 1

**Problem**: "No classes found"
- **Solution**: Check that the `user-data` folder has class folders with exam data

**Problem**: Graph doesn't display
- **Solution**: Make sure matplotlib is installed: `pip install matplotlib`

**Problem**: Terminal UI not working
- **Solution**: Make sure your terminal supports curses (most do by default)

## Code Structure

```
graphs/
  ├── __init__.py          # Module initialization
  ├── plotter.py           # 8 plotting functions (simple, no complex code)
  ├── select_graph.py      # UI for selection (follows select_data.py pattern)
  ├── plot_data.py         # Main runner (ties everything together)
  └── README.md            # Detailed documentation
```

## Features

✅ Simple, beginner-friendly code
✅ No type hints or complex Python features
✅ 8 different graph types
✅ Color-coded visualizations
✅ Interactive graph viewer
✅ Easy navigation with arrow keys
✅ Follows existing UI patterns
✅ Proper folder structure

Enjoy visualizing your class data! 📊📈
