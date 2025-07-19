import pandas as pd
#Sample DataFrame import
# from data.classData import data


df = pd.read_excel('data/details.xlsx')
print("Welcome")
no = int(input("Enter the no. after which to filtered: "))

df = df.select_dtypes(include='number')

# Using Sample DataFrame

# df = pd.DataFrame(data)

# List of subjects
subjects = df.columns

# Calculate number of students scoring more than 90 in each subject
high_scores={}
for subject in subjects:

    high_scores[subject] = (df[subject] > no).sum()

# Create a new DataFrame from the result
filtername = "Above " + str(no)

high_scores_df = pd.DataFrame(list(high_scores.items()), columns=['Subject', filtername])

print(high_scores_df)

