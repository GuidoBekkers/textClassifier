import Levenshtein as ls
from dialogActClassifier import dialog_act_classifier
from gtts import gTTS
from playsound import playsound
import implication as imp
import pandas as pd
import random as rd


def keyword_matching(sentence, slot): # Todo Guido
    for w in sentence.split():
        if w in keywords[slot]:
            return w


def pattern_matching(sentence, slot): # Todo Guido
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
        print_and_text_to_speech("Apologies, no restaurant that serves " + slots["food"] + " was found.")
        return None
    else:
        return matchlist

def handle_suggestion(matchlist=None, restaurant_name=None):

    if restaurant_name is not None:
        matchlist = restaurants[restaurants.restaurantname == restaurant_name]

    while len(matchlist) > 0:

        print_and_text_to_speech(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant that serves " + matchlist.iloc[
            0, 3] + ".")
        print_and_text_to_speech('Would you like more information about this restaurant?')
        utterance = input().lower()

        response = dialog_act_classifier(utterance)  # response is een act

        if response == 'affirm' or response == 'confirm':
            print_and_text_to_speech("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + " and the phone number is " +
                  matchlist.iloc[0, 4] + ".")
            utterance = input().lower()
            check_for_bye(utterance)


        elif response == 'inform' or response == 'request':

            while response == 'inform' or response == 'request':  # als de user om het adres of telefoonnummer vraagt
                if 'adress' in utterance:
                    print_and_text_to_speech("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + ".")

                elif 'phone' in utterance or 'number' in utterance:
                    print_and_text_to_speech("The phone number is " + matchlist.iloc[0, 4] + ".")

                else:
                    print_and_text_to_speech("I am sorry, I am not able to understand, here is all the available information")

                    print_and_text_to_speech(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant " +
                          area_to_sentence_par(matchlist.iloc[0, 2]) + " that serves " + matchlist.iloc[0, 3] + ".")

                    print_and_text_to_speech("The adress is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[
                        0, 6] + " and the phone number is " +
                          matchlist.iloc[0, 4] + ".")


                utterance = input().lower()
                response = dialog_act_classifier(utterance)
                check_for_bye(utterance)

        elif response == 'deny':
            matchlist = matchlist.iloc[1:] # Todo build in a check that this is actually an negative and someone does not want this restaurant
        else:
            print_and_text_to_speech('Sorry I did not understand to you.')
    print_and_text_to_speech('Let me see how I can help you!')
    check_slots()
    return None


def area_to_sentence_par(area):
    if area == "centre":
        return "centre of town"
    else:
        return area + " part of town"


def check_for_bye(utterance):
    response = dialog_act_classifier(utterance)
    if response == 'bye' or response in 'thankyou':
        print_and_text_to_speech("Bye")
        quit()



def load_restaurants():
    restaurants = pd.read_csv('restaurant_info4.csv')
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
    first_sentence = True
    slots_found = []

    matched_restaurants = restaurants
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:

        utterance = input().lower()

        subtract_information_and_update_slots(utterance)

        if first_sentence is False:
            if 'any' in utterance or 'do not care' in utterance:
                for s in slots:
                    if slots[s] is None:
                        slots[s] = 'any'
                        slots_found.append(s)
                        break

        if CONFIRMATION:
            if dialog_act_classifier(utterance) == 'inform':
                slots_found = [slot for slot in slots if slots[slot] is not None][:-1]
                confirmation_question(slots_found)
                slots_found = []

        matched_restaurants = lookup(restaurants, slots['area'], slots['food'], slots['pricerange'])

        if len(matched_restaurants) > 1:
            check_slots()
        elif len(matched_restaurants) < 2:
            break

        first_sentence = False
    return matched_restaurants


def subtract_information_and_update_slots(utterance):

    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = keyword_matching(utterance, key)
        if slots[key] is None:
            slots[key] = pattern_matching(utterance, key)


def check_slots():
    if not slots['area']:
        print_and_text_to_speech(area_questions[0])


    elif not slots['pricerange']:
        print_and_text_to_speech(pricerange_questions[0])


    elif not slots['food']:

        if not food_questions:
            print_and_text_to_speech('Unfortunately, there are no options for that type of food. \nwould you like to restate your food preference?')

            answer = dialog_act_classifier(input())
            if answer == 'affirm':
                print_and_text_to_speech('What kind of food would you like instead?')


                answer_alternative = input().lower()

                slots['food'] = answer_alternative

            return

        print_and_text_to_speech(food_questions[0])


def confirmation_question(slots_found):
    for s in slots_found:
        if s == 'food':
            print('You are looking for {} food, correct?'.format(slots[s]))
        elif s == 'pricerange':
            print('You prefer the price to be {}, correct?'.format(slots[s]))
        elif s == 'area':
            print('So you want to eat in {} area of town?'.format(slots[s]))
        answer = input()
        if dialog_act_classifier(answer) != 'affirm':  # als de reactie geen bevestiging is, wordt het slot gereset
            slots[s] = None




def member_alternative(domain, preference):
    if preference == None:
        print_and_text_to_speech('Can not find alternatives for type None for: ' + domain)

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
    number_of_alternatives = len(search_alternatives(slots)['area']) + len(search_alternatives(slots)['food']) + len(
        search_alternatives(slots)['pricerange'])
    restaurant_index = []
    restaurant_names = {}
    restaurant_counter = 0

    if number_of_alternatives > 1:
        print_and_text_to_speech('Unfortunately, there are no restaurants found. \nThe following alternatives are available:')


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
                    print_and_text_to_speech(str(restaurant_counter) + ' : ' + search_alternatives(slots)[domain][option][
                        0] + ' is a restaurant in the ' + search_alternatives(slots)[domain][option][
                              2] + ' part of town that serves ' + search_alternatives(slots)[domain][option][
                              3] + ' in the pricerange of ' + search_alternatives(slots)[domain][option][1])


                    restaurant_counter += 1

        a_or_b(slots, restaurant_index, restaurant_names)

    else:
        print_and_text_to_speech('There are no alternatives, would you like to change your preferences?')

        response = dialog_act_classifier(input())
        if response == 'affirm':
            restate()


def a_or_b(slots, restaurant_index, restaurant_names):
    print_and_text_to_speech('Would you like to: \n a: restate your preferences \n b: Choose one of these alternatives')

    answer_a_or_b = input()

    while answer_a_or_b not in ['a', 'b']:
        print_and_text_to_speech('please type a or b')

        answer_a_or_b = input()

    if answer_a_or_b == 'a':
        restate()

    if answer_a_or_b == 'b':
        print_and_text_to_speech('Which alternative would you like?')

        answer = int(input())

        while answer not in range(len(restaurant_names)):
            print_and_text_to_speech(f'please type a number between 0 and {len(restaurant_names)-1}')


            answer = int(input())


        handle_suggestion(restaurant_name=restaurant_names[answer])


def restate():
    print_and_text_to_speech('which domain would you like to change?')


    answer_domain = input().lower()

    if answer_domain not in ['area', 'food', 'pricerange']:
        print_and_text_to_speech('Please select area, food or pricerange.')
        answer_domain = input().lower()


    print_and_text_to_speech('What alternative would you like?')


    answer_alternative = input().lower()

    slots[answer_domain] = answer_alternative

import time

def print_and_text_to_speech(string):

    global tts

    print(string)

    if tts:

        language = 'en'

        sound_to_play = gTTS(text=string, lang=language, slow=False)

        unique_name = time.time()

        sound_to_play.save("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))

        playsound("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))

def implication_loop(matchlist: pd.DataFrame):
    imp.getConsequences(matchlist)
    # print(matchlist)
    implication_loop_recursive(matchlist)

def implication_loop_recursive(matchlist: pd.DataFrame):
    matchlist_copy = matchlist.copy(deep=False)
    distinguishers = findDistinguishers(matchlist)
    print("There are multiple restaurants left.")

    while len(distinguishers) > 0 and matchlist.shape[0] > 1:
        print(getNextQuestion(matchlist.columns[distinguishers[0]]))
        response = input().lower()
        d_act = dialog_act_classifier(response)
        # De kolommen waarop hij de restaurants kan onderscheiden veranderen als er restaurants verwijderd worden
        if d_act == 'affirm':
            matchlist = matchlist[(matchlist.iloc[:,distinguishers[0]] == True)]
            distinguishers = findDistinguishers(matchlist)
        #
        # Valt "don't care" onder 'negate' of 'deny'? Als dat zo is dan:
        # moet er nog een elif voor 'negate' komen zodat de lijst niet ingekort wordt
        # Als het goed is wordt "doesnt matter" als 'inform' geclassificeerd.
        #
        elif d_act == 'negate' or d_act == 'deny':
            matchlist = matchlist[(matchlist.iloc[:,distinguishers[0]] == False)]
            distinguishers = findDistinguishers(matchlist)
    hs = handle_suggestion(matchlist)

    if hs is None:
        print("There is no restaurant that satisfies all your preferences.")
        print("Would you like to:")
        print("a: Change your area, pricerange or foodtype")
        print("b: Restate the other attributes")
        ab = a_b_loop()
        if ab == "a":
            return None     # Hij moet naar de information loop gaan
        elif ab == "b":
            implication_loop_recursive(matchlist_copy)
    else:
        return hs

def a_b_loop():
    answer = input().lower()
    if answer in ["a", "b"]:
        return answer
    else:
        print("Please type either a or b")
        return a_b_loop()

# find the columns that can be used to distinguish between the restaurants
def findDistinguishers(matchlist):
    distinguishers = []
    for i in range(7, matchlist.shape[1]):          #MOET range(7, matchlist.shape[1]) zijn!!!!!!!!!!
        num = matchlist.iloc[:,i].value_counts().iloc[0]
        if num != len(matchlist) and num != 0:
            distinguishers.append(i)
    return distinguishers

def getNextQuestion(columnName: str):
    prob = rd.randint(0, 3)
    qclause = getQuestionClause(columnName)
    questionoptions = ["Would you like a ", "How about a ", "Shall I recommend a ", "Do you prefer a "]
    return questionoptions[prob] + qclause + "?"

def getQuestionClause(cn: str):
    answers = ["restaurant with ", "restaurant with a ", "restaurant with ", " ", "restaurant that takes a ",
               " ", "restaurant with ", "restaurant that serves ", "restaurant that is fit for ", " ",
               "restaurant that is a "]
    options = ["pets allowed", "multi language menu", "good food", "busy", "long time", "dirty", "many tourists",
               "spicy", "children", "romantic", "tourist trap"]
    index = options.index(cn)
    if index in [0, 1, 2, 4, 6, 8, 10]:
        return answers[index] + cn
    elif index in [3, 5, 9]:
        return cn + " restaurant"
    elif index in [7]:
        return answers[index] + cn + " food"



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

possible_alternatives = {}


def main():
    global tts, CONFIRMATION

    print('Welcome to our restaurant recommendation system. \n Would you like to use Text-to-Speech? [yes/no]')

    tts_answer = dialog_act_classifier(input())
    if tts_answer == 'affirm':
        tts = True

    else:
        tts = False

    print_and_text_to_speech('Would you want confirmation for your preferences turned on? [yes/no]')
    confirmation_answer = dialog_act_classifier(input())

    if confirmation_answer == 'affirm':
        CONFIRMATION = True

    else:
        CONFIRMATION = False

    print_and_text_to_speech('What kind of restaurant are you looking for?')



    while True:

        matched_restaurants = information_loop(restaurants)

        if len(matched_restaurants) == 0:
            check_slots()
            handle_alternatives(slots)
            information_loop(restaurants)

        elif len(matched_restaurants) == 1:
            handle_suggestion(matched_restaurants)

        elif len(matched_restaurants) > 1:
            implication_loop(matched_restaurants)

main()