import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.model_selection import cross_val_score
from sklearn.tree import DecisionTreeClassifier

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

# Storing the features (sentences) in x and the classes (acts) in y
x = df['sentence']
y = df['act']
x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.10)
print(f'\nSamples in train set: {len(x_train)}')
print(f'Samples in test set: {len(x_test)}')

# Vectorizing the text data of the sentences using the Bag of Words(BOW/count) method. The max_df/max_senteces
# variable removes the words that occur in more than x% of the sentences, since these words are not distinctive since
# they occur in almost all sentences. Better know as stopwords. The vectoriser also lowercases the words 
max_sentences = 0.80
BOW_vect = CountVectorizer(max_df=max_sentences, lowercase=True, strip_accents='ascii')
x_train_counts = BOW_vect.fit_transform(x_train)

# Scoring the model on the vectorised sentences and train target using cross validation
clf = DecisionTreeClassifier()
print('\nExecuting a 5-fold cross-validation over the train set...')
scores = cross_val_score(clf, x_train_counts, y_train, scoring='accuracy', cv=3)
print(f"Accuracy: {scores.mean():0.2} (+/- {scores.std() * 2:0.2})")

# Fitting the model on the training set
clf.fit(x_train_counts, y_train)

# Getting the accuracy of the fitted model on the test set:
x_test_counts = BOW_vect.transform(x_test)
y_pred = clf.predict(x_test_counts)
print(f'Accuracy over test set: {np.mean(y_pred == y_test):.2}')

# Let the model predict on a brand new sentence
print('Now you can give the model a go!')
not_aborted = True
while not_aborted:
    sentence = input('Enter a sentence or type quit to exit the program:')

    if sentence.lower() != 'quit':
        sentence_counts = BOW_vect.transform([sentence])
        prediction = clf.predict(sentence_counts)
        print(f'Dialog Act Prediction: {prediction[0]}')
    elif sentence.lower() == 'quit':
        not_aborted = False
    print('')
