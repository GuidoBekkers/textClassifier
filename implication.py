from enum import Enum
import pandas as pd

class Function(Enum):
    OR = 1
    AND = 0
    NOT = -1

class Implication(object):
    def __init__(self, id_: int, antecedent, consequent: str, cValue: bool, level: int, importance: int = 1):
        if not (isinstance(antecedent, Feature) or isinstance(antecedent, FeatureValue)):
            raise ValueError('Antecedent MUST be a Feature')
        self.id_ = id_
        self.antecedent = antecedent
        self.consequent = consequent                # string, "romantic", "busy"
        self.level = level                          # level 1 or level 2 rule
        self.importance = importance                # how import is this implication rule?
        self.cValue = cValue

    def getFeatureValue(self, restaurant):
        newValue = self.cValue if self.antecedent.getTruthValue(restaurant) else not self.cValue
        return FeatureValue(self.consequent, None, None, newValue)

    def getTruthValue(self, restaurant):
        return self.antecedent.getTruthValue(restaurant)

    def toString(self):
        if isinstance(self.antecedent, Implication):
            return self.antecedent.consequent
        else:
            return self.antecedent.toString() + " --> " + self.consequent + ", " + str(self.cValue)

    def print(self, restaurant):
        print(self.antecedent.toString() + " --> " + str(self.antecedent))
        print(str(self.antecedent) + " == " + str(self.antecedent.getTruthValue(restaurant)))

class Feature(object):
    def __init__(self, name, valueList: list, function: Function):
        self.valueList = valueList  # list of FeatureValues
        self.function = function    # Function (or, and, not
        self.name = name if isinstance(name, str) else self.toString()

    def getTruthValue(self, restaurant):
        if self.function.value == 1:
            return self.getTruthOr(restaurant)
        elif self.function.value == 0:
            return self.getTruthAnd(restaurant)
        elif self.function.value == -1:
            if self.valueList[0].getTruthValue(restaurant) is None:
                return None
            return not self.valueList[0].getTruthValue(restaurant)

    def getTruthOr(self, restaurant):
        antwood = False
        for i in self.valueList:
            if i.getTruthValue(restaurant) is None:
                return None
            if i.getTruthValue(restaurant):
                antwoord = True
        return antwood

    def getTruthAnd(self, restaurant):
        antwoord = True
        for i in self.valueList:
            if i.getTruthValue(restaurant) is None:
                return None
            if not i.getTruthValue(restaurant):
                antwoord = False
        return antwoord

    def print(self, restaurant):
        print(self.toString() + " == " + str(self.getTruthValue(restaurant)))

    def toString(self):
        if self.function.value == -1:
            return "(NOT " + self.valueList[0].name + ")"
        else:
            separator = " OR " if self.function.value == 1 else " AND "
            answer = "(" + self.valueList[0].toString()
            for i in self.valueList[1:]:
                answer += separator + i.toString()
            return answer + ")"

class FeatureValue(object):
    def __init__(self, name: str, columnIndex, expValue, truthValue: bool = None):
        self.name = name.lower()
        self.expValue = expValue.lower() if isinstance(expValue, str) else str(expValue).lower()
        self.columnIndex = columnIndex if isinstance(columnIndex, int) else -1
        self.truthValue = truthValue

    def getTruthValue(self, restaurant):
        if self.truthValue is not None:
            return self.truthValue
        elif self.columnIndex == -1 and self.truthValue is None:
            return None
        if str(restaurant.iloc[self.columnIndex]).lower() == str(self.expValue).lower():
            return True
        else:
            return False

    def toString(self):
        if self.columnIndex == -1:
            return str(self.name)
        else:
            if (self.columnIndex < 5):
                return self.name
            return "("+self.name + " == " + self.expValue+")"

class Implications(object):
    def __init__(self):
        self.fvPets = FeatureValue("pets allowed", 8, "true")
        self.fvMultiLang = FeatureValue("multi lang", 9, "true")
        self.fvGoodFood = FeatureValue("good food", 7, "true")
        self.fvCentre = FeatureValue("centre", 2, "centre")
        self.fvThai = FeatureValue("thai", 3, "thai")
        self.fvKorean = FeatureValue("korean", 3, "korean")
        self.fvVietnamese = FeatureValue("vietnamese", 3, "vietnamese")
        self.fvSpanish = FeatureValue("spanish", 3, "spanish")
        self.fvExpensive = FeatureValue("expensive", 1, "expensive")
        self.fvCheap = FeatureValue("cheap", 1, "cheap")
        # These ones can be changed, they have no index
        self.fvBusy = FeatureValue("busy", None, None, False)
        self.fvLongTime = FeatureValue("long time", None, None, False)
        self.fvDirty = FeatureValue("dirty", None, None, False)
        self.fvManyTourist = FeatureValue("many tourists", None, None, False)
        self.fvSpicy = FeatureValue("spicy", None, None, False)
        # Not used in any rule antecedent
        self.fvChildren = FeatureValue("children", None, None, True)
        self.fvRomantic = FeatureValue("romantic", None, None, False)
        self.fvTouristTrap = FeatureValue("tourist trap", None, None, False)

        self.featureValues = {"pets allowed": self.fvPets,
                         "multi lang": self.fvMultiLang,
                         "good food": self.fvGoodFood,
                         "centre": self.fvCentre,
                         "thai": self.fvThai,
                         "korean": self.fvKorean,
                         "vietnamese": self.fvVietnamese,
                         "spanish": self.fvSpanish,
                         "expensive": self.fvExpensive,
                         "cheap": self.fvCheap,
                         "busy": self.fvBusy,
                         "long time": self.fvLongTime,
                         "dirty": self.fvDirty,
                         "many tourists": self.fvManyTourist,
                         "spicy": self.fvSpicy,
                         "children": self.fvChildren,
                         "romantic": self.fvRomantic,
                         "tourist trap": self.fvTouristTrap }

        self.featureMultiCentre = Feature("multi & centre", [self.fvMultiLang, self.fvCentre], Function.AND)
        self.featureCheapGood = Feature("cheap & good food", [self.fvCheap, self.fvGoodFood], Function.AND)
        self.featureSpicy = Feature("spicy", [self.fvKorean, self.fvThai, self.fvVietnamese], Function.OR)
        self.featureNotSpicy = Feature("not spicy", [self.featureSpicy], Function.NOT)

        self.featureManyExpensive = Feature("many tourists & expensive", [self.fvManyTourist, self.fvExpensive], Function.AND)
        self.featureSpicyMulti = Feature("spicy & multi language", [self.fvSpicy, self.fvMultiLang], Function.AND)
        self.featureNotSpicyPets = Feature("not spicy & pets allowed", [self.featureNotSpicy, self.fvPets], Function.AND)
        # (self, id_: int, antecedent, consequent: str, level: int, importance: int = 1)
        # Predefined rules
        self.impliBusy1 = Implication(1, self.featureCheapGood, "busy", True, 1, 1)
        self.impliLongTime1 = Implication(2, self.fvSpanish, "long time", True, 1, 1)
        self.impliLongTime2 = Implication(3, self.fvBusy, "long time", True, 2, 1)
        self.impliChildren1 = Implication(4, self.fvLongTime, "children", False, 2, 1)
        self.impliRomantic1 = Implication(5, self.fvBusy, "romantic", False, 2, 3)
        self.impliRomantic2 = Implication(6, self.fvLongTime, "romantic", True, 2, 2)
        # New rules
        self.impliDirty1 = Implication(7, self.fvPets, "dirty", True, 1, 1)
        self.impliMany1 = Implication(8, self.featureMultiCentre, "many tourists", True, 1, 1)
        self.impliSpicy1 = Implication(9, self.featureSpicy, "spicy", True, 1, 1)
        self.impliRomantic3 = Implication(10, self.fvGoodFood, "romantic", True, 1, 2)

        self.impliRomantic4 = Implication(11, self.fvDirty, "romantic", False, 2, 6)
        self.impliTouristTrap1 = Implication(12, self.featureManyExpensive, "tourist trap", True, 2, 1)
        self.impliMany2 = Implication(13, self.featureSpicyMulti, "many tourists", True, 2, 1)
        self.impliChildren2 = Implication(14, self.featureNotSpicyPets, "children", True, 2, 2)

        self.implicationRules = [self.impliBusy1, self.impliLongTime1, self.impliLongTime2, self.impliChildren1,
                                 self.impliRomantic1, self.impliRomantic2, self.impliDirty1, self.impliMany1,
                                 self.impliSpicy1, self.impliRomantic3, self.impliRomantic4, self.impliTouristTrap1,
                                 self.impliMany2, self.impliChildren2]

    def getFeatureValue(self, name: str):
        if name in self.featureValues:
            return self.featureValues[name]
        return False

    def setFeatureValue(self, name: str, newValue: bool) -> int:
        if newValue is not None:
            if name in self.featureValues:
                antwoord = 0 if self.featureValues[name].truthValue == newValue else 1
                self.featureValues[name].truthValue = newValue
                return antwoord
        return -1

    def featuresToDictionary(self):
        answer = {}
        for i in self.featureValues:
            if self.featureValues[i].columnIndex == -1:  # Hij moet niet al bestaande kolommen teruggeven
                answer[i] = self.featureValues[i].truthValue
        return answer


def transposeList(input_: list):
    return list(map(list, zip(*input_)))


def solveConclusions(conclusions: list):
    answer = []
    for i in conclusions:
        if len(answer) > 0:
            index = listContainsConclusion(answer, i[0])
            if index > -1:
                answer[index] = mergeConclusions(answer[index], i)
            else:
                answer.append(i)
        else:
            answer.append(i)
    return answer


def listContainsConclusion(list_: list, name: str):
    for i in range(0, len(list_)):
        if list_[i][0] == name:
            return i
    return -1


def mergeConclusions(conclusion1, conclusion2):
    value1 = conclusion1[2] if conclusion1[1] is True else -1 * conclusion1[2]
    value2 = conclusion2[2] if conclusion2[1] is True else -1 * conclusion2[2]
    if set(conclusion2[3]) <= set(conclusion1[3]):
        return conclusion1
    return (conclusion1[0], True if value1 + value2 > 0 else False, abs(value1+value2), conclusion1[3]+conclusion2[3])


def getConsequencesSingle(restaurant):
    implications_ = Implications()
    rules = implications_.implicationRules
    changedValues = True
    loopNumber = 1
    conclusions = []
    iteratie = 0
    while changedValues and iteratie < 5:
        for i in range(0, len(rules)):
            if rules[i].level == loopNumber:
                tijdelijkFV = rules[i].getFeatureValue(restaurant)
                if tijdelijkFV.truthValue == rules[i].cValue:       # changed: consequence value is returned
                    conclusions.append((tijdelijkFV.name, tijdelijkFV.truthValue, rules[i].importance, [rules[i].id_]))
        conclusions = solveConclusions(conclusions)
        changedValues = False
        for i in conclusions:           # sterkte van regel wordt nog niet gebruikt
            newValue = implications_.setFeatureValue(i[0], i[1])
            if newValue == -1:
                return None
            elif newValue == 1:
                changedValues = True
        if loopNumber == 1:
            loopNumber = 2
            changedValues = True
        iteratie += 1
    return implications_.featuresToDictionary()


def printRules():
    temp_ = Implications()
    rules = temp_.implicationRules
    for i in range(0, len(rules)):
        print(rules[i].toString())


def getConsequences(restaurants: list):
    if restaurants is None:
        return None
    dictValues = []
    for i in range(0, restaurants.shape[0]):
        dictValues.append(list(getConsequencesSingle(restaurants.iloc[i]).values()))
    transposed = transposeList(dictValues)
    dictionary0 = list(getConsequencesSingle(restaurants.iloc[0]).keys())
    for i in range(0, len(transposed)):
        restaurants.insert(len(restaurants.columns), dictionary0[i], transposed[i], False)


#zoek = pd.read_csv('restaurant_info4.csv')
#eerste = zoek.iloc[14:15]
#getConsequences(eerste)

def getAddressOrPhone(utterance: str):
    answer = 0
    if "address" in utterance:
        answer += 1
    if "phone" in utterance:
        answer += 2
    return answer