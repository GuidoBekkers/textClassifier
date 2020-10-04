from enum import Enum


class Function(Enum):
    """An enumeration to distinguish the different logical operators: AND, OR & NOT
    """
    OR = 1
    AND = 0
    NOT = -1


class Implication(object):
    def __init__(self, id_: int, antecedent, consequent: str, c_value: bool, level: int, importance: int = 1):
        """Initialises a new Implication that can be used to determine whether the implication holds for a certain
        restaurant
        Parameters
        ----------
        id_ : int
            an id number to distinguish the different implication rules from one another
        antecedent : Feature or FeatureValue
            the logical condition that must be satisfied in order for the consequent to be true
        consequent : str
            the name of the consequent that follows from the satisfaction of the antecedent
        c_value : bool
            the truth value of the consequent if the antecedent is satisfied
        level : int
            the level of the implication, level 1 means it is solely based on already known features, level 2 means that
            there is at least one feature of which the truth value can only be derived if a level 1 implication has been
            tested
        importance : int
            the 'weight' of the implication, if there happens to be contradictory rules the consequence of those rules
            can be derived by weighing the rules with their importance
        Returns
        -------
        It returns a new Implication
        """
        if not (isinstance(antecedent, Feature) or isinstance(antecedent, FeatureValue)):
            raise ValueError('Antecedent MUST be a Feature')
        self.id_ = id_
        self.antecedent = antecedent
        self.consequent = consequent
        self.level = level
        self.importance = importance
        self.c_value = c_value

    def get_feature_value(self, restaurant):
        """Takes an Implication (self) and a restaurant and creates a FeatureValue based on the consequent of the
        implication
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : Implication
            the Implication that is being tested
        Returns
        -------
        It returns a FeatureValue with the truth value equal to the truth value of the consequent if the antecedent is
        satisfied, otherwise its truth value will be the negation of the truth value of the consequent
        """
        new_value = self.c_value if self.antecedent.get_truth_value(restaurant) else not self.c_value
        return FeatureValue(self.consequent, None, None, new_value)

    def get_truth_value(self, restaurant):
        """Takes an Implication (self) and a restaurant. It determines whether the Implication holds for the restaurant
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : Implication
            the Implication that is being tested
        Returns
        -------
        It returns a boolean that indicates the truth value of the implication for the given restaurant
        """
        return self.antecedent.get_truth_value(restaurant)


class Feature(object):
    def __init__(self, name, value_list: list, function: Function):
        """Initialises a new Feature that can be used as antecedent for an Implication. A Feature has multiple
        FeatureValues or Features that are united with a Function (logical operator)
        An example of a Feature is: A && B, where A/B can be a Feature or a FeatureValue
        Parameters
        ----------
        name : str
            the name of the Feature
        value_list : list
            a list of FeatureValues and/or Features that have the role of operands
        function : Function
            an operator that is used to combine the 'operands' together
        Returns
        -------
        It returns a new Feature
        """
        self.value_list = value_list
        self.function = function
        self.name = name if isinstance(name, str) else str(name)

    def get_truth_value(self, restaurant):
        """Takes a Feature (self) and a restaurant. It determines whether the logical function is satisfied
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : Feature
            the Feature that is being tested
        Returns
        -------
        It returns a boolean that indicates the truth value of the feature for the given restaurant
        """
        if self.function.value == 1:
            return self.get_truth_or(restaurant)
        elif self.function.value == 0:
            return self.get_truth_and(restaurant)
        elif self.function.value == -1:
            if self.value_list[0].get_truth_value(restaurant) is None:
                return None
            return not self.value_list[0].get_truth_value(restaurant)

    def get_truth_or(self, restaurant):
        """Takes a Feature (self) and a restaurant. It determines whether one of the elements of its value_list is True
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : Feature
            the Feature that is being tested
        Returns
        -------
        It returns True if one of the elements of its value_list is True based on the restaurant. If one of the elements
        is None the truth value cannot yet be decided. If all the elements are False it will return False
        """
        answer = False
        for i in self.value_list:
            if i.get_truth_value(restaurant) is None:
                return None
            if i.get_truth_value(restaurant):
                answer = True
        return answer

    def get_truth_and(self, restaurant):
        """Takes a Feature (self) and a restaurant. It determines whether all of the elements of its value_list are True
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : Implication
            the Implication that is being tested
        Returns
        -------
        If one element of its value_list is False, based on the restaurant, it returns False. If one is None it cannot
        yet be decided. If all the elements are True it will return True
        """
        answer = True
        for i in self.value_list:
            if i.get_truth_value(restaurant) is None:
                return None
            if not i.get_truth_value(restaurant):
                answer = False
        return answer


class FeatureValue(object):
    def __init__(self, name: str, column_index, exp_value, truth_value: bool = None):
        """Initialises a new FeatureValue that plays the role of a boolean. It can either have a truth value or it can
        have a column index and expected value that will be used to determine its truth value
        Parameters
        ----------
        name : str
            the name of the FeatureValue
        column_index : int
            the index of the column in the csv file with all the restaurants
        exp_value : str
            the value that is expected to be found in the column in order for the FeatureValue to be True
        truth_value : bool
            whether or not the FeatureValue is true, used for consequences
        Returns
        -------
        It returns a new FeatureValue
        """
        self.name = name.lower()
        self.exp_value = exp_value.lower() if isinstance(exp_value, str) else str(exp_value).lower()
        self.column_index = column_index if isinstance(column_index, int) else -1
        self.truth_value = truth_value

    def get_truth_value(self, restaurant):
        """Takes a FeatureValue (self) and a restaurant. It determines whether the 'boolean' is True
        Parameters
        ----------
        restaurant : pandas DataFrame
            this dataframe contains 1 row, 1 restaurant
        self : FeatureValue
            the FeatureValue for which the truth value is being determined
        Returns
        -------
        It returns a boolean that indicates the truth value of the featureValue for the given restaurant
        """
        if self.truth_value is not None:
            return self.truth_value
        elif self.column_index == -1 and self.truth_value is None:
            return None
        if str(restaurant.iloc[self.column_index]).lower() == self.exp_value:
            return True
        else:
            return False


class Implications(object):
    """Initialises a new FeatureValue that plays the role of a boolean. It can either have a truth value or it can
    have a column index and expected value that will be used to determine its truth value
    Parameters
    ----------
    None

    Returns
    -------
    It returns a new Implications object with all the Implications, Features and FeatureValues necessary for the
    reasoning of the dialog system
    """
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

        # A list of all the FeatureValues that will be used in the implications
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
                              "tourist trap": self.fvTouristTrap}

        self.featureMultiCentre = Feature("multi & centre", [self.fvMultiLang, self.fvCentre], Function.AND)
        self.featureCheapGood = Feature("cheap & good food", [self.fvCheap, self.fvGoodFood], Function.AND)
        self.featureSpicy = Feature("spicy", [self.fvKorean, self.fvThai, self.fvVietnamese], Function.OR)
        self.featureNotSpicy = Feature("not spicy", [self.featureSpicy], Function.NOT)
        self.featureManyExpensive = Feature("many tourists & expensive", [self.fvManyTourist, self.fvExpensive],
                                            Function.AND)
        self.featureSpicyMulti = Feature("spicy & multi language", [self.fvSpicy, self.fvMultiLang], Function.AND)
        self.featureNotSpicyPets = Feature("not spicy & pets allowed", [self.featureNotSpicy, self.fvPets],
                                           Function.AND)

        # Predefined rules
        self.impliBusy1 = Implication(1, self.featureCheapGood, "busy", True, 1, 1)
        self.impliLongTime1 = Implication(2, self.fvSpanish, "long time", True, 1, 1)
        self.impliLongTime2 = Implication(3, self.fvBusy, "long time", True, 2, 1)
        self.impliChildren1 = Implication(4, self.fvLongTime, "children", False, 2, 1)
        self.impliRomantic1 = Implication(5, self.fvBusy, "romantic", False, 2, 3)
        self.impliRomantic2 = Implication(6, self.fvLongTime, "romantic", True, 2, 2)
        # New rules: level 1
        self.impliDirty1 = Implication(7, self.fvPets, "dirty", True, 1, 1)
        self.impliMany1 = Implication(8, self.featureMultiCentre, "many tourists", True, 1, 1)
        self.impliSpicy1 = Implication(9, self.featureSpicy, "spicy", True, 1, 1)
        self.impliRomantic3 = Implication(10, self.fvGoodFood, "romantic", True, 1, 2)
        # New rules: level 2
        self.impliRomantic4 = Implication(11, self.fvDirty, "romantic", False, 2, 6)
        self.impliTouristTrap1 = Implication(12, self.featureManyExpensive, "tourist trap", True, 2, 1)
        self.impliMany2 = Implication(13, self.featureSpicyMulti, "many tourists", True, 2, 1)
        self.impliChildren2 = Implication(14, self.featureNotSpicyPets, "children", True, 2, 2)

        # List of all rules
        self.implicationRules = [self.impliBusy1, self.impliLongTime1, self.impliLongTime2, self.impliChildren1,
                                 self.impliRomantic1, self.impliRomantic2, self.impliDirty1, self.impliMany1,
                                 self.impliSpicy1, self.impliRomantic3, self.impliRomantic4, self.impliTouristTrap1,
                                 self.impliMany2, self.impliChildren2]

    def get_feature_value(self, name: str):
        """Takes a Implications (self) and a string and tries to find the FeatureValue with the name being equal to the
        string
        Parameters
        ----------
        name : str
            the name of one of the FeatureValues present in the Implications object
        self : Implications
            the Implications object that contains all the information for the reasoning
        Returns
        -------
        It returns the FeatureValue with that string as name, or False if no such FeatureValue exists
        """
        if name in self.featureValues:
            return self.featureValues[name]
        return False

    def set_feature_value(self, name: str, new_value: bool) -> int:
        """Takes a FeatureValue (self) and a restaurant. It determines whether the 'boolean' is True
        Parameters
        ----------
        name : str
            the name of one of the FeatureValues present in the Implications object
        new_value : bool
            a boolean that indicates the updated truth value of the FeatureValue
        self : Implications
            the Implications object that contains all the information for the reasoning
        Returns
        -------
        It returns an int to indicate the success of updating the truth value of a certain FeatureValue
        0 means that the truth value already has new_value, 1 means that the truth value has been updated successfully
        -1 means that the FeatureValue does not exist or the new_value is None
        """
        if new_value is not None:
            if name in self.featureValues:
                antwoord = 0 if self.featureValues[name].truth_value == new_value else 1
                self.featureValues[name].truth_value = new_value
                return antwoord
        return -1

    def features_to_dictionary(self):
        """Takes an Implications object and turns its newly derived FeatureValues into a dictionary
        Parameters
        ----------
        self : Implications
            the Implications object that contains all the information for the reasoning
        Returns
        -------
        It returns a dictionary with all the (new) FeatureValues as keys and their respective truth value as values
        """
        answer = {}
        for i in self.featureValues:
            if self.featureValues[i].column_index == -1:
                answer[i] = self.featureValues[i].truth_value
        return answer
