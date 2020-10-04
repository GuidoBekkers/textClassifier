import sys
import numpy as np
import random
from joblib import load

if sys.argv[1] == 'majority':
    # Let the model predict on a brand new sentence
    not_aborted = True
    while not_aborted:
        sentence = input('Enter a sentence or type quit to exit the program:')

        if sentence.lower() != 'quit':
            print('inform')
        elif sentence.lower() == 'quit':
            not_aborted = False
        print('')

elif sys.argv[1] == 'rule':

    # dictionary with act as key and corresponding words as values
    rules = {'ack': ['okay', 'okay um', 'alright'], 'affirm': ['yes right', 'right', 'yes'],
             'bye': ['see you', 'good bye', 'bye'], 'confirm': ['is it'], 'deny': ['i dont want'],
             'hello': ['hi', 'hello'],
             'inform': ['looking for'], 'negate': ['no'], 'repeat': ['can you repeat that', 'what did you say'],
             'reqalts': ['how about'], 'reqmore': ['more'], 'request': ['what is', 'where'], 'restart': ['start over'],
             'thankyou': ['thank you', 'thanks']}

    not_aborted = True
    while not_aborted:
        acts = []
        sentence = input('Enter a sentence or type quit to exit the program:')
        if sentence.lower() != 'quit':
            for k, v in rules.items():
                if any(keywords in sentence.lower() for keywords in v):
                    acts.append(k)

            if not acts:
                print('null')
            else:
                print(random.choice(acts))

        elif sentence.lower() == 'quit':
            not_aborted = False
        print('')

else:

    # Loading the model
    if sys.argv[1] == 'mlp':
        clf = load('joblibs\MLP.joblib')

    elif sys.argv[1] == 'tree':
        clf = load('joblibs\decisionTree.joblib')

    elif sys.argv[1] == 'svm':
        clf = load('joblibs\SVM.joblib')

    # Loading the vectorizer
    BOW_vect = load('BOW_vect.joblib')

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