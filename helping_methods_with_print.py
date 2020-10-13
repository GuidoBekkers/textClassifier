import print_and_text_to_speech as pattt
from dialog_act_classifier import dialog_act_classifier


def confirmation_question(slots_found, slots, tts):
    """Function provides confirmation questions when slots are filled.
    Parameters
    ----------
    slots_found : list
        consists the slots that are filled by the last utterance of the user
    slots : dict
        the dictionary with the preferences of the user
    tts : bool
        the boolean that determines whether or not text to speech is on
    Returns
    -------
    None
    """
    slots_confirmed = []
    for s in slots_found:
        if s == 'food':
            pattt.print_and_text_to_speech('You are looking for {} food, correct?'.format(slots[s]), tts)
        elif s == 'pricerange':
            pattt.print_and_text_to_speech('You prefer the price to be {}, correct?'.format(slots[s]), tts)
        elif s == 'area':
            pattt.print_and_text_to_speech('So you want to eat in {} area of town?'.format(slots[s]), tts)
        answer = input()
        slots_confirmed.append(s)
        if dialog_act_classifier(answer) != 'affirm':  # als de reactie geen bevestiging is, wordt het slot gereset
            slots[s] = None
            slots_confirmed.remove(s)
    return slots_confirmed


def a_b_loop(tts):
    """The input is checked and only returns if the user types "a" or "b", otherwise the user is told to choose either
    a or b
    Parameters
    ----------
    tts : bool
        the boolean that determines whether or not text to speech is on
    Returns
    -------
    The answer of the user ("a" or "b")
    """
    answer = input().lower()
    if answer in ["a", "b"]:
        return answer
    else:
        pattt.print_and_text_to_speech("Please type either a or b", tts)
        return a_b_loop(tts)


def check_for_bye(utterance, tts):
    """Checks if the user has said "bye" yet and closes down in case the user has
    Parameters
    ----------
    utterance : str
        the input of the user
    tts : bool
        the boolean that determines whether or not text to speech is on
    Returns
    -------
    None
    """
    response = dialog_act_classifier(utterance)
    if response == 'bye' or response in 'thankyou':
        pattt.print_and_text_to_speech("Bye", tts)
        quit()
