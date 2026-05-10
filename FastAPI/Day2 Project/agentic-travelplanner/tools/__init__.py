from .weather import get_current_weather,get_weather_forecast
from .hotels import search_hotels, estimate_hotel_cost
from .experiences import (search_activities,
                         search_restaurants,
                         search_tourist_attractions,
                         search_transportation
                         )
from .finance import (get_exchange_rate,
                      convert_currency,
                      add,
                      multiply,
                      subtract,
                      divide,
                      calculate_daily_budget,
                      calculate_total_cost)


ALL_TOOLS = [
    get_current_weather,
    get_weather_forecast,
    search_hotels,
    estimate_hotel_cost,
    search_tourist_attractions,
    search_restaurants,
    search_activities,
    search_transportation,
    get_exchange_rate,
    convert_currency,
    add,
    multiply,
    subtract,
    divide,
    calculate_total_cost,
    calculate_daily_budget
]