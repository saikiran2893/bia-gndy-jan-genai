##  Search Hotel tool


from langchain.tools import tool

from langchain_community.utilities import  GoogleSerperAPIWrapper

@tool
def search_hotels(destination: str,budget:int)-> str:
    """
    Searches for hotels in a specified destination within a given budget using the GoogleSerprer API.

    This tool takes a destination and a budget as input and returns a list of hotels that match the criteria, including their names, prices, and ratings.
      It is useful for travelers who want to find accommodation options that fit their preferences and budget.

    Parameters:
    - destination (str): The location where the traveler wants to find hotels.
    - budget (int): The maximum price the traveler is willing to pay for a hotel.

    Returns:
    - str: A string describing the hotels that match the search criteria, including their names, prices, and ratings.
    """

    search = GoogleSerperAPIWrapper()
    search_query = f"Find hotels in {destination} with a budget of ${budget} ."

    search_hotels = search.run(search_query)

    return search_hotels

## HOTEL ESTIMATION

@tool
def estimate_hotel_cost(price_per_night: float, total_days:int) -> float:
    """
    Estimates the total cost of a hotel stay based on the destination, number of nights, and budget .

    This tool takes a destination, number of nights and returns an estimated total cost for the hotel stay. 

    Parameters:
    - destination (str): The location where the traveler plans to stay.
    - total_days (int): The number of days the traveler intends to stay at the hotel.

    Returns:
    - flaot: A numeric describing the estimated total cost for the hotel stay based on the provided criteria.
    """
    try:
        total_cost = round(price_per_night * total_days, 2)
        return total_cost
    except Exception as e:
        print(f"Error occurred while estimating hotel cost: {e}")
        return str(e)
    
