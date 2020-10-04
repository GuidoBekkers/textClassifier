from dialog_act_classifier import dialog_act_classifier
import implication as imp
import pandas as pd
import helping_methods as hm
import print_and_text_to_speech as pattt
import helping_methods_with_print as hmwp


def handle_suggestion(matchlist=None, restaurant_name=None):
    """Functions that handles suggesting restaurants to the user. If there are multiple restaurants it will select
    the first one. The user can either confirm, ask for information or negate the suggestion. When negated the
    restaurant will be removed from the matchlist. If the matchlist becomes empty the function is done. If the user
    accepts, or asked and received more information it checks for bye.
    If a restaurant name is given to the function, it will only suggest that one restaurant.
    Parameters
    ----------
    matchlist : pandas DataFrame
        matched restaurants which need to be suggested to the user.
    restaurant_name: str
        str which contains the name of the restaurant which needs to be suggested to the user.
    returns
    -------
    None
    """
    if restaurant_name is not None:
        matchlist = restaurants[restaurants.restaurantname == restaurant_name]

    while len(matchlist) > 0:

        pattt.print_and_text_to_speech(hm.restaurant_to_string(matchlist.iloc[0]), tts)
        pattt.print_and_text_to_speech('Would you like more information about this restaurant?', tts)
        utterance = input().lower()

        response = dialog_act_classifier(utterance)  # response is een act

        if response == 'affirm' or response == 'confirm':
            pattt.print_and_text_to_speech(hm.restaurant_info_to_string(matchlist.iloc[0]), tts)
            utterance = input().lower()
            hmwp.check_for_bye(utterance, tts)

        elif response == 'inform' or response == 'request':

            while response == 'inform' or response == 'request':  # als de user om het adres of telefoonnummer vraagt
                if 'address' in utterance:
                    pattt.print_and_text_to_speech(
                        "The address is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6] + ".", tts)

                elif 'phone' in utterance or 'number' in utterance:
                    pattt.print_and_text_to_speech("The phone number is " + matchlist.iloc[0, 4] + ".", tts)

                else:
                    pattt.print_and_text_to_speech(
                        "I am sorry, I am not able to understand, here is all the available information", tts)

                    pattt.print_and_text_to_speech(matchlist.iloc[0, 0] + " is a " + matchlist.iloc[0, 1] + " restaurant " +
                                             hm.area_to_sentence_par(matchlist.iloc[0, 2]) + " that serves " +
                                             matchlist.iloc[0, 3] + ".", tts)

                    pattt.print_and_text_to_speech("The address is " + matchlist.iloc[0, 5] + ", " + matchlist.iloc[0, 6]
                                                   + " and the phone number is " + matchlist.iloc[0, 4] + ".", tts)

                utterance = input().lower()
                response = dialog_act_classifier(utterance)
                hmwp.check_for_bye(utterance, tts)

        elif response == 'deny' or response == 'negate':
            matchlist = matchlist.iloc[1:]
        else:
            pattt.print_and_text_to_speech('Sorry I did not understand to you.', tts)

    pattt.print_and_text_to_speech('Let me see how I can help you!', tts)
    check_slots()
    return


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
    first_sentence = True  # checks whether it is dealing with the first question of the conversation
    slots_found = []
    slots_confirmed = []

    matched_restaurants = restaurants  # if all that slots have been filled,
    while slots['area'] == None or slots['pricerange'] == None or slots['food'] == None:

        utterance = input().lower()  # lets the user state a preference

        subtract_information_and_update_slots(utterance)  # checks what knowledge the utterance contains

        if first_sentence is False:
            if 'any' in utterance or 'do not care' in utterance:
                for s in slots:
                    if slots[s] is None:
                        slots[s] = 'any'
                        slots_found.append(s)
                        break

        slots_found = [slot for slot in slots if slots[slot] is not None]
        if CONFIRMATION:  # if the user has stated to want confirmation, this part restates the understood preferences
            if dialog_act_classifier(utterance) == 'inform':
                if slots_confirmed:
                    slots_found = [x for x in slots_found if x not in slots_confirmed]
                slots_confirmed.extend(hmwp.confirmation_question(slots_found, slots, tts))

        matched_restaurants = hm.lookup(restaurants, slots['area'], slots['food'],
                                     slots['pricerange'])  # uses the lookup function to search for matched restaurants

        if len(matched_restaurants) < 2:  # if 0 or 1 matched restaurants are found, the loop breaks and returns either no restaurants or the one restaurant
            break

        check_slots()  # since there are more options still available, the slots are checked to narrow down the search

        first_sentence = False  # sets first_sentence to False after first iteration of the loop

    return matched_restaurants


def subtract_information_and_update_slots(utterance):
    """Function extracts information from the user's utterance using keyword and pattern matching and updates slots
    accordingly
    Parameters
    ----------
    utterance : str
        the input from the user
    Returns
    -------
    None
    """
    for key in filter(lambda x: slots[x] is None, slots):
        slots[key] = hm.keyword_matching(utterance, key)
        if slots[key] is None:
            slots[key] = hm.pattern_matching(utterance, key)


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

        pattt.print_and_text_to_speech(hm.area_question, tts)  # prints a question regarding the area if that bit of knowledge is unknown

    elif not slots['pricerange']:
        pattt.print_and_text_to_speech(hm.pricerange_question, tts)  # prints a question regarding the pricerange if that bit of knowledge is unknown

    elif not slots['food']:
        # prints a question regarding the food if that bit of knowledge is unknown
        if not hm.food_questions:  # This checks whether both the food questions have been asked, if so, the user has uttered an impossible foodtype wish
            # in that case, the user can restate a foodtype preference
            pattt.print_and_text_to_speech(
                'Unfortunately, there are no options for that type of food.\nWhat kind of food would you like instead?', tts)

            # answer_alternative = input().lower()
            # slots['food'] = answer_alternative
            slots['food'] = input().lower()  # if the user has restated a preference, the slots are updated
            return  # if the user doesn't want to restate preferences, return None and break out of check_slots
        pattt.print_and_text_to_speech(hm.food_questions.pop())


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
    number_of_alternatives = len(hm.search_alternatives(slots)['area']) + len(hm.search_alternatives(slots)['food']) + len(
        hm.search_alternatives(slots)['pricerange'])  # For checking how many alternatives are possible
    restaurant_names = {}  # dict containing a restaurant name at a given index
    restaurant_counter = 0  # for indexing restaurant_names

    if number_of_alternatives > 0:
        pattt.print_and_text_to_speech(
            'Unfortunately, there are no restaurants found. \nThe following alternatives are available:', tts)

        for domain in ['area', 'food', 'pricerange']:

            if not len(hm.search_alternatives(slots)[domain]) == 0:

                for option in range(len(hm.search_alternatives(slots)[domain])):
                    hm.restaurant_names[restaurant_counter] = hm.search_alternatives(slots)[domain][option][
                        0]  # adds restaurant to the dict

                    pattt.print_and_text_to_speech(
                        str(restaurant_counter) + ' : ' + hm.search_alternatives(slots)[domain][option][
                            0] + ' is a restaurant in the ' + hm.search_alternatives(slots)[domain][option][
                            2] + ' part of town that serves ' + hm.search_alternatives(slots)[domain][option][
                            3] + ' in the pricerange of ' + hm.search_alternatives(slots)[domain][option][
                            1], tts)  # showing the alternatives to the user

                    restaurant_counter += 1  # for safely storing restaurant names at a unique index

        a_or_b(restaurant_names)  # Letting the user either restate preferences (a) of choosing alternatives (b)

    else:  # if no alternatives are found, the user can change preferences
        pattt.print_and_text_to_speech('There are no alternatives, would you like to change your preferences?', tts)

        response = dialog_act_classifier(input())
        if response == 'affirm':
            restate()

        else:
            pattt.print_and_text_to_speech('Then I am afraid that I can not help you', tts)

            response = input().lower()
            hmwp.check_for_bye(response, tts)


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
    pattt.print_and_text_to_speech('Would you like to: \n a: restate your preferences \n b: Choose one of these alternatives', tts)
    answer_a_or_b = input()

    while answer_a_or_b not in ['a', 'b']:  # Handling misspells
        pattt.print_and_text_to_speech('please type a or b', tts)

        answer_a_or_b = input()

    if answer_a_or_b == 'a':
        restate()

    if answer_a_or_b == 'b':
        pattt.print_and_text_to_speech('Which alternative would you like?', tts)

        answer = int(input())

        while answer not in range(len(restaurant_names)):
            pattt.print_and_text_to_speech(
                f'please type a number between 0 and {len(restaurant_names) - 1}', tts)  # Handling misspells

            answer = int(input())

        handle_suggestion(restaurant_name=restaurant_names[answer])  # When an alternative is chosen, the name of the restaurant (on the given index in the dictionary) is passed to handle_suggestion


def restate():
    """Function can be used whenever the option is chosen to restate the preferences.
    Parameters
    ----------
    None
    Returns
    -------
    Doesn't return anything, but asks the user which domain and preference are desired to be changed
    """
    pattt.print_and_text_to_speech('which domain would you like to change?', tts)

    answer_domain = input().lower()

    if answer_domain not in ['area', 'food', 'pricerange']:

        pattt.print_and_text_to_speech('Please select area, food or pricerange.', tts)  # This is done to catch the exception where the user misspells anything
        answer_domain = input().lower()

    pattt.print_and_text_to_speech('What alternative would you like?', tts)

    answer_alternative = input().lower()

    slots[answer_domain] = answer_alternative  # The slots get updated with the new, desired preference for a given domain


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
    imp.get_consequences(matchlist)
    return implication_loop_recursive(matchlist)


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
    distinguishers = hm.find_distinguishers(matchlist)
    pattt.print_and_text_to_speech("There are multiple restaurants left.", tts)

    while len(distinguishers) > 0 and matchlist.shape[0] > 1:
        pattt.print_and_text_to_speech(hm.get_next_question(matchlist.columns[distinguishers[0]]), tts)
        response = input().lower()
        d_act = dialog_act_classifier(response)
        if d_act == 'affirm':
            matchlist = matchlist[(matchlist.iloc[:, distinguishers[0]] == True)]
            distinguishers = hm.find_distinguishers(matchlist)
        elif d_act == 'negate' or d_act == 'deny':
            matchlist = matchlist[(matchlist.iloc[:, distinguishers[0]] == False)]
            distinguishers = hm.find_distinguishers(matchlist)
    hs = handle_suggestion(matchlist)
    if matchlist.shape[0] > 1:
        pattt.print_and_text_to_speech("The remaining restaurants could not be further distinguished from one another", tts)
    if hs is None:
        pattt.print_and_text_to_speech("There is no restaurant that satisfies all your preferences.\nWould you like to:\n"
                                 + "a: Change your area, pricerange or foodtype\nb: Restate the other attributes", tts)
        ab = hmwp.a_b_loop(tts)
        if ab == "a":
            return None
        elif ab == "b":
            return implication_loop_recursive(matchlist_copy)
    else:
        return hs


slots = {}
questions = {}

slots['area'] = None
slots['pricerange'] = None
slots['food'] = None

restaurants = hm.restaurants

possible_alternatives = {}


def main():
    """Main function that initiates and runs the dialog system. Handles configurability, the information loop,
    and the suggestion of restaurants or alternatives.
    Parameters
    ----------
    none
    Returns
    -------
    none
    """
    global tts, CONFIRMATION

    print('Welcome to our restaurant recommendation system. \n Would you like to use Text-to-Speech? [yes/no]')

    tts_answer = dialog_act_classifier(input())  # If yes, set text-to-speech(tts) to True
    if tts_answer == 'affirm':
        tts = True

    else:
        tts = False

    pattt.print_and_text_to_speech('Would you want confirmation for your preferences turned on? [yes/no]', tts)

    confirmation_answer = dialog_act_classifier(input())  # If yes, set text-to-speech(tts) to True
    if confirmation_answer == 'affirm':
        CONFIRMATION = True

    else:
        CONFIRMATION = False

    while True:

        pattt.print_and_text_to_speech('How can I help you?', tts)

        information_loop(restaurants)
        matched_restaurants = hm.lookup(restaurants, slots['area'], slots['food'], slots['pricerange'])

        if len(matched_restaurants) == 0:  # If no matching restaurants found, find alternatives or restate preferences
            check_slots()
            information_loop(restaurants)
            handle_alternatives(slots)

        elif len(matched_restaurants) == 1:  # If 1 matching restaurants found, suggest that restaurant
            handle_suggestion(matched_restaurants)

        elif len(matched_restaurants) > 1:  # If multiple matching restaurants found, find the best one for the user
            implication_loop(matched_restaurants)
            slots['area'] = None
            slots['pricerange'] = None
            slots['food'] = None


main()
