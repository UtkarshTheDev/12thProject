"""Main script to run the plotting feature.
This script lets users select class, exam, and graph type, then displays the graph.
"""

import os
from graphs.select_graph import select_class_exam_and_graph
from graphs.plotter import (
    plot_bar_chart,
    plot_subject_comparison,
    plot_line_chart,
    plot_pie_chart,
    plot_horizontal_bar,
    plot_subject_average,
    plot_scatter,
    plot_box_plot
)


def run_plot_data(base_dir='user-data'):
    """Main function to run the plotting feature."""
    print("\n" + "="*60)
    print("         PLOT CLASS EXAM DATA")
    print("="*60)
    print("\nSelect class, exam, and graph type to visualize data.\n")
    
    # Get user selections
    class_name, exam_name, graph_type = select_class_exam_and_graph(base_dir)
    
    if not class_name or not exam_name or not graph_type:
        print("\nNo selection made. Exiting.")
        return
    
    # Build path to percentage.csv
    csv_path = os.path.join(base_dir, class_name, exam_name, 'percentage.csv')
    
    # Check if file exists
    if not os.path.isfile(csv_path):
        print(f"\nError: percentage.csv not found for {class_name} - {exam_name}")
        print(f"Expected path: {csv_path}")
        return
    
    print(f"\n{'='*60}")
    print(f"Class: {class_name}")
    print(f"Exam: {exam_name}")
    print(f"Graph: {graph_type}")
    print(f"{'='*60}\n")
    print("Loading data and generating graph...\n")
    
    # Call the appropriate plotting function based on selection
    try:
        if "Bar Chart" in graph_type:
            plot_bar_chart(csv_path, class_name, exam_name)
        
        elif "Subject Comparison" in graph_type:
            plot_subject_comparison(csv_path, class_name, exam_name)
        
        elif "Line Chart" in graph_type:
            plot_line_chart(csv_path, class_name, exam_name)
        
        elif "Pie Chart" in graph_type:
            plot_pie_chart(csv_path, class_name, exam_name)
        
        elif "Horizontal Bar" in graph_type:
            plot_horizontal_bar(csv_path, class_name, exam_name)
        
        elif "Subject Average" in graph_type:
            plot_subject_average(csv_path, class_name, exam_name)
        
        elif "Scatter Plot" in graph_type:
            plot_scatter(csv_path, class_name, exam_name)
        
        elif "Box Plot" in graph_type:
            plot_box_plot(csv_path, class_name, exam_name)
        
        else:
            print("Unknown graph type selected.")
        
        print("\nGraph displayed successfully!")
        
    except Exception as e:
        print(f"\nError generating graph: {e}")
        print("Please make sure the data file has the required columns.")


if __name__ == "__main__":
    run_plot_data()
