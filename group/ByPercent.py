import pandas as pd

def create_grouping_ranges(thresholds):
    # This function creates ranges for grouping percentages.
    # For example, if thresholds are [90,80,70], it makes ranges like [90-100], [80-89], etc.
    # Thresholds should be in descending order.
    if not thresholds or thresholds[0] != 100:
        thresholds = [100] + thresholds  # Add 100 at the start

    # Sort descending and remove 0 if present
    thresholds = sorted([int(t) for t in thresholds if t != 0], reverse=True)

    ranges = []
    for i in range(len(thresholds)):
        if i == len(thresholds) - 1:
            # Last range is from 0 to this threshold
            ranges.append([0, thresholds[i]])
        else:
            # Range from next threshold +1 to this one
            ranges.append([thresholds[i+1] + 1, thresholds[i]])
    return ranges

def groupByPercent(csv_path):
    # This function loads the percentage.csv file and groups students by their percentages in each subject.
    # It asks the user for custom grouping or uses default.
    # Returns the original dataframe with added group columns, and a summary dataframe with counts.
    df = load_percentage_csv(csv_path)

    # Default groups: 90-100, 80-89, etc.
    default_grouping = [[90, 100], [80, 89], [70, 79], [60, 69], [50, 59], [40, 49], [33, 39], [0, 32]]
    print("\nCurrent default grouping:")
    for group in default_grouping:
        print(f"{group[0]} - {group[1]}")
    user_input = input("\nEnter custom grouping thresholds (comma-separated, e.g., 90,80,70,33 or press Enter for default): ")
    if user_input.strip() == "":
        grouping = default_grouping
    else:
        try:
            thresholds = [int(t.strip()) for t in user_input.split(",")]
            # Check if all are between 0 and 100
            valid = True
            for x in thresholds:
                if not (0 <= x <= 100):
                    valid = False
                    break
            if not valid:
                print("Warning: All values should be between 0 and 100. Using default grouping.")
                grouping = default_grouping
            else:
                grouping = create_grouping_ranges(thresholds)
                print("\nCustom grouping created:")
                for group in grouping:
                    print(f"{group[0]}-{group[1]}")
        except:
            print("Invalid input format. Using default grouping.")
            grouping = default_grouping

    def get_group(score):
        # This helper function assigns a group to a score.
        # For example, 85 goes to "80-89"
        if pd.isna(score):
            return "N/A"
        for group in grouping:
            if group[0] <= score <= group[1]:
                return f"{group[0]}-{group[1]}"
        return "Other"

    subjects = get_subjects_from_percentage_df(df)
    if not subjects:
        print("Warning: No subject percentage columns found (expected columns ending with '_%').")
        return df, pd.DataFrame()

    results = []
    for subject in subjects:
        col = f"{subject}_%"  # Column name like "Math_%"
        print(f"\n--- {subject} (Using % column: {col}) ---")
        # Add a new column for the group
        df[f"{subject}_group"] = df[col].apply(get_group)
        # Count how many in each group
        group_counts = df[f"{subject}_group"].value_counts().sort_index(ascending=False)
        subject_result = {'Subject': subject}
        for group, count in group_counts.items():
            print(f"{group}: {count} students")
            subject_result[group] = count
        results.append(subject_result)

    summary_df = pd.DataFrame(results).fillna(0)
    # Sort the columns by the group start number descending
    other_cols = []
    for col in summary_df.columns:
        if col != 'Subject':
            other_cols.append(col)
    other_cols_sorted = sorted(other_cols, key=lambda x: int(x.split('-')[0]) if '-' in x and x.split('-')[0].isdigit() else 0, reverse=True)
    summary_df = summary_df[['Subject'] + other_cols_sorted]
    return df, summary_df


# Helpers for loading and getting subjects from the percentage CSV.

def load_percentage_csv(csv_path):
    # This function loads the CSV file into a pandas dataframe.
    return pd.read_csv(csv_path)

def get_subjects_from_percentage_df(df):
    # This function finds the subject names from the column names.
    # Columns like "Math_%" mean subject is "Math".
    subjects = []
    for col in df.columns:
        if col.endswith('_%') and col != 'Overall_Percentage':
            # Remove the "_%" to get subject name
            subjects.append(col[:-2])
    return subjects