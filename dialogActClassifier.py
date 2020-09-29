from joblib import load


def initialize_classifier():
    return load('SVM.joblib')


def initialize_vectorizer():
    return load('BOW_vect.joblib')


clf = initialize_classifier()
BOW_vect = initialize_vectorizer()

def dialog_act_classifier(utterance):
    vectorized_utterance = BOW_vect.transform([utterance.lower()])
    return clf.predict(vectorized_utterance)
