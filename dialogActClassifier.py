from joblib import load


def initialize_classifier():
    """Loads the classifier object from a .joblib file.
    Parameters
    ----------
    None
    Returns
    -------
    classifier object."""

    return load('MLP.joblib')


def initialize_vectorizer():
    """Loads the vectorizer object from a .joblib file.
    Parameters
    ----------
    None
    Returns
    -------
    vectorizer object."""

    return load('BOW_vect.joblib')


clf = initialize_classifier()
BOW_vect = initialize_vectorizer()

def dialog_act_classifier(utterance):
    """Vectorises the input and then classifies using the classifier object.
    Parameters
    ----------
    utterance: str
        An utterance which needs to be classified
    Returns
    -------
    prediction: str"""

    vectorized_utterance = BOW_vect.transform([utterance.lower()])
    return clf.predict(vectorized_utterance)[0]
