import pandas as pd

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