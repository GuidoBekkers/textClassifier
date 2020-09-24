import pandas as pd
import Levenshtein as ls


def keyword_matching(sentence, slot):
    for kw in keywords[slot]:
        if kw in sentence:
            return kw


def pattern_matching(sentence, slot):
    max_dist = 3
    i = max_dist + 1
    res = None
    for p in patterns[slot]:
        if p in sentence:
            sl = sentence.split(p, 1)[0].split()
            while len(sl) > 2:
                sl.pop(0)   # now sl is a list that contains two strings that appear before the pattern word
            for value in keywords[slot]:
                dist = min(ls.distance(sl[-1], value), ls.distance(sl[0] + " " + sl[1], value))
                if dist <= max_dist and dist < i:
                    i = dist
                    res = value
            return res


def handle_suggestion(matchlist=None):
    if matchlist == None:
        return None
    while len(matchlist) > 0:
        print(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant that serves " + matchlist.iloc[
            0, 3] + ".")
        response = clf.predict(BOW_vect.transform([input().lower()]))
        if response == 'affirm':
            print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + " and the phone number is " +
                  matchlist.iloc[0, 4] + ".")
            return check_for_bye()  # In principe is hij nu klaar, aangezien de suggestie geaccepteerd is
        elif response == 'inform' or response == 'request':
            responseN = response
            while responseN == 'inform' or responseN == 'request':  # als de user om het adres of telefoonnummer vraagt
                askedInformation = keywordMatching(responseN)  # "adress" / "what is the adress?" --> "adress"
                if askedInformation == "adress":
                    print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + ".")
                elif askedInformation == "phone number":
                    print("The phone number is " + matchlist.iloc[0, 4] + ".")
                else:
                    print("I am sorry, I am not able to understand, here is all the available information")
                    print(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant " +
                          area_to_sentence_par(matchlist.iloc[0, 2]) + " that serves " + matchlist.iloc[0, 3] + ".")
                    print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[
                        0, 6] + " and the phone number is " +
                          matchlist.iloc[0, 4] + ".")
                responseN = clf.predict(BOW_vect.transform([input().lower()]))
            return check_for_bye()
        else:
            matchlist = matchlist[1, :]
    print("Apologies, there is no alternative restaurant")
    return None


def return_match_from_matchlist(slots):
    matchlist = lookup(slots["area"], slots["food"], slots["pricerange"])
    if len(matchlist) == 0:
        print("Apologies, no restaurant that serves " + slots["food"] + " was found.")
        return None
    else:
        return matchlist


def area_to_sentence_par(area):
    if area == "centre":
        return "centre of town"
    else:
        return area + " part of town"

def classify_utterance(string):
    return clf.predict(BOW_vect.transform([string.lower()]))

def check_for_bye():
    response = clf.predict(BOW_vect.transform([input().lower()]))
    if response == 'bye':
        return "finished"
    else:
        return "unknown"


def lookup(area=None, food=None, pricerange=None):
    """Looks up the restaurant(s) from the csv based on the preferences given by the user.
    :type area:str
    :type food:str
    :type pricerange: str
    :return restaurants: DataFrame
    """
    restaurants = pd.read_csv('restaurant_info.csv')
    if area is not None:
        area = area.lower()
        restaurants = restaurants[(restaurants.area == area)]
    if food is not None:
        food = food.lower()
        restaurants = restaurants[(restaurants.food == food)]
    if pricerange is not None:
        pricerange = pricerange.lower()
        restaurants = restaurants[(restaurants.pricerange == pricerange)]

    return restaurants


def information_loop():
    slot_question = None
    slots_found = []
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:
        utterance = input()

        dialog_act_classifier = 'inform'

        if slot_question is not None:
            if 'any' in utterance or 'do not care' in utterance:
                slots[slot_question] = 'any'
                slots_found.append(slot_question)
        if dialog_act_classifier == 'inform':
            slots_found = subtract_information_and_update_slots(utterance)

        for slot in slots_found:
            confirmation_question(slot, slots[slot])
            answer = input()
            if classify_utterance(answer) != 'affirm':
                slots[slot] = None

        print(slots)
        slot_question = check_slots()


def subtract_information_and_update_slots(utterance):
    filled_slots = []
    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = keyword_matching(utterance, key)
        if slots[key] is None and pattern_matching(utterance, key) is not None:
            slots[key] = pattern_matching(utterance, key)
            filled_slots.append(key)
        else:
            filled_slots.append(key)
    return filled_slots


def check_slots():
    if not slots['area']:
        # Code could be used in order to have multiple questions
        print(area_questions[0])
        area_questions.remove(area_questions[0])
        return 'area'

    elif not slots['pricerange']:
        print(pricerange_questions[0])
        pricerange_questions.remove(pricerange_questions[0])
        return 'pricerange'

    elif not slots['food']:
        print(food_questions[0])
        food_questions.remove(food_questions[0])
        return 'food'
    return None


slots = {}
questions = {}

slots['area'] = None
slots['pricerange'] = None
slots['food'] = None

print(slots)

area_questions = ['Which area would you like to dine in?',
                  'Could you give a specific area?']  # Questions could be in a list to have multiple questions
pricerange_questions = ['What pricerange were you thinking of?',
                        'Could you specify cheap, expensive or moderately priced?']
food_questions = ['Do you have any specific preferences regarding the type of food?',
                  'Could you state what food you want?']

def confirmation_question(slot, keyword):
    if slot == 'food':
        print('So you want to eat {} food?'.format(keyword))
    if slot == 'pricerange':
        print('So you want a {} price?'.format(keyword))
    if slot == 'area':
        print('So you want to eat in the {} area?'.format(keyword))


df = pd.read_csv('restaurant_info.csv')
keywords = {'food': list(dict.fromkeys(list(df.food))),
            'area': ['west', 'north', 'south', 'centre', 'east'],
            'pricerange': ['cheap', 'moderate', 'expensive'],
            'type': ['restaurant', 'bar', 'brasserie']
            }
patterns = {'food': ['food'],
            'area': ['part' 'area'],
            'pricerange': ['priced', 'price'],
            'type': []
            }


def main():
    print('Welcome, how can I help you?')

    information_loop()

    # print(return_match_from_matchlist(slots))

    antwoord = handle_suggestion(return_match_from_matchlist(slots))
    if antwoord == None:  # Als er geen restaurant is gevonden met de slots, moet hij opnieuw de slots vullen
        information_loop()
        handle_suggestion(return_match_from_matchlist(slots))


main()
