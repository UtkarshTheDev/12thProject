"""Simple plotting functions for class exam data.
This module provides easy-to-use functions to create different types of charts.
"""

import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_bar_chart(csv_path, class_name, exam_name):
    """Create a bar chart showing overall percentage for each student."""
    df = pd.read_csv(csv_path)
    
    plt.figure(figsize=(12, 6))
    
    if 'Overall_Percentage' in df.columns:
        students = df['Name'].tolist()
        percentages = df['Overall_Percentage'].tolist()
        
        plt.bar(students, percentages, color='skyblue', edgecolor='navy')
        plt.xlabel('Students', fontsize=12)
        plt.ylabel('Percentage (%)', fontsize=12)
        plt.title(f'Student Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
        plt.xticks(rotation=45, ha='right')
        plt.ylim(0, 100)
        plt.grid(axis='y', alpha=0.3)
        plt.tight_layout()
        plt.show()
    else:
        print("Overall_Percentage column not found in data.")


def plot_subject_comparison(csv_path, class_name, exam_name):
    """Create a grouped bar chart comparing all students across subjects."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    students = df['Name'].tolist()
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    bar_width = 0.8 / len(subject_cols)
    x_positions = range(len(students))
    
    for i, subject_col in enumerate(subject_cols):
        subject_name = subject_col.replace('_%', '')
        values = df[subject_col].tolist()
        offset = (i - len(subject_cols) / 2) * bar_width + bar_width / 2
        positions = [x + offset for x in x_positions]
        ax.bar(positions, values, bar_width, label=subject_name)
    
    ax.set_xlabel('Students', fontsize=12)
    ax.set_ylabel('Percentage (%)', fontsize=12)
    ax.set_title(f'Subject-wise Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    ax.set_xticks(x_positions)
    ax.set_xticklabels(students, rotation=45, ha='right')
    ax.legend()
    ax.set_ylim(0, 100)
    ax.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_line_chart(csv_path, class_name, exam_name):
    """Create a line chart showing student performance trends."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    students = df['Name'].tolist()
    percentages = df['Overall_Percentage'].tolist()
    
    plt.figure(figsize=(12, 6))
    plt.plot(students, percentages, marker='o', linewidth=2, markersize=8, color='green')
    plt.xlabel('Students', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Performance Trend - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_pie_chart(csv_path, class_name, exam_name):
    """Create a pie chart showing pass/fail distribution."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    pass_count = len(df[df['Overall_Percentage'] >= 35])
    fail_count = len(df[df['Overall_Percentage'] < 35])
    
    labels = ['Pass (>=35%)', 'Fail (<35%)']
    sizes = [pass_count, fail_count]
    colors = ['lightgreen', 'lightcoral']
    explode = (0.1, 0)
    
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%',
            shadow=True, startangle=90, textprops={'fontsize': 12})
    plt.title(f'Pass/Fail Distribution - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.axis('equal')
    plt.tight_layout()
    plt.show()


def plot_horizontal_bar(csv_path, class_name, exam_name):
    """Create a horizontal bar chart for easier reading of student names."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns:
        print("Overall_Percentage column not found.")
        return
    
    df_sorted = df.sort_values('Overall_Percentage', ascending=True)
    students = df_sorted['Name'].tolist()
    percentages = df_sorted['Overall_Percentage'].tolist()
    
    colors = ['red' if p < 35 else 'orange' if p < 60 else 'green' for p in percentages]
    
    plt.figure(figsize=(10, 8))
    plt.barh(students, percentages, color=colors, edgecolor='black')
    plt.xlabel('Percentage (%)', fontsize=12)
    plt.ylabel('Students', fontsize=12)
    plt.title(f'Student Rankings - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xlim(0, 100)
    plt.grid(axis='x', alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_subject_average(csv_path, class_name, exam_name):
    """Create a bar chart showing average percentage for each subject."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    subject_names = []
    averages = []
    
    for col in subject_cols:
        subject_name = col.replace('_%', '')
        avg = df[col].mean()
        subject_names.append(subject_name)
        averages.append(avg)
    
    colors = ['red' if a < 35 else 'orange' if a < 60 else 'green' for a in averages]
    
    plt.figure(figsize=(10, 6))
    plt.bar(subject_names, averages, color=colors, edgecolor='black')
    plt.xlabel('Subjects', fontsize=12)
    plt.ylabel('Average Percentage (%)', fontsize=12)
    plt.title(f'Subject-wise Class Average - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(axis='y', alpha=0.3)
    
    for i, v in enumerate(averages):
        plt.text(i, v + 2, f'{v:.1f}%', ha='center', fontweight='bold')
    
    plt.tight_layout()
    plt.show()


def plot_scatter(csv_path, class_name, exam_name):
    """Create a scatter plot showing roll number vs percentage."""
    df = pd.read_csv(csv_path)
    
    if 'Overall_Percentage' not in df.columns or 'Roll No' not in df.columns:
        print("Required columns not found.")
        return
    
    roll_nos = df['Roll No'].tolist()
    percentages = df['Overall_Percentage'].tolist()
    
    colors = ['red' if p < 35 else 'orange' if p < 60 else 'green' for p in percentages]
    
    plt.figure(figsize=(12, 6))
    plt.scatter(roll_nos, percentages, c=colors, s=100, alpha=0.6, edgecolors='black')
    plt.xlabel('Roll Number', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Roll No vs Performance - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.ylim(0, 100)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()


def plot_box_plot(csv_path, class_name, exam_name):
    """Create a box plot showing distribution of subject percentages."""
    df = pd.read_csv(csv_path)
    
    subject_cols = [col for col in df.columns if col.endswith('_%') and col != 'Overall_Percentage']
    
    if not subject_cols:
        print("No subject percentage columns found.")
        return
    
    data_to_plot = []
    labels = []
    
    for col in subject_cols:
        subject_name = col.replace('_%', '')
        values = df[col].dropna().tolist()
        data_to_plot.append(values)
        labels.append(subject_name)
    
    plt.figure(figsize=(12, 6))
    box = plt.boxplot(data_to_plot, labels=labels, patch_artist=True)
    
    for patch in box['boxes']:
        patch.set_facecolor('lightblue')
    
    plt.xlabel('Subjects', fontsize=12)
    plt.ylabel('Percentage (%)', fontsize=12)
    plt.title(f'Subject Performance Distribution - {class_name} - {exam_name}', fontsize=14, fontweight='bold')
    plt.xticks(rotation=45, ha='right')
    plt.ylim(0, 100)
    plt.grid(axis='y', alpha=0.3)
    plt.tight_layout()
    plt.show()
