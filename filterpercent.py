import pandas as pd

# Load the main data
df = pd.read_excel('data/details.xlsx')

# Extract 'out of marks' from the first row
outofmarks_row = df.iloc[0]
df = df.iloc[1:]

# Create a dictionary for 'out of marks'
outofmarks_dict = outofmarks_row.to_dict()

# Define the percentage categories
categories = [90, 75, 50, 33]

print("Welcome")

# Prompt the user for the percentage categories
print("Enter the percentage categories after which to filter.")
print("For default categories, press Enter.")
print("Default: 90,75,50,33")

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
high_scores_df = pd.DataFrame(results)

# Display the results
print("\nNumber of students scoring above each percentage threshold by subject:")
print(high_scores_df)

