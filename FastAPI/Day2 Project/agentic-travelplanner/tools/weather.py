## 1. Weather tool

from datetime import date,datetime
from typing import Union
from langchain.tools import tool
from langchain_community.utilities import SerpAPIWrapper
import os
from config.settings import SERP_API_KEY


@tool
def get_current_weather(target_location :str):
    """
    Retrives the current weather conditions for a specified location  using Serper API.

    This tool takes a location as input and returns the current weather conditions, including temperature, humidity, and weather description.
      It is useful for travelers who want to know the weather conditions at their destination before they arrive.

    Parameters:
    - target_location (str): The location for which to retrieve the current weather conditions.

    Returns:
    - str: A string describing the current weather conditions at the specified location.
    """

    google_search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))
    search_query = f"what is the wather in {target_location}?"

    current_weather = google_search.run(search_query)

    return current_weather



@tool
def get_weather_forecast(target_location :str, time: Union[str, date, datetime]):
    """
    Retrieves the weather forecast for a specified location using the SerpAPI .

    This tool takes a location as input and returns the weather forecast for that location, including temperature, humidity,rain and weather description for the upcoming days.
      It is useful for travelers who want to plan their activities based on the expected weather conditions at their destination.

    Parameters:
    - target_location (str): The location for which to retrieve the weather forecast.
    - time (Union[str, date, datetime]): The time for which to retrieve the weather forecast. This can be a string (e.g., "tomorrow", "next week"), a date object, or a datetime object.

    Returns:
    - str: A string describing the weather forecast for the specified location.
    """

    google_search = SerpAPIWrapper(serpapi_api_key=os.getenv("SERP_API_KEY"))
    search_query = f"what is the wather forecast in {target_location} on {time}?"

    predicted_weather = google_search.run(search_query)

    return predicted_weather




