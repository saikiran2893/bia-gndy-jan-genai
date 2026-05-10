## EXCHANGE RATE TOOL
import requests
from langchain.tools import tool
import os
from config.settings import EXCHANGE_RATE_API

@tool
def get_exchange_rate(source_currency: str, target_currency: str) -> float:
    """
    Retrieves the exchange rate between two specified currencies using the Exchange Rate API.

    This tool takes a source currency and a target currency as input and returns the current exchange rate between them.
      It is useful for travelers who want to know the value of their home currency in terms of the local currency at their destination.

    Parameters:
    - source_currency (str): The currency code of the source currency (e.g., "USD" for US Dollar).
    - target_currency (str): The currency code of the target currency (e.g., "EUR" for Euro).

    Returns:
    - float: The exchange rate between the source and target currencies.
    """

    api_key = EXCHANGE_RATE_API
    url = f"https://v6.exchangerate-api.com/v6/{api_key}/pair/{source_currency}/{target_currency}"

    try:
        response = requests.get(url)
        data = response.json()

        if data['result'] == 'success':
            exchange_rate = data['conversion_rate']
            return f"The current exchange rate from {source_currency} to {target_currency} is: {exchange_rate}"
        else:
            return f"Error retrieving exchange rate: {data['error-type']}"

    except Exception as e:
        return f"An error occurred while fetching exchange rate: {e}"
    

@tool
def convert_currency(amount: float, conversion_rate: float) -> float:
    """
    Converts a specified amount from a source currency to a target currency using the Exchange Rate API.

    This tool takes an amount, a source currency, and a target currency as input and returns the converted amount in the target currency.
      It is useful for travelers who want to know how much their money is worth in the local currency at their destination.

    Parameters:
    - amount (float): The amount of money to convert.
=   - conversion_rate (float): The exchange rate between the source and target currencies.

    Returns:
    - float: The converted amount in the target currency.
    """

    return round(amount * conversion_rate, 2)


## ARITHMETIC CALCULATOR

@tool
def add(a: float, b: float) -> float:
    """
    Adds two numbers together.

    Parameters:
    - a (float): The first number to add.
    - b (float): The second number to add.

    Returns:
    - float: The sum of the two numbers.
    """
    return round(a + b, 2)


@tool
def subtract(a: float, b: float) -> float:
    """
    Subtracts one number from another.

    Parameters:
    - a (float): The number to be subtracted from.
    - b (float): The number to subtract.

    Returns:
    - float: The difference between the two numbers.
    """
    return round(a - b, 2)

@tool
def multiply(a: float, b: float) -> float:
    """
    Multiplies two numbers together.

    Parameters:
    - a (float): The first number to multiply.
    - b (float): The second number to multiply.

    Returns:
    - float: The product of the two numbers.
    """
    return round(a * b, 2)

@tool
def divide(a: float, b: float) -> float:
    """
    Divides one number by another.

    Parameters:
    - a (float): The number to be divided.
    - b (float): The number to divide by.

    Returns:
    - float: The quotient of the two numbers.
    """
    if b == 0:
        return "Error: Division by zero is not allowed."
    return round(a / b, 2)


@tool
def calculate_total_cost(hotel_cost: float, activity_cost: float, restaurant_cost: float, transportation_cost: float) -> float:
    """
    Calculates the total cost of a trip based on hotel, activity, restaurant, and transportation costs.

    Parameters:
    - hotel_cost (float): The total cost of the hotel stay.
    - activity_cost (float): The total cost of activities planned for the trip.
    - restaurant_cost (float): The total cost of meals at restaurants during the trip.
    - transportation_cost (float): The total cost of transportation during the trip.

    Returns:
    - float: The total estimated cost of the trip.
    """
    return round(hotel_cost + activity_cost + restaurant_cost + transportation_cost, 2)


@tool
def calculate_daily_budget(total_cost: float, total_days: int) -> float:
    """
    Calculates the daily budget for a trip based on the total estimated cost and the number of days.

    Parameters:
    - total_cost (float): The total estimated cost of the trip.
    - total_days (int): The number of days the trip will last.

    Returns:
    - float: The daily budget for the trip.
    """
    if total_days == 0:
        return "Error: Total days cannot be zero."
    return round(total_cost / total_days, 2)