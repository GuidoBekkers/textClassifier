import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer


def load_and_preprocess(datafile, majority_class=False):# Reading of the datafile into a table with a single column 'data'
    df = pd.read_table(datafile, header=None, names=['data'])

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

    if majority_class == True:
        y_train, y_test = train_test_split(y, test_size=0.10)

        return y_train, y_test

    else:
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.10)
        print(f'\nSamples in train set: {len(x_train)}')
        print(f'Samples in test set: {len(x_test)}')

        # Vectorizing the text data of the sentences using the Bag of Words(BOW/count) method. The max_df/max_senteces
        # variable removes the words that occur in more than x% of the sentences, since these words are not distinctive since
        # they occur in almost all sentences. Better know as stopwords. The vectoriser also lowercases the words
        max_sentences = 0.80
        BOW_vect = CountVectorizer(max_df=max_sentences, lowercase=True, strip_accents='ascii')
        x_train_counts = BOW_vect.fit_transform(x_train)

        return x_train_counts, y_train, BOW_vect, x_test, y_test