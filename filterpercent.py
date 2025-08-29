import pandas as pd

# Load the main data
df = pd.read_excel('data/details.xlsx')

# Extract 'out of marks' from the first row
outofmarks_row = df.iloc[0]
df = df.iloc[1:]

# Create a dictionary for 'out of marks'
outofmarks_dict = outofmarks_row.to_dict()

print("Welcome")
# no = int(input("Enter the Percentage after which to filtered: "))

# Define the percentage categories
categories = [90, 75, 50, 33]

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
    
    for percentage in categories:
        # Calculate the marks threshold based on the percentage
        marks_threshold = (percentage / 100) * out_of_marks
        # Count students above the threshold
        count_above = (df[subject].astype(float) > marks_threshold).sum()
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

