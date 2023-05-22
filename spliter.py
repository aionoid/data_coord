import pandas as pd

# read the large csv file into a pandas dataframe
#  df = pd.read_csv('data.csv')
df = pd.read_csv('output/missing_dd.csv')

#  column_name = "place"
column_name = "Location"
# get the unique values of the column you want to split the data by
column_values = df[column_name].unique()

# loop over the unique values of the column
for value in column_values:
    # create a dataframe for each unique value
    value_df = df[df[column_name] == value]
    new_df = value_df.dropna(subset=['Latitude'])

    # write the dataframe to a new csv file
    #  value_df.to_csv(f'{column_name}_{value}.csv', index=False)
    new_df.to_csv(f'{column_name}_{value}_nonull.csv', index=False)
