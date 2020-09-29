import pandas as pd
import Levenshtein as ls
from dialogActClassifier import dialog_act_classifier
from gtts import gTTS
from playsound import playsound
from implicationLoop import implication_loop

def keyword_matching(sentence, slot):
    for w in sentence.split():
        if w in keywords[slot]:
            return w


def pattern_matching(sentence, slot):
    max_dist = 2
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


def return_match_from_matchlist(slots):  # Remove this function entirely
    matchlist = lookup(slots["area"], slots["food"], slots["pricerange"])
    if len(matchlist) == 0:
        print("Apologies, no restaurant that serves " + slots["food"] + " was found.")
        return None
    else:
        return matchlist

def handle_suggestion(matchlist=None, restaurant_name=None):
    global tts

    if restaurant_name is not None:
        matchlist = restaurants[restaurants.restaurantname == restaurant_name]

    while len(matchlist) > 0:
        print(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant that serves " + matchlist.iloc[
            0, 3] + ".")
        utterance = input().lower()
        response = dialog_act_classifier(utterance)  # response is een act
        if tts:
            text_to_speech(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant that serves " + matchlist.iloc[
            0, 3] + ".")


        if response == 'affirm':
            print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + " and the phone number is " +
                  matchlist.iloc[0, 4] + ".")
            utterance = input().lower()
            check_for_bye(utterance)

            if tts:
                text_to_speech(
                    "The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + " and the phone number is " +
                    matchlist.iloc[0, 4] + ".")

        elif response == 'inform' or response == 'request':
            while response == 'inform' or response == 'request':  # als de user om het adres of telefoonnummer vraagt
                if 'adress' in utterance:
                    print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + ".")
                    if tts:
                        text_to_speech("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + ".")
                elif 'phone' in utterance or 'number' in utterance:
                    print("The phone number is " + matchlist.iloc[0, 4] + ".")
                    if tts:
                        text_to_speech("The phone number is " + matchlist.iloc[0, 4] + ".")
                else:
                    print("I am sorry, I am not able to understand, here is all the available information")
                    if tts:
                        text_to_speech("I am sorry, I am not able to understand, here is all the available information")

                    print(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant " +
                          area_to_sentence_par(matchlist.iloc[0, 2]) + " that serves " + matchlist.iloc[0, 3] + ".")


                    print("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[
                        0, 6] + " and the phone number is " +
                          matchlist.iloc[0, 4] + ".")

                    if tts:
                        text_to_speech("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[
                        0, 6] + " and the phone number is " +
                          matchlist.iloc[0, 4] + ".")

                utterance = input().lower()
                response = dialog_act_classifier(utterance)
                check_for_bye(utterance)

        else:
            matchlist = matchlist.iloc[1:]
    return None


def area_to_sentence_par(area):
    if area == "centre":
        return "centre of town"
    else:
        return area + " part of town"


def check_for_bye(utterance):
    response = dialog_act_classifier(utterance)
    if response == 'bye':
        return "finished"
        quit()


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
    matched_restaurants = restaurants
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:

        utterance = input().lower()

        if dialog_act_classifier(utterance) == 'inform':
            subtract_information_and_update_slots(utterance)

        if len(matched_restaurants) > 1:
            check_slots()
        elif len(matched_restaurants) < 2:
            break

        matched_restaurants = lookup(restaurants, slots['area'], slots['food'], slots['pricerange'])

    return matched_restaurants


def subtract_information_and_update_slots(utterance):

    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = keyword_matching(utterance, key)
        if slots[key] is None:
            slots[key] = pattern_matching(utterance, key)


def check_slots():
    if not slots['area']:
        # Code could be used in order to have multiple questions
        print(area_questions[0])
        area_questions.remove(area_questions[0])
        if tts:
            text_to_speech(area_questions[0])
        area_questions.remove(area_questions[0])

    elif not slots['pricerange']:
        print(pricerange_questions[0])
        pricerange_questions.remove(pricerange_questions[0])
        if tts:
            text_to_speech(pricerange_questions[0])
        pricerange_questions.remove(pricerange_questions[0])

    elif not slots['food']:

        if not food_questions:
            print('Unfortunately, there are no options for that type of food. \nwould you like to restate your food preference?')
            if tts:
                text_to_speech('Unfortunately, there are no options for that type of food. \nwould you like to restate your food preference?')
            answer = dialog_act_classifier(input())
            if answer == 'affirm':
                print('What kind of food would you like instead?')
                if tts:
                    text_to_speech('What kind of food would you like instead?')

                answer_alternative = input().lower()

                slots['food'] = answer_alternative

            return

        print(food_questions[0])
        if tts:
            text_to_speech(food_questions[0])
        food_questions.remove(food_questions[0])


slots = {}
questions = {}

slots['area'] = None
slots['pricerange'] = None
slots['food'] = None

area_questions = ['Which area would you like to dine in?',
                  'Could you give a specific area?']  # Questions could be in a list to have multiple questions
pricerange_questions = ['What pricerange were you thinking of?',
                        'Could you specify cheap, expensive or moderately priced?']
food_questions = ['Do you have any specific preferences regarding the type of food?',
                  'Could you state what food you want?']

restaurants = load_restaurants()


keywords = {'food': list(dict.fromkeys(list(restaurants.food))),
            'area': ['west', 'north', 'south', 'centre', 'east'],
            'pricerange': ['cheap', 'moderate', 'expensive'],
            'type': ['restaurant', 'bar', 'brasserie']
            }
patterns = {'food': ['food'],
            'area': ['part' 'area'],
            'pricerange': ['priced', 'price'],
            'type': []
            }

set_membership = {}
set_membership['pricerange'] = {0: ['cheap', 'moderate'],
                                1: ['moderate', 'expensive']}
set_membership['area'] = {0: ['centre', 'north', 'west'],
                          1: ['centre', 'north', 'east'],
                          2: ['centre', 'south', 'west'],
                          3: ['centre', 'south', 'east']}
set_membership['food'] = {0: ['thai', 'chinese', 'korean', 'vietnamese', 'asian oriental'],
                          1: ['mediterranean', 'spanish', 'portuguese', 'italian', 'romanian', 'tuscan', 'catalan'],
                          2: ['french', 'european', 'bistro', 'swiss', 'gastropub', 'traditional'],
                          3: ['north american', 'steakhouse', 'british'],
                          4: ['lebanese', 'turkish', 'persian'],
                          5: ['international', 'modern european', 'fusion']}




def member_alternative(domain, preference):
    global tts
    if preference == None:
        print('Can not find alternatives for type None for: ' + domain)
        if tts:
            text_to_speech('Can not find alternatives for type None for: ' + domain)
        return

    domain = domain.lower()
    preference = preference.lower()

    updated_members = []

    for x in range(len(set_membership[domain])):

        if preference in set_membership[domain][x]:

            for y in range(len(set_membership[domain][x])):
                if set_membership[domain][x][y] not in updated_members:
                    updated_members.append(set_membership[domain][x][y])

    updated_members.remove(preference)
    return updated_members


def search_alternatives(slots):
    possible_restaurants_dict = {}
    possible_restaurants_dict['area'] = []
    possible_restaurants_dict['food'] = []
    possible_restaurants_dict['pricerange'] = []

    for domain in ['area', 'food', 'pricerange']:
        try:
            alternatives_for_domain = member_alternative(domain, slots[domain])

        except TypeError:
            raise Exception('Can not find alternative for NoneType')
            return

        temp_slots = slots.copy()
        temp_slots[domain] = []

        for alt in alternatives_for_domain:

            temp_slots[domain] = alt

            if len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) == 1:

                restaurant = lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[0]
                possible_restaurants_dict[domain].append([restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

            elif len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) > 1:

                for restaurant in range(len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']))):
                    restaurant = lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[
                        restaurant]
                    possible_restaurants_dict[domain].append(
                        [restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

    return possible_restaurants_dict


def handle_alternatives(slots):
    global tts
    number_of_alternatives = len(search_alternatives(slots)['area']) + len(search_alternatives(slots)['food']) + len(
        search_alternatives(slots)['pricerange'])
    restaurant_index = []
    restaurant_names = {}
    restaurant_counter = 0

    if number_of_alternatives > 1:
        print('Unfortunately, there are no restaurants found. \nThe following alternatives are available:')

        if tts:
            text_to_speech('Unfortunately, there are no restaurants found. \nThe following alternatives are available:')

        for domain in ['area', 'food', 'pricerange']:
            if not len(search_alternatives(slots)[domain]) == 0:
                for option in range(len(search_alternatives(slots)[domain])):
                    option_dict = {}
                    option_dict['area'] = search_alternatives(slots)[domain][option][2]
                    option_dict['food'] = search_alternatives(slots)[domain][option][3]
                    option_dict['pricerange'] = search_alternatives(slots)[domain][option][1]
                    restaurant_index.append(option_dict)

                    search_alternatives(slots)[domain][option][0]
                    restaurant_names[restaurant_counter] = search_alternatives(slots)[domain][option][
                        0]
                    print(str(restaurant_counter) + ' : ' + search_alternatives(slots)[domain][option][
                        0] + ' is a restaurant in the ' + search_alternatives(slots)[domain][option][
                              2] + ' part of town that serves ' + search_alternatives(slots)[domain][option][
                              3] + ' in the pricerange of ' + search_alternatives(slots)[domain][option][1])

                    if tts:
                        text_to_speech(str(restaurant_counter) + ' : ' + search_alternatives(slots)[domain][option][
                        0] + ' is a restaurant in the ' + search_alternatives(slots)[domain][option][
                              2] + ' part of town that serves ' + search_alternatives(slots)[domain][option][
                              3] + ' in the pricerange of ' + search_alternatives(slots)[domain][option][1])

                    restaurant_counter += 1

        a_or_b(slots, restaurant_index, restaurant_names)

    else:
        print('There are no alternatives, would you like to change your preferences?')

        if tts:
            text_to_speech('There are no alternatives, would you like to change your preferences?')

        response = dialog_act_classifier(input())
        if response == 'affirm':
            restate()


def a_or_b(slots, restaurant_index, restaurant_names):
    global tts
    print('Would you like to: \n a: restate your preferences \n b: Choose one of these alternatives')

    if tts:
        text_to_speech('Would you like to:. \n a: restate your preferences. \n b: Choose one of these alternatives')

    answer_a_or_b = input()

    while answer_a_or_b not in ['a', 'b']:
        print('please type a or b')
        if tts:
            text_to_speech('please type a or b')

        answer_a_or_b = input()

    if answer_a_or_b == 'a':
        restate()

    if answer_a_or_b == 'b':
        print('Which alternative would you like?')

        if tts:
            text_to_speech('Which alternative would you like?')

        answer_1_or_2 = int(input())

        while answer_1_or_2 not in ['1', '2']:
            print('please type 1 or 2')
            if tts:
                text_to_speech('please type 1 or 2')

            answer_1_or_2 = int(input())


        handle_suggestion(restaurant_names[answer_1_or_2])


def restate():
    global tts
    print('which domain would you like to change?')

    if tts:
        text_to_speech('Which domain would you like to change?')

    answer_domain = input().lower()

    if answer_domain not in ['area', 'food', 'pricerange']:
        print('Please select area, food or pricerange.')
        if tts:
            text_to_speech('Please select area, food or pricerange')

    print('What alternative would you like?')

    if tts:
        text_to_speech('What alternative would you like?')

    answer_alternative = input().lower()

    slots[answer_domain] = answer_alternative

possible_alternatives = {}

def text_to_speech(string):

    mytext = string

    language = 'en'

    myobj = gTTS(text=mytext, lang=language, slow=False)

    myobj.save("welcome.mp3")

    playsound('welcome.mp3')


def main():

    global tts


    print('Welcome to our restaurant recommendation system. \n Would you like to use Text-to-Speech? [yes/no]')

    tts_answer = dialog_act_classifier(input())
    if tts_answer == 'affirm':
        tts = True

    else:
        tts = False


    print('What kind of restaurant are you looking for?')

    if tts:
        text_to_speech('What kind of restaurant are you looking for?')


    while True:

        matched_restaurants = information_loop(restaurants)

        if len(matched_restaurants) == 0:
            handle_alternatives(slots)
            information_loop(restaurants) # todo waarom doen we dit?

        elif len(matched_restaurants) == 1:
            handle_suggestion(matched_restaurants)

        elif len(matched_restaurants) > 1:
            implication_loop(matched_restaurants)

main()
