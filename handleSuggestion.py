def handle_suggestion(slots, matchlist=None):
    if matchlist == None:
        return
    while len(matchlist) > 0:
        print(matchlist[0][0] + " is a " + matchlist[0][1] + " restaurant that serves " + matchlist[0][3] + ".")
        response = clf.predict(BOW_vect.transform([input().lower()]))
        if response == 'affirm':
            print("The adress is " + matchlist[0][5] + ", " + matchlist[0][6] + " and the phone number is " + matchlist[0][4] + ".")
            return check_for_bye()  #In principe is hij nu klaar, aangezien de suggestie geaccepteerd is
        elif response == 'inform' or response == 'request':
            responseN = response
            while responseN == 'inform' or responseN == 'request':  #als de user om het adres of telefoonnummer vraagt
                askedInformation = keywordMatching(responseN)       # "adress" / "what is the adress?" --> "adress"
                if askedInformation == "adress":
                    print("The adress is " + matchlist[0][5] + ", " + matchlist[0][6] + ".")
                elif askedInformation == "phone number":
                    print("The phone number is " + matchlist[0][4] + ".")
                else:
                    print("I am sorry, I am not able to understand, here is all the available information")
                    print(matchlist[0][0] + " is a " + matchlist[0][1] + " restaurant " +
                          area_to_sentence_par(matchlist[0][2]) + " that serves " + matchlist[0][3] + ".")
                    print("The adress is " + matchlist[0][5] + ", " + matchlist[0][6] + " and the phone number is " +
                          matchlist[0][4] + ".")
                responseN = clf.predict(BOW_vect.transform([input().lower()]))
            return check_for_bye()
        else:
            matchlist = matchlist[1,:]
    print("Apologies, there is no alternative restaurant")
    return "restart information loop"


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