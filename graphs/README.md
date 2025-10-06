# Graphs Module - Plot Class Exam Data

This module provides an easy way to visualize class exam data with different types of graphs and charts.

## Features

### Available Graph Types

1. **Bar Chart - Student Performance**
   - Shows overall percentage for each student
   - Easy to compare student performance at a glance

2. **Subject Comparison - All Students**
   - Grouped bar chart comparing all students across different subjects
   - See which subjects students perform best/worst in

3. **Line Chart - Performance Trend**
   - Line graph showing performance trends across students
   - Good for seeing overall class patterns

4. **Pie Chart - Pass/Fail Distribution**
   - Shows percentage of students who passed (>=35%) vs failed
   - Quick overview of class success rate

5. **Horizontal Bar - Student Rankings**
   - Students ranked by performance with color coding
   - Red (<35%), Orange (35-60%), Green (>60%)
   - Easier to read student names

6. **Subject Average - Class Performance**
   - Average percentage for each subject
   - Identifies strong and weak subjects for the class
   - Color coded by performance level

7. **Scatter Plot - Roll No vs Percentage**
   - Shows relationship between roll number and performance
   - Color coded by performance level

8. **Box Plot - Subject Distribution**
   - Shows distribution of marks in each subject
   - Displays median, quartiles, and outliers
   - Good for understanding spread of marks

## How to Use

### From Main Menu (index.py)
1. Run `python index.py`
2. Select option `[4] Plot graphs and charts`
3. Select your class using arrow keys
4. Select your exam
5. Select the graph type you want to see
6. The graph will be displayed

### Run Directly
```bash
python graphs/plot_data.py
```

### From Code
```python
from graphs.plot_data import run_plot_data

run_plot_data(base_dir='user-data')
```

## Requirements

The module requires:
- pandas (for reading CSV data)
- matplotlib (for creating graphs)

Install with:
```bash
pip install pandas matplotlib
```

## Data Structure

The module reads from `percentage.csv` files stored in:
```
user-data/
  ├── ClassName/
  │   ├── ExamName/
  │   │   ├── percentage.csv  (Used for plotting)
  │   │   ├── result.csv
  │   │   └── grouped.csv
```

## File Structure

```
graphs/
  ├── __init__.py          # Module initialization
  ├── plotter.py           # All plotting functions
  ├── select_graph.py      # UI for selecting class/exam/graph
  ├── plot_data.py         # Main runner script
  └── README.md            # This file
```

## Notes

- All graphs are color-coded for easy understanding
- Graphs are displayed using matplotlib's interactive viewer
- You can zoom, pan, and save graphs from the viewer
- Simple, beginner-friendly code with no complex logic
- No type hints used for easier readability
