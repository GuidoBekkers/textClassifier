from joblib import load
import re
import string

contraptions = {'doesnt': "does not",
               'im': 'i am',
               'dont': 'do not',
               'id': 'i would'}

def initialize_classifier():
    """Loads the classifier object from a .joblib file.
    Parameters
    ----------
    None
    Returns
    -------
    classifier object."""

    return load('joblibs/MLP.joblib')


def initialize_vectorizer():
    """Loads the vectorizer object from a .joblib file.
    Parameters
    ----------
    None
    Returns
    -------
    vectorizer object."""

    return load('joblibs/BOW_vect.joblib')


clf = initialize_classifier()
BOW_vect = initialize_vectorizer()

def dialog_act_classifier(utterance):
    """Cleans the input and then vectorizes it and then classifies using the classifier object.
    Parameters
    ----------
    utterance: str
        An utterance which needs to be classified
    Returns
    -------
    prediction: str"""
    utterance = utterance.lower()
    utterance = utterance.translate(str.maketrans('', '', string.punctuation))
    for key in contraptions.keys():
        utterance = utterance.replace(key, contraptions[key])
    vectorized_utterance = BOW_vect.transform([utterance])
    return clf.predict(vectorized_utterance)[0]
