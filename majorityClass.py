import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

# Reading of the datafile into a table with a single column 'data'
df = pd.read_table("dialog_acts.dat", header=None, names=['data'])

# Splitting the single column into two columns. Column 'act' contains the act category and column 'sentence' contains
# the sentence. Dropping the 'data' column. Resulting in a dataframe with 2 columns.
df['act'] = df['data'].str.split(' ').str[0]
df['sentence'] = df['data'].str.split(' ').str[1:]
df['sentence'] = df['sentence'].str.join(' ')
df.drop(labels='data', inplace=True, axis=1)
print('First 10 rows of the dataframe:')
print(df.head(5))

# Storing the 15 different act categories in a variable.
acts = df['act'].unique()
print('\nDistribution of the acts in the dataset:')
print(df['act'].value_counts())

# Storing the classes (acts) in y. Making a training set and test set.
# Note that only the column of acts is needed if we always return the most common act.
y = df['act']
y_train, y_test = train_test_split(y, test_size=0.10)

# The accuracy on the test set
y_pred = y_train.value_counts().idxmax()
print(f'Accuracy over test set: {np.mean(y_pred == y_test):.2}')

# Let the model predict on a brand new sentence
not_aborted = True
while not_aborted:
    sentence = input('Enter a sentence or type quit to exit the program:')

    if sentence.lower() != 'quit':
        print(y_pred)
    elif sentence.lower() == 'quit':
        not_aborted = False
    print('')

