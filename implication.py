import implication_classes as impc


def transpose_list(input_: list):
    """Takes a list of (sub)lists and transposes it. In other words, the first (sub)list will contain all the first
    elements of the input_ sub(lists)
    Parameters
    ----------
    input_ : list
        a list of lists
    Returns
    -------
    It returns a list of lists
    """
    return list(map(list, zip(*input_)))


def solve_conclusions(conclusions: list):
    """Takes a list of tuples that indicate conclusions that the system derived based on the implications and combines
    elements that have the same FeatureValue/name
    Parameters
    ----------
    conclusions : list
        a list with tuples ('name', 'truth value', 'importance', 'list of rules that led to this conclusion')
    Returns
    -------
    It returns an updated list where the tuples with the same name get combined
    """
    answer = []
    for i in conclusions:
        if len(answer) > 0:
            index = list_contains_conclusion(answer, i[0])
            if index > -1:
                answer[index] = merge_conclusions(answer[index], i)
            else:
                answer.append(i)
        else:
            answer.append(i)
    return answer


def list_contains_conclusion(list_: list, name: str):
    """Takes a list of tuples that indicate conclusions and a string, and looks if there is a conclusion where its first
    element is equal to name and returns the index
    Parameters
    ----------
    list_ : str
        the list of conclusions
    name : str
        a string that indicates the name of one of the conclusions
    Returns
    -------
    It returns the index of the element in list_ with the same 'name' as name, or -1 if it is not present
    """
    for i in range(0, len(list_)):
        if list_[i][0] == name:
            return i
    return -1


def merge_conclusions(conclusion1, conclusion2):
    """Takes two conclusions and combines them into one where the truth value is decided based on the truth values
    and importance of the two tuples and the two 'sets' get combined
    Parameters
    ----------
    conclusion1 : tuple
        a tuple with 4 elements: 'name', 'truth value', 'importance', 'set of rules that led to this conclusion'
    conclusion2 : tuple
        a tuple with 4 elements: 'name', 'truth value', 'importance', 'set of rules that led to this conclusion'
    Returns
    -------
    It returns a single tuple with the combination of the elements of the conclusions
    """
    value1 = conclusion1[2] if conclusion1[1] is True else -1 * conclusion1[2]
    value2 = conclusion2[2] if conclusion2[1] is True else -1 * conclusion2[2]
    if set(conclusion2[3]) <= set(conclusion1[3]):
        return conclusion1
    return conclusion1[0], True if value1 + value2 > 0 else False, abs(value1+value2), conclusion1[3]+conclusion2[3]


def get_consequences_single(restaurant):
    """Takes a single restaurant and reasons about said restaurant. It then returns a dictionary with all the
    consequences that could be derived. It keeps on applying implication rules until no new information can be obtained
    In the first cycle it only applies the level 1 rules and in the next cycles it only applies level 2 rules
    Parameters
    ----------
    restaurant : pandas DataFrame
        this dataframe contains 1 row, 1 restaurant
    Returns
    -------
    It returns a dictionary with all the consequences that could be obtained
    """
    implications_ = impc.Implications()
    rules = implications_.implicationRules
    changed_values = True
    loop_number = 1
    conclusions = []
    while changed_values:
        for i in range(0, len(rules)):
            if rules[i].level == loop_number:
                temp_fv = rules[i].get_feature_value(restaurant)
                if temp_fv.truth_value == rules[i].c_value:
                    conclusions.append((temp_fv.name, temp_fv.truth_value, rules[i].importance, [rules[i].id_]))
        conclusions = solve_conclusions(conclusions)
        changed_values = False
        for i in conclusions:
            new_value = implications_.set_feature_value(i[0], i[1])
            if new_value == -1:
                return None
            elif new_value == 1:
                changed_values = True
        if loop_number == 1:
            loop_number = 2
            changed_values = True
    return implications_.features_to_dictionary()


def get_consequences(restaurants):
    """Takes a list of restaurants and reasons about each restaurant, it then turns all the consequences of all
    restaurants into columns and adds these to the pandas dataframe
    Parameters
    ----------
    restaurants : pandas DataFrame
        a dataframe with multiple rows/restaurants
    Returns
    -------
    None
    """
    if restaurants is None:
        return None
    dict_values = []
    for i in range(0, restaurants.shape[0]):
        dict_values.append(list(get_consequences_single(restaurants.iloc[i]).values()))
    transposed = transpose_list(dict_values)
    dictionary0 = list(get_consequences_single(restaurants.iloc[0]).keys())
    for i in range(0, len(transposed)):
        restaurants.insert(len(restaurants.columns), dictionary0[i], transposed[i], False)
