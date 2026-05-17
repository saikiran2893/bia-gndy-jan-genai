"""
mcp_server.py — Travel Planner MCP Server (HTTP + SSE)
=======================================================
Exposes all 16 travel tools over HTTP+SSE so any MCP client
(Claude Desktop, LangGraph agent, MCP Inspector) can connect.

Run:
    python mcp_server.py

Server starts at:
    http://localhost:8000/sse    (SSE endpoint for MCP clients)
    http://localhost:8000/       (health check)

For HTTPS (self-signed, local dev):
    python mcp_server.py --https

Connect Claude Desktop:
    {
      "mcpServers": {
        "travel-planner": {
          "url": "http://localhost:8000/sse"
        }
      }
    }
"""

import argparse
import json
import os
import urllib.parse
import urllib.request
from datetime import date, datetime
from pathlib import Path
from typing import Union

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

load_dotenv()

# ── API keys ──────────────────────────────────────────────────────────────────
SERP_API_KEY       = os.getenv("SERP_API_KEY", "")
SERPER_API_KEY     = os.getenv("SERPER_API_KEY", "")
TAVILY_API_KEY     = os.getenv("TAVILY_API_KEY", "")
EXCHANGE_RATE_API  = os.getenv("EXCHANGE_RATE_API", "")

# ── MCP Server ────────────────────────────────────────────────────────────────
mcp = FastMCP(
    name="travel-planner-server",
    instructions=(
        "Travel planning assistant. Provides weather, hotel search, "
        "tourist attractions, restaurants, activities, transportation, "
        "currency exchange, and budget calculation tools."
    ),
)


# ══════════════════════════════════════════════════════════════════════════════
# WEATHER TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def _serp_search(query: str) -> str:
    """Call SerpAPI Google search and return organic snippet text."""
    params = urllib.parse.urlencode({
        "q": query,
        "api_key": SERP_API_KEY,
        "engine": "google",
        "num": 5,
    })
    url = f"https://serpapi.com/search?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("organic_results", [])
        snippets = [r.get("snippet", "") for r in results if r.get("snippet")]
        return "\n".join(snippets) if snippets else "No results found."
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def get_current_weather(target_location: str) -> str:
    """
    Retrieves the current weather conditions for a specified location using SerpAPI.

    Parameters:
    - target_location (str): The location for which to retrieve the current weather conditions.

    Returns:
    - str: Current weather conditions including temperature, humidity, and description.
    """
    query = f"current weather in {target_location} today temperature humidity"
    return _serp_search(query)


@mcp.tool()
def get_weather_forecast(target_location: str, time: str) -> str:
    """
    Retrieves the weather forecast for a specified location and time using SerpAPI.

    Parameters:
    - target_location (str): The location for which to retrieve the weather forecast.
    - time (str): The time for forecast e.g. 'tomorrow', 'next week', '2024-06-15'.

    Returns:
    - str: Weather forecast including temperature, humidity, rain, and description.
    """
    query = f"weather forecast in {target_location} on {time}"
    return _serp_search(query)


# ══════════════════════════════════════════════════════════════════════════════
# HOTEL TOOLS
# ══════════════════════════════════════════════════════════════════════════════

def _serper_search(query: str, k: int = 5) -> str:
    """Call Serper.dev Google Search API."""
    payload = json.dumps({"q": query, "num": k}).encode()
    req = urllib.request.Request(
        "https://google.serper.dev/search",
        data=payload,
        headers={
            "X-API-KEY": SERPER_API_KEY,
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("organic", [])
        snippets = [f"{r.get('title','')}: {r.get('snippet','')}" for r in results]
        return "\n".join(snippets) if snippets else "No results found."
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def search_hotels(destination: str, budget: int) -> str:
    """
    Searches for hotels in a specified destination within a given budget using the Serper API.

    Parameters:
    - destination (str): The location where the traveler wants to find hotels.
    - budget (int): The maximum price per night the traveler is willing to pay (USD).

    Returns:
    - str: Hotels matching the criteria including names, prices, and ratings.
    """
    query = f"best hotels in {destination} under ${budget} per night"
    return _serper_search(query)


@mcp.tool()
def estimate_hotel_cost(price_per_night: float, total_days: int) -> float:
    """
    Estimates the total cost of a hotel stay.

    Parameters:
    - price_per_night (float): Cost per night in USD.
    - total_days (int): Number of days staying at the hotel.

    Returns:
    - float: Total estimated hotel cost.
    """
    try:
        return round(price_per_night * total_days, 2)
    except Exception as e:
        return f"Error: {e}"


# ══════════════════════════════════════════════════════════════════════════════
# EXPERIENCES TOOLS  (uses Tavily)
# ══════════════════════════════════════════════════════════════════════════════

def _tavily_search(query: str, k: int = 5) -> str:
    """Call Tavily Search API."""
    payload = json.dumps({
        "api_key": TAVILY_API_KEY,
        "query": query,
        "max_results": k,
    }).encode()
    req = urllib.request.Request(
        "https://api.tavily.com/search",
        data=payload,
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
        results = data.get("results", [])
        return "\n".join([r.get("content", "") for r in results]) or "No results."
    except Exception as e:
        return f"Search error: {e}"


@mcp.tool()
def search_tourist_attractions(destination: str) -> str:
    """
    Searches for popular tourist attractions in a specified destination using Tavily.

    Parameters:
    - destination (str): The location where the traveler wants to find tourist attractions.

    Returns:
    - str: Popular tourist attractions including names, descriptions, and ratings.
    """
    return _tavily_search(f"Find popular tourist attractions in {destination}.")


@mcp.tool()
def search_restaurants(destination: str) -> str:
    """
    Searches for must-try restaurants in a specified destination using Tavily.

    Parameters:
    - destination (str): The location where the traveler wants to find restaurants.

    Returns:
    - str: Restaurants including names, locations, and ratings.
    """
    return _tavily_search(f"Find restaurants to try mandatorily in {destination}.")


@mcp.tool()
def search_activities(destination: str) -> str:
    """
    Searches for must-do activities in a specified destination using Tavily.

    Parameters:
    - destination (str): The location where the traveler wants to find activities.

    Returns:
    - str: Activities including names, locations, and ratings.
    """
    return _tavily_search(f"Find activities to do mandatorily in {destination}.")


@mcp.tool()
def search_transportation(destination: str) -> str:
    """
    Searches for transportation options in a specified destination using Tavily.

    Parameters:
    - destination (str): The location where the traveler wants to find transportation options.

    Returns:
    - str: Transportation options including bus, metro, taxi descriptions.
    """
    return _tavily_search(f"Find transportation options to use mandatorily in {destination}.")


# ══════════════════════════════════════════════════════════════════════════════
# FINANCE TOOLS
# ══════════════════════════════════════════════════════════════════════════════

@mcp.tool()
def get_exchange_rate(source_currency: str, target_currency: str) -> str:
    """
    Retrieves the exchange rate between two currencies using ExchangeRate-API.

    Parameters:
    - source_currency (str): Source currency code e.g. 'USD'.
    - target_currency (str): Target currency code e.g. 'INR'.

    Returns:
    - str: Current exchange rate between the two currencies.
    """
    url = f"https://v6.exchangerate-api.com/v6/{EXCHANGE_RATE_API}/pair/{source_currency}/{target_currency}"
    try:
        with urllib.request.urlopen(url, timeout=10) as r:
            data = json.loads(r.read())
        if data.get("result") == "success":
            rate = data["conversion_rate"]
            return f"The current exchange rate from {source_currency} to {target_currency} is: {rate}"
        return f"Error retrieving exchange rate: {data.get('error-type', 'unknown')}"
    except Exception as e:
        return f"An error occurred while fetching exchange rate: {e}"


@mcp.tool()
def convert_currency(amount: float, conversion_rate: float) -> float:
    """
    Converts an amount using a given conversion rate.

    Parameters:
    - amount (float): The amount of money to convert.
    - conversion_rate (float): The exchange rate to apply.

    Returns:
    - float: The converted amount rounded to 2 decimal places.
    """
    return round(amount * conversion_rate, 2)


@mcp.tool()
def add(a: float, b: float) -> float:
    """Adds two numbers. Returns a + b."""
    return round(a + b, 2)


@mcp.tool()
def subtract(a: float, b: float) -> float:
    """Subtracts b from a. Returns a - b."""
    return round(a - b, 2)


@mcp.tool()
def multiply(a: float, b: float) -> float:
    """Multiplies two numbers. Returns a * b."""
    return round(a * b, 2)


@mcp.tool()
def divide(a: float, b: float) -> float:
    """
    Divides a by b.

    Parameters:
    - a (float): Dividend.
    - b (float): Divisor (must not be zero).

    Returns:
    - float: The quotient, or an error string if b is zero.
    """
    if b == 0:
        return "Error: Division by zero is not allowed."
    return round(a / b, 2)


@mcp.tool()
def calculate_total_cost(
    hotel_cost: float,
    activity_cost: float,
    restaurant_cost: float,
    transportation_cost: float,
) -> float:
    """
    Calculates the total estimated trip cost.

    Parameters:
    - hotel_cost (float): Total hotel cost.
    - activity_cost (float): Total activities cost.
    - restaurant_cost (float): Total restaurant / food cost.
    - transportation_cost (float): Total transportation cost.

    Returns:
    - float: Total trip cost.
    """
    return round(hotel_cost + activity_cost + restaurant_cost + transportation_cost, 2)


@mcp.tool()
def calculate_daily_budget(total_cost: float, total_days: int) -> float:
    """
    Calculates the daily budget based on total cost and trip duration.

    Parameters:
    - total_cost (float): Total estimated trip cost.
    - total_days (int): Number of trip days.

    Returns:
    - float: Daily budget amount.
    """
    if total_days == 0:
        return "Error: Total days cannot be zero."
    return round(total_cost / total_days, 2)


# ══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Travel Planner MCP Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind (default: 0.0.0.0)")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind (default: 8000)")
    parser.add_argument("--https", action="store_true", help="Enable HTTPS with self-signed cert")
    args = parser.parse_args()

    ssl_certfile = None
    ssl_keyfile  = None

    if args.https:
        # Generate a self-signed certificate for local HTTPS
        cert_path = Path("certs")
        cert_path.mkdir(exist_ok=True)
        ssl_certfile = str(cert_path / "cert.pem")
        ssl_keyfile  = str(cert_path / "key.pem")

        if not Path(ssl_certfile).exists():
            print("Generating self-signed certificate...")
            os.system(
                f'openssl req -x509 -newkey rsa:4096 -keyout {ssl_keyfile} '
                f'-out {ssl_certfile} -days 365 -nodes '
                f'-subj "/CN=localhost"'
            )

        print(f"\n🔒 HTTPS enabled")
        print(f"   SSE endpoint : https://{args.host}:{args.port}/sse")
        print(f"   Health check : https://{args.host}:{args.port}/\n")
    else:
        print(f"\n🚀 Travel Planner MCP Server")
        print(f"   SSE endpoint : http://{args.host}:{args.port}/sse")
        print(f"   Health check : http://{args.host}:{args.port}/")
        print(f"   Tools loaded : 16\n")

    # FastMCP runs a Starlette/uvicorn app under the hood
    mcp.run(
        transport="sse",
        host=args.host,
        port=args.port,
        ssl_certfile=ssl_certfile,
        ssl_keyfile=ssl_keyfile,
    )