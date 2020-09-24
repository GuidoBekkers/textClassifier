import pandas as pd
import Levenshtein as ls


def keyword_matching(sentence, slot):
    for w in sentence.split():
        if w in keywords[slot]:
            return w


def pattern_matching(sentence, slot):
    max_dist = 3
    i = max_dist + 1
    res = None
    wordlist = sentence.split()
    for w in wordlist:
        if w in patterns[slot]:
            index = wordlist.index(w) - 1
            match = wordlist[index]
            for value in keywords[slot]:
                dist = ls.distance(match, value)
                if dist <= max_dist and dist < i:
                    i = dist
                    res = value
            return res


# sentence = 'i want moderateley priced spenish food'

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


def check_for_bye():
    response = clf.predict(BOW_vect.transform([input().lower()]))
    if response == 'bye':
        return "finished"
    else:
        return "unknown"


def load_restaurants():
    restaurants = pd.read_csv('restaurant_info.csv')
    return restaurants

def lookup(restaurants, area=None, food=None, pricerange=None):
    """Looks up the restaurant(s) from the csv based on the preferences given by the user.
    :type area:str
    :type food:str
    :type pricerange: str
    :return restaurants: DataFrame
    """
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

def information_loop(restaurants):
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:

        utterance = input()

        dialog_act_classifier = 'inform'

        # if dialog_act_classifier(utterance) == 'inform':
        if dialog_act_classifier == 'inform':
            subtract_information_and_update_slots(utterance)

        check_slots()


def subtract_information_and_update_slots(utterance):
    # use keywords to obtain domain and new information

    # utterance = utterance.split()

    # domain = utterance[0]

    # new_information_about_domain = utterance[1:]

    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = keyword_matching(utterance, key)
        if slots[key] is None:
            slots[key] = pattern_matching(utterance, key)

    # if domain in slots.keys():

    # slots[domain] = new_information_about_domain


def check_slots():
    if not slots['area']:
        # Code could be used in order to have multiple questions
        print(area_questions[0])
        area_questions.remove(area_questions[0])

    elif not slots['pricerange']:
        print(pricerange_questions[0])
        pricerange_questions.remove(pricerange_questions[0])

    elif not slots['food']:
        print(food_questions[0])
        food_questions.remove(food_questions[0])


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

df = pd.read_csv('/content/drive/My Drive/restaurant_info.csv')
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

restaurants = load_restaurants()

def main():
    print('Welcome, how can I help you?')
    information_loop(restaurants)

    # print(return_match_from_matchlist(slots))

    antwoord = handle_suggestion(slots, return_match_from_matchlist(slots))
    if antwoord == None:  # Als er geen restaurant is gevonden met de slots, moet hij opnieuw de slots vullen
        information_loop()
        handle_suggestion(slots, return_match_from_matchlist(slots))


main()
