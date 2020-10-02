import Levenshtein as ls
from dialogActClassifier import dialog_act_classifier
from gtts import gTTS
from playsound import playsound
import implication as imp
import pandas as pd
import random as rd
import time



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
    """Creates a clause to describe the area
    Parameters
    ----------
    area : str
        the area that describes the part of town
    Returns
    -------
    It returns "centre of town" or area (south, north, east, west) + " part of town"
    """
    if area == "centre":
        return "centre of town"
    else:
        return area + " part of town"


def check_for_bye(utterance):
    """Checks if the user has said "bye" yet and closes down in case the user has
    Parameters
    ----------
    utterance : str
        the input of the user
    Returns
    -------
    None
    """
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
    """Function that loops until all the slots have been filled
    Parameters
    ----------
    restaurants : pandas DataFrame
        this df contains all the restaurants in the csv file
    Returns
    -------
    matched_restaurants : pandas DataFrame
        updated version of the df, containing the restaurants that match the given preferences
    """
    first_sentence = True # checks whether it is dealing with the first question of the conversation
    slots_found = []

    matched_restaurants = restaurants # if all that slots have been filled,
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:

        utterance = input().lower() # lets the user state a preference

        subtract_information_and_update_slots(utterance) # checks what knowledge the utterance contains

        if first_sentence is False:
            if 'any' in utterance or 'do not care' in utterance:
                for s in slots:
                    if slots[s] is None:
                        slots[s] = 'any'
                        slots_found.append(s)
                        break

        if CONFIRMATION: # if the user has stated to want confirmation, this part restates the understood preferences
            if dialog_act_classifier(utterance) == 'inform':
                slots_found = [slot for slot in slots if slots[slot] is not None][:-1]
                confirmation_question(slots_found)
                slots_found = []

        matched_restaurants = lookup(restaurants, slots['area'], slots['food'], slots['pricerange']) # uses the lookup function to search for matched restaurants

        if len(matched_restaurants) < 2: # if 0 or 1 matched restaurants are found, the loop breaks and returns either no restaurants or the one restaurant
            break

        check_slots() # since there are more options still available, the slots are checked to narrow down the search

        first_sentence = False # sets first_sentence to False after first iteration of the loop

    return matched_restaurants


def subtract_information_and_update_slots(utterance):

    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = keyword_matching(utterance, key)
        if slots[key] is None:
            slots[key] = pattern_matching(utterance, key)


def check_slots():
    """Function checks if a slot is filled or not. If not, prints a question to fill slot.
    Parameters
    ----------
    None
    Returns
    -------
    None if user doesn't want to restate preferences if a certain type of food is not possible
    """

    if not slots['area']:
        print_and_text_to_speech(area_question) # prints a question regarding the area if that bit of knowledge is unknown

    elif not slots['pricerange']:
        print_and_text_to_speech(pricerange_question) # prints a question regarding the pricerange if that bit of knowledge is unknown

    elif not slots['food']:

        if not food_questions: # This checks whether both the food questions have been asked, if so, the user has uttered an impossible foodtype wish
            # in that case, the user can restate a foodtype preference
            print_and_text_to_speech('Unfortunately, there are no options for that type of food. \nwould you like to restate your food preference?')

            answer = dialog_act_classifier(input())
            if answer == 'affirm':
                print_and_text_to_speech('What kind of food would you like instead?')

                answer_alternative = input().lower()

                slots['food'] = answer_alternative # if the user has restated a preference, the slots are updated

            return # if the user doesn't want to restate preferences, return None and break out of check_slots

        print_and_text_to_speech(food_questions[0]) # prints a question regarding the pricerange if that bit of knowledge is unknown


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
    """Function used to check which members in the set membership can be used to search for alternatives (example: thai and chinese can be swapped)
    Parameters
    ----------
    domain : str
        either 'area', 'food' or 'pricerange'
    preference : str
        contains the preference for a given domain (example: domain = 'area', preference = 'north')
    Returns
    -------
    None if no preference is present for a given domain
    updated_members : list
        list containing the possible alternatives based on the set membership only
    """

    if preference == None: # if no preference is found, the system needs to check first whether there is a preference for that domain
        #print_and_text_to_speech('Can not find alternatives for type None for: ' + domain)
        return

    domain = domain.lower()
    preference = preference.lower()

    updated_members = []

    for x in range(len(set_membership[domain])):

        if preference in set_membership[domain][x]: # checks if certain preferences are in the set_membership dictionary

            for y in range(len(set_membership[domain][x])):
                if set_membership[domain][x][y] not in updated_members: # checks whether a certain preference isn't already in the possible members list
                    updated_members.append(set_membership[domain][x][y])

    if preference in updated_members:
        updated_members.remove(preference) # removes the current preference, since this has been added as part of the members, but plays no role in the alternatives
    return updated_members


def search_alternatives(slots):
    """Searches for alternatives in the csv file using the possible members from member_alternative
    Parameters
    ----------
    slots : dict
        slots is the dictionary that holds the knowledge regarding the preferences per domain
    Returns
    -------
    None if no member_alternatives can be found, possibly because of an empty slot
    possible_restaurant_dict : dict
        a dictionary containing the possible restaurants as a list (value) per domain (key)
    """

    possible_restaurants_dict = {}
    possible_restaurants_dict['area'] = []
    possible_restaurants_dict['food'] = []
    possible_restaurants_dict['pricerange'] = []

    for domain in ['area', 'food', 'pricerange']:

        if member_alternative(domain, slots[domain]) == None:
            break

        alternatives_for_domain = member_alternative(domain, slots[domain]) # checks alternatives based on set membership


        #except TypeError:
         #   raise Exception('Can not find alternative for NoneType')
          #  return

        temp_slots = slots.copy() # to use the slots, but to not change them, a copy is made to check for alternatives
        temp_slots[domain] = [] # for storing more than one alternatives, a list is made per domain

        for alt in alternatives_for_domain:

            temp_slots[domain] = alt

            if len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) == 1:
                # if one alternative is found, this restaurant is added to the possible_restaurants_dict

                restaurant = lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[0]
                possible_restaurants_dict[domain].append([restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

            elif len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) > 1:
                # if more than one alternative is found, a loop goes over the possible restaurants and adds them to the possible_restaurants_dict

                for rest in range(len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']))):
                    restaurant = lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[
                        rest]
                    possible_restaurants_dict[domain].append([restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

    return possible_restaurants_dict


def handle_alternatives(slots):
    """Main function for organizing the process of choosing an alternative when no restaurant match is found
    Parameters
    ----------
    slots : dict
        slots is the dictionary that holds the knowledge regarding the preferences per domain
    Returns
    -------
    Doesn't return anything, but calls a_or_b if there are several options, or asks if the user wants to restate preferences when no alternatives are possible
    """
    number_of_alternatives = len(search_alternatives(slots)['area']) + len(search_alternatives(slots)['food']) + len(
        search_alternatives(slots)['pricerange']) # For checking how many alternatives are possible
    restaurant_names = {} # dict containing a restaurant name at a given index
    restaurant_counter = 0 # for indexing restaurant_names

    if number_of_alternatives > 0:
        print_and_text_to_speech('Unfortunately, there are no restaurants found. \nThe following alternatives are available:')

        for domain in ['area', 'food', 'pricerange']:

            if not len(search_alternatives(slots)[domain]) == 0:

                for option in range(len(search_alternatives(slots)[domain])):
                    #option_dict = {}
                    #option_dict['area'] = search_alternatives(slots)[domain][option][2]
                    #option_dict['food'] = search_alternatives(slots)[domain][option][3]
                    #option_dict['pricerange'] = search_alternatives(slots)[domain][option][1]
                    #restaurant_index.append(option_dict)

                    #search_alternatives(slots)[domain][option][0]
                    restaurant_names[restaurant_counter] = search_alternatives(slots)[domain][option][0] # adds restaurant to the dict

                    print_and_text_to_speech(str(restaurant_counter) + ' : ' + search_alternatives(slots)[domain][option][
                        0] + ' is a restaurant in the ' + search_alternatives(slots)[domain][option][
                              2] + ' part of town that serves ' + search_alternatives(slots)[domain][option][
                              3] + ' in the pricerange of ' + search_alternatives(slots)[domain][option][1]) # showing the alternatives to the user

                    restaurant_counter += 1 # for safely storing restaurant names at a unique index

        a_or_b(restaurant_names) # Letting the user either restate preferences (a) of choosing alternatives (b)

    else:  # if no alternatives are found, the user can change preferences
        print_and_text_to_speech('There are no alternatives, would you like to change your preferences?')

        response = dialog_act_classifier(input())
        if response == 'affirm':
            restate()

        else:
            print_and_text_to_speech('Then I am afraid that I can not help you')

            response = input().lower()
            check_for_bye(response)




def a_or_b(restaurant_names):
    """Function for handling restating preferences (a) or choosing alternatives (b) when no restaurant match is found
    Parameters
    ----------
    restaurant_names : dict
        dictionary that contains the restaurant names in order to suggest them whenever alternative is chosen
    Returns
    -------
    Doesn't return anything, but either calls restate() if a, or
    """
    print_and_text_to_speech('Would you like to: \n a: restate your preferences \n b: Choose one of these alternatives')
    answer_a_or_b = input()

    while answer_a_or_b not in ['a', 'b']: # Handling misspells
        print_and_text_to_speech('please type a or b')

        answer_a_or_b = input()

    if answer_a_or_b == 'a':
        restate()

    if answer_a_or_b == 'b':
        print_and_text_to_speech('Which alternative would you like?')

        answer = int(input())

        while answer not in range(len(restaurant_names)):
            print_and_text_to_speech(f'please type a number between 0 and {len(restaurant_names)-1}') # Handling misspells

            answer = int(input())

        handle_suggestion(restaurant_name=restaurant_names[answer]) # When an alternative is chosen, the name of the restaurant (on the given index in the dictionary) is passed to handle_suggestion


def restate():
    """Function can be used whenever the option is chosen to restate the preferences.
    Parameters
    ----------
    None
    Returns
    -------
    Doesn't return anything, but asks the user which domain and preference are desired to be changed
    """
    print_and_text_to_speech('which domain would you like to change?')


    answer_domain = input().lower()

    if answer_domain not in ['area', 'food', 'pricerange']:
        print_and_text_to_speech('Please select area, food or pricerange.') # This is done to catch the exception where the user misspells anything
        answer_domain = input().lower()


    print_and_text_to_speech('What alternative would you like?')


    answer_alternative = input().lower()

    slots[answer_domain] = answer_alternative # The slots get updated with the new, desired preference for a given domain


def print_and_text_to_speech(string):
    """Takes a string as input and prints it. If the user wants text-to-speech conversion, this function also converts and plays the speech
    Parameters
    ----------
    string : str
        the string that will be either printed and then converted to speech, or just printed
    Returns
    -------
    Doesn't return, only prints and if applicable plays the speech file
    """

    global tts

    print(string)

    if tts:

        language = 'en'

        sound_to_play = gTTS(text=string, lang=language, slow=False)

        unique_name = time.time()

        sound_to_play.save("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))

        playsound("tts_mp3/{0}_text_to_speech.mp3".format(unique_name))

def implication_loop(matchlist: pd.DataFrame):
    """Takes a pandas dataframe and updates it by reasoning about each restaurant, then it uses the updated dataframe
    to further rule out restaurants and find one that satisfies all the user's wishes
    Parameters
    ----------
    matchlist : pandas dataframe
        a dataframe with all the selected restaurants
    Returns
    -------
    None
    """
    imp.getConsequences(matchlist)
    implication_loop_recursive(matchlist)


def implication_loop_recursive(matchlist: pd.DataFrame):
    """Takes a updated pandas dataframe (with the new columns in the dataframe) and asks the user questions about
    the other features that can set the restaurants apart. (If all the restaurants serve good food it will not ask
    the user about good food, since it is pointless to ask)
    Parameters
    ----------
    matchlist : pandas DataFrame
        a dataframe with all the selected restaurants
    Returns
    -------
    The outcome of handle_suggestion
    """
    matchlist_copy = matchlist.copy(deep=False)
    distinguishers = findDistinguishers(matchlist)
    print_and_text_to_speech("There are multiple restaurants left.")

    while len(distinguishers) > 0 and matchlist.shape[0] > 1:
        print_and_text_to_speech(getNextQuestion(matchlist.columns[distinguishers[0]]))
        response = input().lower()
        d_act = dialog_act_classifier(response)
        if d_act == 'affirm':
            matchlist = matchlist[(matchlist.iloc[:,distinguishers[0]] == True)]
            distinguishers = findDistinguishers(matchlist)
        elif d_act == 'negate' or d_act == 'deny':
            matchlist = matchlist[(matchlist.iloc[:,distinguishers[0]] == False)]
            distinguishers = findDistinguishers(matchlist)
    hs = handle_suggestion(matchlist)

    if hs is None:
        print_and_text_to_speech("There is no restaurant that satisfies all your preferences.\nWould you like to:\n"
                                 + "a: Change your area, pricerange or foodtype\nb: Restate the other attributes")
        ab = a_b_loop()
        if ab == "a":
            return None     # Hij moet naar de information loop gaan
        elif ab == "b":
            implication_loop_recursive(matchlist_copy)
    else:
        return hs


def a_b_loop():
    """The input is checked and only returns if the user types "a" or "b", otherwise the user is told to choose either
    a or b
    Parameters
    ----------
    None
    Returns
    -------
    The answer of the user ("a" or "b")
    """
    answer = input().lower()
    if answer in ["a", "b"]:
        return answer
    else:
        print_and_text_to_speech("Please type either a or b")
        return a_b_loop()


def findDistinguishers(matchlist):
    """The columns, which the system has not asked about, which can distinguish the different restaurants present in
    the matchlist
    Parameters
    ----------
    matchlist : pandas dataframe
        a dataframe with restaurants filtered based on the 'slots'
    Returns
    -------
    It returns a list with the indexes of the columns that can be used to distinguish the restaurants in matchlist
    """
    distinguishers = []
    for i in range(7, matchlist.shape[1]):
        num = matchlist.iloc[:,i].value_counts().iloc[0]
        if num != len(matchlist) and num != 0:
            distinguishers.append(i)
    return distinguishers


def getNextQuestion(columnName: str):
    """Creates a new question (yes-no question) based on the name of a column
    Parameters
    ----------
    columnName : str
        the name of one of the columns (that the system has not yet asked questions about)
    Returns
    -------
    It returns a string with the question that the system should ask next
    """
    prob = rd.randint(0, 3)
    qclause = getQuestionClause(columnName)
    questionoptions = ["Would you like a ", "How about a ", "Shall I recommend a ", "Do you prefer a "]
    return questionoptions[prob] + qclause + "?"


def getQuestionClause(cn: str):
    """Creates a new question clause based on the name of a column
    Parameters
    ----------
    cn : str
        the name of one of the columns
    Returns
    -------
    It returns a string with the (subject) clause that describes the restaurant
    """
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

area_question = 'Which area would you like to dine in?'
pricerange_question = 'What pricerange were you thinking of?'
food_questions = ['Do you have any specific preferences regarding the type of food?',
                  'What type of food are you looking for?']


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

set_membership = {} # this dictionary is for checking which preferences can be swapped for a member alternative (like cheap - moderate)
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