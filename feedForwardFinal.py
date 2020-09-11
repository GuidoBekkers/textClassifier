import numpy as np
import csv
from sklearn.neural_network import MLPClassifier
import sklearn.feature_extraction.text


def leesBestandUit(naam_bestand):
    data_ = []
    for row in (csv.reader(open(naam_bestand))):
        data_.append(row)
    return data_


# Splits de regels op in 'Act', 'originele zin'
def splitsDataRows(lijst):
    return [i.lower().split(' ', 1) for sublijst in lijst for i in sublijst]


#  Geeft een [] terug met de twee delen (training - test)
def splitsNaar2Delen(lijst, grootte_training):
    return [lijst[:round(grootte_training * len(lijst))], lijst[round((1-grootte_training) * len(lijst)):]]


def splitsActInput(lijst):
    return [[i[0] for i in lijst], [i[1] for i in lijst]]


data = leesBestandUit('dialog_acts.dat')
nieuw = splitsDataRows(data)

gesplitst = splitsNaar2Delen(nieuw, 0.85)  # [Act_Lijst, zinnen_lijst]

trainingSetSplit = splitsActInput(gesplitst[0])
testSetSplit = splitsActInput(gesplitst[1])

count_vectorizer = sklearn.feature_extraction.text.CountVectorizer()
# krijg 'bag of words' van training set (zinnen lijst)
training_counts = count_vectorizer.fit_transform(trainingSetSplit[1])

model = MLPClassifier().fit(training_counts, trainingSetSplit[0])  # training BoW, training acts

# test set naar bag of words
test_counts = count_vectorizer.transform(testSetSplit[1])  # test zinnen

model_verwachtingen = model.predict(test_counts)  # test BoW

print(f'Accuracy: {np.mean(model_verwachtingen == testSetSplit[0]):.2}')
