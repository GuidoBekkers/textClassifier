import pandas as pd
import random as rd
import Levenshtein as ls


def keyword_matching(sentence, slot):
    """Function checks if a keyword of a given slot is present in a given sentence. If so, the keyword is returned
    Parameters
    ----------
    sentence : str
        This is the string that needs to be analysed for keywords.
    slot: str
        The slot indicates for which keywords the sentence is analysed.
    Returns
    -------
    A keyword if it exists in the sentence, else None
    """
    for w in sentence.split():
        if w in keywords[slot]:
            return w


def pattern_matching(sentence, slot):
    """Function checks if a keyword of a given slot is present in a given sentence, using patterns. It also checks for
    language errors.
    Parameters
    ----------
    sentence : str
        This is the string that needs to be analysed for keywords.
    slot: str
        The slot indicates for which keywords the sentence is analysed.
    Returns
    -------
    A keyword if it exists in the sentence, else None
    """
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


def lookup(restaurants, area=None, food=None, pricerange=None):
    """Function that looks up restaurants in the database based on inputted preferences.
    Parameters
    ----------
    restaurants : pandas DataFrame
        this df contains all the restaurants in the csv file
    area: str
        this string contains the preference for the area property of the restaurant
    food: str
        this string contains the preference for the food property of the restaurant
    pricerange: str
        this string contains the preference for the pricerange property of the restaurant

    Returns
    -------
    matched_restaurants : pandas DataFrame
        updated version of the df, containing the restaurants that match the given preferences
    """
    if area == 'any':
        area = None
    if food == 'any':
        food = None
    if pricerange == 'any':
        pricerange = None

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


def load_restaurants():
    """Function that loads restaurants in a pandas DataFrame from the csv file.
        Parameters
        ----------
        Returns
        -------
        restaurants : pandas DataFrame
            DataFrame containing the restaurants and their properties from the csv file.
        """
    restaurants = pd.read_csv('restaurant_info4.csv')
    return restaurants


def restaurant_to_string(matchlist):
    """Turns a restaurant (row) into a string that the system can print
    Parameters
    ----------
    matchlist : pandas dataframe
        a pandas dataframe with 1 row, the restaurant
    Returns
    -------
    It returns a string with the necessary data
    """
    return str(matchlist.iloc[0]) + " is a " + str(matchlist.iloc[1]) + " restaurant that serves " + \
           str(matchlist.iloc[3]) + "."


def restaurant_info_to_string(matchlist):
    """Turns a restaurant (row) into a string that the system can print
    Parameters
    ----------
    matchlist : pandas dataframe
        a pandas dataframe with 1 row, the restaurant
    Returns
    -------
    It returns a string with the necessary data
    """
    return "The address is " + str(matchlist.iloc[5]) + ", " + str(matchlist.iloc[6]) + " and the phone number is " \
           + str(matchlist.iloc[4]) + "."


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

    if preference == None:  # if no preference is found, the system needs to check first whether there is a preference for that domain
        return

    domain = domain.lower()
    preference = preference.lower()

    updated_members = []

    for x in range(len(set_membership[domain])):

        if preference in set_membership[domain][x]:  # checks if certain preferences are in the set_membership dictionary

            for y in range(len(set_membership[domain][x])):
                if set_membership[domain][x][y] not in updated_members:  # checks whether a certain preference isn't already in the possible members list
                    updated_members.append(set_membership[domain][x][y])

    if preference in updated_members:
        updated_members.remove(preference)  # removes the current preference, since this has been added as part of the members, but plays no role in the alternatives
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

        alternatives_for_domain = member_alternative(domain,
                                                     slots[domain])  # checks alternatives based on set membership

        temp_slots = slots.copy()  # to use the slots, but to not change them, a copy is made to check for alternatives
        temp_slots[domain] = []  # for storing more than one alternatives, a list is made per domain

        for alt in alternatives_for_domain:

            temp_slots[domain] = alt

            if len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) == 1:
                # if one alternative is found, this restaurant is added to the possible_restaurants_dict

                restaurant = \
                lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[
                    0]
                possible_restaurants_dict[domain].append([restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

            elif len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange'])) > 1:
                # if more than one alternative is found, a loop goes over the possible restaurants and adds them to the possible_restaurants_dict

                for rest in range(
                        len(lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']))):
                    restaurant = \
                        lookup(restaurants, temp_slots['area'], temp_slots['food'], temp_slots['pricerange']).iloc[
                            rest]
                    possible_restaurants_dict[domain].append(
                        [restaurant[0], restaurant[1], restaurant[2], restaurant[3]])

    return possible_restaurants_dict


#
# Helping methods for the reasoning loop
#


def find_distinguishers(matchlist):
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
        num = matchlist.iloc[:, i].value_counts().iloc[0]
        if num != len(matchlist) and num != 0:
            distinguishers.append(i)
    rd.shuffle(distinguishers)
    return distinguishers


def get_next_question(column_name: str):
    """Creates a new question (yes-no question) based on the name of a column
    Parameters
    ----------
    column_name : str
        the name of one of the columns (that the system has not yet asked questions about)
    Returns
    -------
    It returns a string with the question that the system should ask next
    """
    prob = rd.randint(0, 3)
    qclause = get_question_clause(column_name)
    questionoptions = ["Would you like a ", "How about a ", "Shall I recommend a ", "Do you prefer a "]
    return questionoptions[prob] + qclause + "?"


def get_question_clause(cn: str):
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

# the dictionary below is for checking which preferences can be swapped for a member alternative (like cheap - moderate)
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

area_question = 'Which area would you like to dine in?'
pricerange_question = 'What pricerange were you thinking of?'
food_questions = ['Do you have any specific preferences regarding the type of food?',
                  'What type of food are you looking for?']