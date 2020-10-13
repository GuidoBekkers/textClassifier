import pandas as pd
import numpy as np
import random
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, classification_report, confusion_matrix
from sklearn.model_selection import GridSearchCV

df = pd.read_table("dialog_acts.dat", header=None, names=['data'])
df['act'] = df['data'].str.split(' ').str[0]
df['sentence'] = df['data'].str.split(' ').str[1:]
df['sentence'] = df['sentence'].str.join(' ')
df.drop(labels='data', inplace=True, axis=1)

df.act.value_counts()

contraptions = {'doesnt': "does not",
               'im': 'i am',
               'dont': 'do not',
               'id': 'i would'}

df['sentence'] = df['sentence'].replace(contraptions, regex=True)
df['sentence_length'] = df.sentence.str.split().apply(len)
df['sentence_length'].describe()

x = df['sentence']
y = df['act']

train_categories = 0
test_categories = 0

while train_categories < 15 and test_categories < 15:
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.15)
    train_categories = len(y_train.value_counts())
    test_categories = len(y_test.value_counts())

print(f'\nSamples in train set: {len(x_train)}')
print(f'Samples in test set: {len(x_test)}')

i = 0
def create_cf_matrix(y_test, y_pred, save_fig=False):
    global i
    cf_matrix = confusion_matrix(y_test, y_pred, labels=list(y_test.unique()))
    cm_sum = np.sum(cf_matrix, axis=1, keepdims=True)
    f = plt.figure(figsize=(11, 11))
    ax = plt.subplot()
    sns.heatmap(cf_matrix / cm_sum, annot=True, ax=ax, fmt='0.1%', cmap='Blues')  # annot=True to annotate cells

    ax.set_xlabel('Predicted labels')
    ax.set_ylabel('True labels')
    ax.set_title('Confusion Matrix')
    ax.xaxis.set_ticklabels(list(y_test.unique()), rotation=45)
    ax.yaxis.set_ticklabels(list(y_test.unique()), rotation=45)

    titles = ['majority', 'rule_based', 'decision_tree', 'SVM', 'MLP']
    if save_fig:
        plt.savefig(f'confusion_matrix_{titles[i]}')
    i += 1

print('Accuracy of the majority class classifier on the test samples:')
y_pred = len(y_test) * ['inform']
print(f"accuracy: {accuracy_score(y_test, y_pred)}")
print(f"precision: {precision_score(y_test, y_pred, average='weighted')}")
print(f"recall: {recall_score(y_test, y_pred, average='weighted')}")
create_cf_matrix(y_test, y_pred)

print('Accuracy of the rulebased classifier on the test samples')
# dictionary with act as key and corresponding words as values
rules = {'ack': ['okay', 'okay um', 'alright'], 'affirm': ['yes right', 'right', 'yes'],
         'bye': ['see you', 'good bye', 'bye'], 'confirm': ['is it'], 'deny': ['i dont want'],
         'hello': ['hi', 'hello'],
         'inform': ['looking for'], 'negate': ['no'], 'repeat': ['can you repeat that', 'what did you say'],
         'reqalts': ['how about'], 'reqmore': ['more'], 'request': ['what is', 'where'], 'restart': ['start over'],
         'thankyou': ['thank you', 'thanks']}

y_pred = []

for x in x_test:
    acts = []
    for k, v in rules.items():
        if any(keywords in x.lower() for keywords in v):
            acts.append(k)
    if not acts:
        y_pred.append('null')
    else:
        y_pred.append(random.choice(acts))

print(f"accuracy: {accuracy_score(y_test, y_pred)}")
print(f"precision: {precision_score(y_test, y_pred, average='weighted')}")
print(f"recall: {recall_score(y_test, y_pred, average='weighted')}")
create_cf_matrix(y_test, y_pred)

max_sentences = 0.85
min_sentences = 1
BOW_vect = CountVectorizer(max_df=max_sentences, min_df=1, lowercase=True, strip_accents='ascii')
x_train_counts = BOW_vect.fit_transform(x_train)


### Decision Tree
print('Finding best hyperparameters for Decision tree using grid search and cross validation.')
params = {'max_depth': list(range(1,25)),
          'min_samples_split': [10, 50,100]}
grid_search_cv = GridSearchCV(DecisionTreeClassifier(), params, verbose=1, cv=3, n_jobs=-1)
grid_search_cv.fit(x_train_counts, y_train)
x_test_counts = BOW_vect.transform(x_test)
y_pred = grid_search_cv.predict(x_test_counts)
print('Evaluation of the best hyperparameters on the test set')
print(f"accuracy: {accuracy_score(y_test, y_pred)}")
print(f"precision: {precision_score(y_test, y_pred, average='weighted')}")
print(f"recall: {recall_score(y_test, y_pred, average='weighted')}")
create_cf_matrix(y_test, y_pred)


### SVM
print('Finding best parameters for SVM using grid search and cross validation.')
params = params = {
    "loss" : ["hinge", "log", "squared_hinge", "modified_huber"],
    "alpha" : [0.0001, 0.001, 0.01, 0.1],
    "penalty" : ["l2", "l1", "none", "elasticnet"],
}

grid_search_cv = GridSearchCV(SGDClassifier(), params, verbose=1, cv=3, n_jobs=-1)
grid_search_cv.fit(x_train_counts, y_train)

x_test_counts = BOW_vect.transform(x_test)
y_pred = grid_search_cv.predict(x_test_counts)
print('Evaluation of the best hyperparameters on the test set')
print(f"accuracy: {accuracy_score(y_test, y_pred)}")
print(f"precision: {precision_score(y_test, y_pred, average='weighted')}")
print(f"recall: {recall_score(y_test, y_pred, average='weighted')}")
create_cf_matrix(y_test, y_pred)

results = pd.DataFrame({'utterance': x_test, 'act': y_test, 'predicted_act':y_pred})
results['utterance_length'] = results.utterance.str.split().apply(len)
corrects = results[(results.act == results.predicted_act)]
mistakes = results[(results.act != results.predicted_act)]
print(f'Distribution True:\n{mistakes.act.value_counts()}')
print(f'Distribution predicted:\n{mistakes.predicted_act.value_counts()}')
print(f'Utterance length description:\n {results.utterance_length.describe()}')
print(f'Utterance length description:\n {mistakes.utterance_length.describe()}')
print(f'Mistakes: {mistakes}')

### MLP
print('Finding best parameters for MLP using grid search and cross validation.')
params = {
    'hidden_layer_sizes': [(10,30,10),(20, 20), (20)],
    'activation': ['tanh', 'relu'],
    'solver': ['sgd', 'adam'],
    'alpha': [0.0001, 0.05],
    'learning_rate': ['constant','adaptive'],
}

grid_search_cv = GridSearchCV(MLPClassifier(max_iter=100), params, n_jobs=-1, cv=3)
grid_search_cv.fit(x_train_counts, y_train)

x_test_counts = BOW_vect.transform(x_test)
y_pred = grid_search_cv.predict(x_test_counts)

print('Evaluation of the best hyperparameters on the test set')
print(f"accuracy: {accuracy_score(y_test, y_pred)}")
print(f"precision: {precision_score(y_test, y_pred, average='weighted')}")
print(f"recall: {recall_score(y_test, y_pred, average='weighted')}")

create_cf_matrix(y_test, y_pred)

results = pd.DataFrame({'utterance': x_test, 'act': y_test, 'predicted_act':y_pred})
results['utterance_length'] = results.utterance.str.split().apply(len)
corrects = results[(results.act == results.predicted_act)]
mistakes = results[(results.act != results.predicted_act)]
print(f'Distribution True:\n{mistakes.act.value_counts()}')
print(f'Distribution predicted:\n{mistakes.predicted_act.value_counts()}')
print(f'Utterance length description:\n {results.utterance_length.describe()}')
print(f'Utterance length description:\n {mistakes.utterance_length.describe()}')
print(f'Mistakes: {mistakes}')