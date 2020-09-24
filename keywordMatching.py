import pandas as pd
import itertools as perm
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
    for kw in keywords[slot]:
        if kw in sentence:
            return kw


def pattern_matching(sentence, slot):
    max_dist = 3
    i = max_dist + 1
    res = None
    for p in patterns[slot]:
        if p in sentence:
            sl = sentence.split(p, 1)[0].split()  # sl is a list that contains two strings that appear before the
            # pattern word
            while len(sl) > 2:
                sl.pop(0)
            for value in keywords[slot]:
                dist = min(ls.distance(sl[-1], value), ls.distance(sl[0] + " " + sl[1], value))
                if dist <= max_dist and dist < i:
                    i = dist
                    res = value
            return res


sentence = 'I want thei food moderatly priced in a restaurant in western area'

for key in filter(lambda x: slots[x] is None, slots):
    slots[key] = keyword_matching(sentence, key)
    if slots[key] is None:
        slots[key] = pattern_matching(sentence, key)

print(slots)

