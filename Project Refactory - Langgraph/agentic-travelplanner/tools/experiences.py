## TOURIST ATTRACTION SEARCH

from langchain.tools import tool

from langchain_community.tools.tavily_search import TavilySearchResults

from config.settings import TAVILY_API_KEY

@tool
def search_tourist_attractions(destination: str) -> str:
    """
    Searches for tourist attractions in a specified destination using the Tavily Search API.

    This tool takes a destination as input and returns a list of popular tourist attractions in that location, including their names, descriptions, and ratings.
      It is useful for travelers who want to explore the key attractions and points of interest at their destination.

    Parameters:
    - destination (str): The location where the traveler wants to find tourist attractions.

    Returns:
    - str: A string describing the popular tourist attractions in the specified destination, including their names, descriptions, and ratings.
    """

    search = TavilySearchResults(k=5)
    search_query = f"Find popular tourist attractions in {destination}."

    attractions = search.invoke(search_query)

    return "\n".join([r['content'] for r in attractions])


## Restaurant Search
@tool
def search_restaurants(destination: str) -> str:
    """
    Searches for restaurants in a specified destination  using the Tavily Search API.

    Parameters:
    - destination (str): The location where the traveler wants to find restaurants.

    Returns:
    - str: A string describing the restaurants that match the search criteria, including their names, locations, and ratings.
    """

    search = TavilySearchResults(k=5)
    search_query = f"Find restaurants to try mandatorily in {destination}."

    restaurants = search.invoke(search_query)

    return "\n".join([r['content'] for r in restaurants])

@tool
def search_activities(destination: str) -> str:
    """
    Searches for activities in a specified destination using the Tavily Search API.

    Parameters:
    - destination (str): The location where the traveler wants to find activities.

    Returns:
    - str: A string describing the activities that match the search criteria, including their names, locations, and ratings.
    """

    search = TavilySearchResults(k=5)
    search_query = f"Find activities to do mandatorily in {destination}."

    activities = search.invoke(search_query)

    return "\n".join([r['content'] for r in activities])


@tool
def search_transportation(destination: str) -> str:
    """
    Searches for transportation options in a specified destination using the Tavily Search API.

    Parameters:
    - destination (str): The location where the traveler wants to find transportation options.

    Returns:
    - str: A string describing the transportation like bus, metro, taxi, etc that match the search criteria.
    """

    search = TavilySearchResults(k=5)
    search_query = f"Find transportation options to use mandatorily in {destination}."

    transportation_options = search.invoke(search_query)

    return "\n".join([r['content'] for r in transportation_options])


