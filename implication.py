from enum import Enum
import pandas as pd

class Function(Enum):
    OR = 1
    AND = 0
    NOT = -1
    LONE = 2

class Implication(object):
    def __init__(self, id_: int, antecedent, consequent: str, cValue: bool, level: int, importance: int = 1):
        if not (isinstance(antecedent, Feature) or isinstance(antecedent, FeatureValue)):
            raise ValueError('Antecedent MUST be a Feature')
        # if not isinstance(consequent, FeatureValue):
        #    raise ValueError('consequent MUST be a FeatureValue')
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
        #if len(valueList) == 0:
        #    raise ValueError('valueList cannot be empty')
        #if function.value == -1 and len(valueList) > 1:
        #    raise ValueError('If function is NOT, then valueList cannot be longer than 1')
        self.valueList = valueList  # list of FeatureValues
        self.function = function    # Function (or, and, not
        self.name = name if isinstance(name, str) else self.toString()

    def getTruthValue(self, restaurant):
        # print("Name = " + str(self.name))
        if self.function.value == 2:
            if self.valueList[0].getTruthValue(restaurant) is None:
                return None
            return self.valueList[0].getTruthValue(restaurant)
        elif self.function.value == 1:
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
                #print("return NONE !!!!!!!!!!!!!!")
                return None
            if not i.getTruthValue(restaurant):
                #print(i.toString() + " is false? " + str(i.name))
                antwoord = False
        #print("antwoord is .... " + str(antwoord))
        return antwoord

    def print(self, restaurant):
        print(self.toString() + " == " + str(self.getTruthValue(restaurant)))

    def toString(self):
        if self.function.value == -1:
            return "(NOT " + self.valueList[0].name + ")"
        elif self.function.value == 2:
            return self.valueList[0].toString()
        else:
            separator = " OR " if self.function.value == 1 else " AND "
            answer = "(" + self.valueList[0].toString()
            for i in self.valueList[1:]:
                answer += separator + i.toString()
            return answer + ")"

class FeatureValue(object):
    def __init__(self, name: str, columnIndex, expValue, truthValue: bool = None):
        # if truthValue is not None and not isinstance(truthValue, bool):
        #    raise ValueError('truthValue must be a boolean or None')
        self.name = name.lower()
        self.expValue = expValue.lower() if isinstance(expValue, str) else str(expValue).lower()
        self.columnIndex = columnIndex if isinstance(columnIndex, int) else -1
        self.truthValue = truthValue

    def getTruthValue(self, restaurant):
        if self.truthValue is not None:
            return self.truthValue
        elif self.columnIndex == -1 and self.truthValue is None:
            return None
        #print(str(restaurant.iloc[self.columnIndex]).lower() + " =? " + str(self.expValue))
        if str(restaurant.iloc[self.columnIndex]).lower() == str(self.expValue).lower():
            #print(self.name + ": return true")
            return True
        else:
            #print(self.name + ": return false")
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
        # Not used in any rule
        self.fvChildren = FeatureValue("children", None, None, True)
        self.fvRomantic = FeatureValue("romantic", None, None, False)
        self.fvTouristTrap = FeatureValue("tourist trap", None, None, False)

        # Romantisch --> als er goed voedsel is

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
        self.impliRomantic1 = Implication(5, self.fvBusy, "romantic", False, 2, 1)
        self.impliRomantic2 = Implication(6, self.fvLongTime, "romantic", True, 2, 2)
        # New rules
        self.impliDirty1 = Implication(7, self.fvPets, "dirty", True, 1, 1)
        self.impliMany1 = Implication(8, self.featureMultiCentre, "many tourists", True, 1, 1)
        self.impliSpicy1 = Implication(9, self.featureSpicy, "spicy", True, 1, 1)
        self.impliRomantic3 = Implication(10, self.fvDirty, "romantic", False, 2, 3)
        self.impliTouristTrap1 = Implication(11, self.featureManyExpensive, "tourist trap", True, 2, 1)
        self.impliMany2 = Implication(12, self.featureSpicyMulti, "many tourists", True, 2, 1)
        self.impliChildren2 = Implication(13, self.featureNotSpicyPets, "children", True, 2, 2)

        self.implicationRules = [self.impliBusy1, self.impliLongTime1, self.impliLongTime2, self.impliChildren1,
                                 self.impliRomantic1, self.impliRomantic2, self.impliDirty1, self.impliMany1,
                                 self.impliSpicy1, self.impliRomantic3, self.impliTouristTrap1, self.impliMany2,
                                 self.impliChildren2]

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
            answer[i] = self.featureValues[i].truthValue
        return answer


def getConsequences(restaurant):
    implications_ = Implications()
    rules = implications_.implicationRules
    changedValues = True
    loopNumber = 1
    conclusions = []
    iteratie = 0
    while(changedValues and iteratie < 5):
        for i in range(0, len(rules)):
            if rules[i].level == loopNumber:
                tijdelijkFV = rules[i].getFeatureValue(restaurant)
                if tijdelijkFV.truthValue == rules[i].cValue:       # changed: consequence value is returned
                    print(str(tijdelijkFV.name) + " = " + str(tijdelijkFV.truthValue) + " with importance " + str(rules[i].importance))
                    conclusions.append((tijdelijkFV.name, tijdelijkFV.truthValue))
        newInfo = False
        for i in conclusions:           # sterkte van regel wordt nog niet gebruikt
            txtt = implications_.getFeatureValue(i[0])
            txtt_ = str(txtt) if txtt == False else txtt.name + " == " + str(txtt.truthValue)
            #print(str(i[0]) + ", " + str(i[1]) + " -->> " + txtt_)
            newValue = implications_.setFeatureValue(i[0], i[1])
            if newValue == -1:
                #print("ERROR: None, " + i[0] + " is not a featureValue?")
                return None
            elif newValue == 1:
                #print("NIEUWE WAARDE! ! ! !  ! ! ! ! ! ! !! ! ! ! ! ! ")
                newInfo = True
        changedValues = newInfo
        if loopNumber == 1:
            loopNumber = 2
            changedValues = True
        print(loopNumber)
        print("change? " + str(changedValues))
        iteratie += 1
    return implications_.featuresToDictionary()

def printRules():
    temp_ = Implications()
    rules = temp_.implicationRules
    for i in range(0, len(rules)):
        print(rules[i].toString())

zoek = pd.read_csv('restaurant_info4.csv')
eerste = zoek.iloc[4]
print(eerste)
woordenboek = getConsequences(eerste)
print("~~~~~~~~ RULES ~~~~~~~~")
printRules()



"""
tijdelijk = Implications()
tff = tijdelijk.getFeatureValue("romantic2")
if tff is not False:
    print(tff.truthValue)
else:
    print("N O N E")
succes = tijdelijk.setFeatureValue("romantic", True)
print(str(succes) + " >> ")
tff = tijdelijk.getFeatureValue("romantic2")
if tff is not False:
    print(tff.truthValue)
else:
    print("N O N E")


zoek = pd.read_csv('restaurant_info.csv')
zoek1 = zoek.iloc[0]
# print(zoek.iloc[0])

waarde1 = FeatureValue("area", 2, "north")
waarde2 = FeatureValue("food", 3, "british")
#print(waarde1.getTruthValue(zoek1))
#print(waarde2.getTruthValue(zoek1))
fvArea = FeatureValue("area", 2, "north")
fvFood = FeatureValue("food", 3, "british")
fvPrice = FeatureValue("price", 1, "moderate")
fvTrue = FeatureValue("true", -1, None, True)
featureNotNorth = Feature("notNorth", [fvArea], Function.NOT)
feat1 = Feature("test", [featureNotNorth, fvFood, fvTrue], Function.AND)
print("~~~~~~~~feature test~~~~~~~~~~")
#featureNotNorth.print(zoek1)
feat1.print(zoek1)
print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
# print(feat1.getTruthValue(zoek1))


def groet(lijstje: list):
    for i in lijstje:
        print("Hello " + str(i))


#groet(["kees"])
#groet([1, 2])


def getColumnFromName(name):
    if name == "pricerange":
        return 1
    elif name == "area":
        return 2
    elif name == "food":
        return 3
    elif name == "phone":
        return 4
    elif name == "addr":
        return 5
    elif name == "postcode":
        return 6
    else:
        return 0
"""