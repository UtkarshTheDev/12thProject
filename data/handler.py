
def extractOutofMarks(df):
    # Extract 'out of marks' from the first row
    outofmarks_row = df.iloc[0]
    df = df.iloc[1:]

    # Create a dictionary for 'out of marks'
    outofmarks_dict = outofmarks_row.to_dict()
    return outofmarks_dict


def excludeRollNoAndName(df):
    # Exclude 'Roll No' and 'Name' columns
    df_numeric = df.select_dtypes(include='number')
    if 'Roll No' in df_numeric.columns:
        df_numeric = df_numeric.drop(columns=['Roll No'])
    return df_numeric

def extractDataFromExcel(file_path):
    df = pd.read_excel(file_path)
    return df