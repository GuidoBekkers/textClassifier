import sys
import numpy as np
from sklearn.model_selection import cross_val_score
from sklearn.linear_model import SGDClassifier
from sklearn.neural_network import MLPClassifier
from sklearn.tree import DecisionTreeClassifier
from load_and_preprocess import load_and_preprocess

if sys.argv[1] == 'majority':
    y_train, y_test = load_and_preprocess("dialog_acts.dat", majority_class=True)

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

elif sys.argv[1] == 'rule':
    import random

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

    x_train_counts, y_train, BOW_vect, x_test, y_test = load_and_preprocess("dialog_acts.dat")

    if sys.argv[1] == 'mlp':
        clf = MLPClassifier()

    elif sys.argv[1] == 'tree':
        clf = DecisionTreeClassifier()

    elif sys.argv[1] == 'svm':
        clf = SGDClassifier()



    # Scoring the model on the vectorised sentences and train target using cross validation

    print('\nExecuting a 5-fold cross-validation over the train set...')

    try:
        for score in ["accuracy", "precision_macro", "recall_macro"]:
            scores = cross_val_score(clf, x_train_counts, y_train, scoring=score, cv=3)
            print(f"{score}: {scores.mean():0.2} (+/- {scores.std() * 2:0.2})")
    except NameError:
        print('Classifier not recognised')
        sys.exit(0)

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