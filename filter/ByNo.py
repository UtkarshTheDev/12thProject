import pandas as pd

def filterbyno(df):
    # Default threshold values
    default_thresholds = [90, 75, 50, 33]
    
    # Get user input for threshold values
    user_input = input("Enter the mark thresholds (comma-separated, or press Enter for default): ")

    # Process user input
    if user_input.strip() == "":
        thresholds = default_thresholds
    else:
        try:
            thresholds = sorted([int(x.strip()) for x in user_input.split(',') if x.strip().isdigit()], reverse=True)
            if not thresholds:
                print("No valid numbers entered. Using default thresholds.")
                thresholds = default_thresholds
        except ValueError:
            print("Invalid input. Using default thresholds.")
            thresholds = default_thresholds

    print(f"\nUsing mark thresholds: {thresholds}")

    # Exclude non-subject columns
    df_numeric = df.select_dtypes(include='number')
    if 'Roll No' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Roll No'])
    if 'Name' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Name'])

    # List of all subjects
    subjects = df_numeric.columns
    
    # Initialize results list
    results = []

    # Calculate number of students scoring above each threshold for each subject
    for subject in subjects:
        subject_result = {'Subject': subject}
        marks = df[subject].astype(float)
        
        for threshold in thresholds:
            count_above = (marks > threshold).sum()
            subject_result[f'Above {threshold}'] = count_above
        
        # For Fail (below 33)
        fail_count = (marks < 33).sum()
        subject_result['Fail (<33)'] = fail_count
        
        results.append(subject_result)

    # Create a DataFrame from the results
    if results:
        filter_df = pd.DataFrame(results)
        return filter_df
    else:
        print("No data found for the specified criteria.")
        return pd.DataFrame()