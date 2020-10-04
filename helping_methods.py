import pandas as pd
import random as rd
import Levenshtein as ls


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
