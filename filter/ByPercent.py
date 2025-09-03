import pandas as pd

def filterByPercent(df):
    categories = [90, 75, 50, 33]

    # Get user input
    user_input = input("Enter the percentage categories (comma-separated, or press Enter for default): ")

    # Process user input
    if user_input.strip() == "":
        categories = [90, 75, 50, 33]
    else:
        try:
            categories = sorted([int(x.strip()) for x in user_input.split(',') if x.strip().isdigit()], reverse=True)
            if not categories:
                print("No valid percentages entered. Using default categories.")
                categories = [90, 75, 50, 33]
        except ValueError:
            print("Invalid input. Using default categories.")
            categories = [90, 75, 50, 33]

    print(f"\nUsing categories: {categories}")

    # Exclude 'Roll No' and 'Name' columns
    df_numeric = df.select_dtypes(include='number')
    if 'Roll No' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Roll No'])

    # List of subjects
    subjects = df_numeric.columns

    # Initialize a dictionary to store results
    results = []

    # Calculate number of students scoring above each percentage threshold for each subject
    for subject in subjects:
        out_of_marks = float(outofmarks_dict.get(subject, 80))
        subject_result = {'Subject': subject}
        print(f"\n--- {subject} (Out of: {out_of_marks}) ---")
    
        for percentage in categories:
            marks_threshold = (percentage / 100) * out_of_marks
            marks = df[subject].astype(float)
            count_above = (marks > marks_threshold).sum()
            subject_result[f'Above {percentage}%'] = count_above

    # For Fail
    fail_count = (df[subject].astype(float) < 33).sum()
    subject_result['Fail'] = fail_count
    results.append(subject_result)

    # Create a DataFrame from the results
    filter_df = pd.DataFrame(results)

    return filter_df
