import pandas as pd


# df = pd.read_excel('File-Name.xlsx')
print("Welcome")
no = int(input("Enter the no. after which to filtered: "))
# Sample data
data = {
    "Roll No": [1, 2, 3, 4, 5],
    "Name": ["Alice", "Bob", "Charlie", "Diana", "Ethan"],
    "Math": [88, 76, 95, 69, 85],
    "Science": [91, 82, 89, 74, 90],
    "English": [84, 79, 92, 81, 87],
    "History": [78, 85, 88, 73, 80],
    "Computer Science": [93, 89, 97, 88, 92]
}

df = pd.DataFrame(data)

# List of subjects
subjects = ["Math", "Science", "English", "History", "Computer Science"]

# Calculate number of students scoring more than 90 in each subject
high_scores={}
for subject in subjects:

    high_scores[subject] = (df[subject] > no).sum()

# Create a new DataFrame from the result
filtername = "Above " + str(no)

high_scores_df = pd.DataFrame(list(high_scores.items()), columns=['Subject', filtername])

print(high_scores_df)

