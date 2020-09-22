import pandas as pd


def lookup(area=None, food=None, pricerange=None):
    """Looks up the restaurant(s) from the csv based on the preferences given by the user.
    :type area:str
    :type food:str
    :type pricerange: str
    :return restaurants: DataFrame
    """
    restaurants = pd.read_csv('restaurant_info.csv')
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


matches = lookup(area='East', food='Steakhouse')
if len(matches) > 0:
    print(f"Restaurants found: {len(matches)}")
    match = matches.iloc[0]
    print(f'First match: {match.restaurantname}. Address: {match.addr}. Phone: {match.phone}. Postcode: {match.postcode}')
else:
    print('No restaurants found!')
