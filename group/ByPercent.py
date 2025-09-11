import pandas as pd
from data.handler import extractOutofMarks

def create_grouping_ranges(thresholds):
    """Create grouping ranges from threshold values.
    
    Args:
        thresholds: List of threshold values in descending order (e.g., [90, 80, 70, 33])
        
    Returns:
        List of [min, max] ranges for each group
    """
    # Add 100 as the upper bound if not already present
    if not thresholds or thresholds[0] != 100:
        thresholds = [100] + thresholds
    
    # Sort in descending order to ensure proper grouping
    thresholds = sorted([int(t) for t in thresholds if t != 0], reverse=True)
    
    # Create ranges
    ranges = []
    for i in range(len(thresholds)):
        if i == len(thresholds) - 1:
            # Last range goes down to 0
            ranges.append([0, thresholds[i]])
        else:
            # Other ranges go down to the next threshold + 1
            ranges.append([thresholds[i+1] + 1, thresholds[i]])
    
    return ranges

def groupByPercent(df):
    default_grouping = [[90, 100], [80, 89], [70, 79], [60, 69], [50, 59], [40, 49], [33, 39], [0, 32]]
    
    # Get user input for grouping values
    print("\nCurrent default grouping:")
    for group in default_grouping:
        print(f"{group[0]} - {group[1]}")
        
    user_input = input("\nEnter custom grouping thresholds (comma-separated, e.g., 90,80,70,33 or press Enter for default): ")

    # Process User input
    if user_input.strip() == "":
        grouping = default_grouping
    else:
        try:
            # Parse and validate user input
            thresholds = [int(t.strip()) for t in user_input.split(",")]
            if not all(0 <= x <= 100 for x in thresholds):
                print("Warning: All values should be between 0 and 100. Using default grouping.")
                grouping = default_grouping
            else:
                grouping = create_grouping_ranges(thresholds)
                print("\nCustom grouping created:")
                for group in grouping:
                    print(f"{group[0]}-{group[1]}")
        except (ValueError, IndexError):
            print("Invalid input format. Using default grouping.")
            grouping = default_grouping
    
    # Apply the grouping to the dataframe
    def get_group(score):
        if pd.isna(score):
            return "N/A"
        for group in grouping:
            if group[0] <= score <= group[1]:
                return f"{group[0]}-{group[1]}"
        return "Other"
    
    # Get out of marks for each subject
    outofmarks_dict = extractOutofMarks(df)
    
    # Apply grouping to all numeric columns that represent marks/percentages
    df_numeric = df.select_dtypes(include=['number'])
    if 'Roll No' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Roll No'])
    
    if len(df_numeric.columns) == 0:
        print("Warning: No numeric columns found in the dataframe.")
        return df
    
    # Create a list to store results
    results = []
    
    # Process each subject
    for subject in df_numeric.columns:
        out_of_marks = float(outofmarks_dict.get(subject, 100))  # Default to 100 if not found
        print(f"\n--- {subject} (Out of: {out_of_marks}) ---")
        
        # Calculate percentage if marks are not already in percentage
        if out_of_marks != 100:
            df[f"{subject}_percentage"] = (df[subject] / out_of_marks) * 100
            score_series = df[f"{subject}_percentage"]
        else:
            score_series = df[subject]
        
        # Apply grouping
        df[f"{subject}_group"] = score_series.apply(get_group)
        
        # Count students in each group
        group_counts = df[f"{subject}_group"].value_counts().sort_index(ascending=False)
        
        # Store results
        subject_result = {'Subject': subject}
        for group, count in group_counts.items():
            print(f"{group}: {count} students")
            subject_result[group] = count
        
        results.append(subject_result)
    
    # Create a summary DataFrame
    summary_df = pd.DataFrame(results).fillna(0)
    
    # Reorder columns to have Subject first, then groups in descending order
    other_cols = [col for col in summary_df.columns if col != 'Subject']
    other_cols_sorted = sorted(other_cols, key=lambda x: int(x.split('-')[0]) if '-' in x and x.split('-')[0].isdigit() else 0, reverse=True)
    summary_df = summary_df[['Subject'] + other_cols_sorted]
    
    return df, summary_df