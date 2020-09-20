import pandas as pd
import Levenshtein as ls

df = pd.read_csv('restaurant_info.csv')
keywords = {'food': list(dict.fromkeys(list(df.food))),
            'area': ['west', 'north', 'south', 'centre', 'east'],
            'price': ['cheap', 'moderate', 'expensive'],
            'type': ['restaurant', 'bar', 'brasserie']
            }
patterns = {'food': ['food'],
            'area': ['part' 'area'],
            'price': ['priced', 'price'],
            'type': []
            }

slots = {'area': None, 'food': None, 'price': None, 'type': None}


# 'any' of 'do not care' kan hier niet bijgevoegd worden. Dat moet ergens anders in het programma verwerkt worden.

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


sentence = 'i want moderateley priced spenish food'

for key in filter(lambda x: slots[x] is None, slots):
    slots[key] = keyword_matching(sentence, key)
    if slots[key] is None:
        slots[key] = pattern_matching(sentence, key)

print(slots)
