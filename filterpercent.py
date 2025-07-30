import pandas as pd

# Load the main data
df = pd.read_excel('data/details.xlsx')

# Extract 'out of marks' from the first row
outofmarks_row = df.iloc[0]
df = df.iloc[1:]

# Create a dictionary for 'out of marks'
outofmarks_dict = outofmarks_row.to_dict()

print("Welcome")
no = int(input("Enter the Percentage after which to filtered: "))

# Exclude 'Roll No' and 'Name' columns
df_numeric = df.select_dtypes(include='number')
if 'Roll No' in df_numeric.columns:
    df_numeric = df_numeric.drop(columns=['Roll No'])

# List of subjects
subjects = df_numeric.columns

# Calculate number of students scoring more than the given number in each subject
high_scores = {}
for subject in subjects:
    out_of_marks = outofmarks_dict.get(subject, 80)
    
    # Calculate the marks threshold based on the percentage
    marks_threshold = (no / 100) * float(out_of_marks)
    
    high_scores[subject] = (df[subject].astype(float) > marks_threshold).sum()

# Create a new DataFrame from the result
filtername = "Above " + str(no) + "%"
high_scores_df = pd.DataFrame(list(high_scores.items()), columns=['Subject', filtername])

print(high_scores_df)

