import asyncio
from html import unescape
import os
import re

import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool,TextContent,CallToolResult,GetPromptResult,Prompt,PromptMessage, PromptArgument
from pathlib import Path
import sqlite3
import urllib.parse
import urllib.request
import json 
import re
from html import unescape
import ssl



DB_PATH = Path(__file__).parent / "demo.db"

server = Server("My MCP Day2 Server", "0.1.0")



ssl._create_default_https_context = ssl._create_unverified_context


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row          # rows behave like dicts
    return conn
    

def rows_to_text(rows):
    if not rows:
        return "No data found."
    headers = list(rows[0].keys())
    divider = "*" * (len(headers) *15)
    return "\n".join([", ".join(map(str, row)) for row in rows])



## Tool Definitions
@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="list_tables",
            description="List all tables in the demo database. Useful for debugging and verifying database setup.",
            inputSchema={"type": "object", "properties": {}}
        ),
        Tool(
            name="query_table",
            description="Query a specific table in the demo database and return results. Input should specify the table name and optional filters.",
            inputSchema={
                "type": "object",
                "properties": {
                    "table_name": {"type": "string", "description": "Name of the table to query (e.g., customers, orders, products)"},
                    "filters": {"type": "object", "description": "Optional filters for querying the table (e.g., {\"city\": \"New York\"})"},
                    "limit": {"type": "integer", "description": "Optional limit on number of results to return (default: 5)"}
                },
                "required": ["table_name"]
            }
        ),
        Tool(
            name="run_sql",
            description="Run a raw SQL query against the demo database. use it for joins or aggregations. Only select statements are allowed for security reasons.",
            inputSchema={"type": "object", "properties": {
                         "sql_query": {"type": "string", "description": "The SQL query to execute "}
                         },
                         "required": ["sql_query"]
                         }
        ),
        Tool(
            name="weather_tool",
            description="Get current weather information for a specified city. Input should include the city name.No API is reqired",
            inputSchema={
                "type": "object",
                "properties": {
                    "city": {"type": "string", "description": "Name of the city to get weather information for"}
                },
                "required": ["city"]
            }
        ),
        Tool(
            name="web_search",
            description="Perform a web search for a given query and return the top results. Input should include the search query.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "The search query to perform the web search for"},
                    "max_results": {"type": "integer", "description": "Maximum number of search results to return (default: 5)"}
                },                "required": ["query"]
            }
        ),
        Tool(
            name="summarize_text",
            description="Summarize a given piece of text. Input should include the text to summarize and an optional summary length.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "The text to summarize"},
                    "summary_length": {"type": "integer", "description": "The desired length of the summary in number of sentences (default: 5)"}
                },  
                "required": ["text"]
            }
        )

    ]


## Tool handlers
@server.call_tool()
async def list_tables_handler(tool_name: str, arguments: dict) -> CallToolResult:
    if tool_name == "list_tables":
        conn = get_db()
        rows = conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        conn.close()
        tables = [r["name"] for r in rows]
        return CallToolResult(content=[TextContent(type="text",text="The tables in the database are: " + ", ".join(f"{t}" for t in tables))])
    
    elif tool_name == "query_table":
        table_name = arguments["table_name"]
        filters = arguments.get("filters", {})
        limit = arguments.get("limit", 5)

        conn = get_db()
        query = f"SELECT * FROM {table_name}"
        if filters:
            filter_clauses = [f"{k}='{v}'" for k, v in filters.items()]
            query += " WHERE " + " AND ".join(filter_clauses)
        query += f" LIMIT {limit};"

        try:
            rows = conn.execute(query).fetchall()
            conn.close()
            return CallToolResult(content=[TextContent(type="text",text=rows_to_text(rows))])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text",text=f"Error querying table: {str(e)}")])
        
    elif tool_name == "run_sql":
        sql_query = arguments["sql_query"]
        if not sql_query.strip().lower().startswith("select"):
            return CallToolResult(content=[TextContent(type="text",text="Only SELECT statements are allowed for security reasons.")])
        
        conn = get_db()
        try:
            rows = conn.execute(sql_query).fetchall()
            conn.close()
            return CallToolResult(content=[TextContent(type="text",text=rows_to_text(rows))])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text",text=f"Error executing SQL query: {str(e)}")])


    elif tool_name == "weather_tool":
        city = arguments["city"]
        try:
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={urllib.parse.quote(city)}&count=1"
            with  urllib.request.urlopen(geo_url) as response:
                geo_data = json.loads(response.read())
            if not geo_data.get("results"):
                return CallToolResult(content=[TextContent(type="text",text=f"City '{city}' not found.")])
            lat = geo_data["results"][0]["latitude"]
            lon = geo_data["results"][0]["longitude"]
            city = geo_data["results"][0]["name"]
            country = geo_data["results"][0]["country"]

            # Step 2: Fetch weather
            wx_url = (
                f"https://api.open-meteo.com/v1/forecast"
                f"?latitude={lat}&longitude={lon}"
                f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,weathercode"
                f"&timezone=auto"
            )

            with urllib.request.urlopen(wx_url, timeout=8) as r:
                wx = json.loads(r.read())
            
            curr = wx.get("current", {})

            text = f"Current weather in {city}, {country}:\n"
            text += f"Temperature: {curr.get('temperature_2m', 'N/A')}°C\n"
            text += f"Humidity: {curr.get('relative_humidity_2m', 'N/A')}%\n"
            text += f"Wind Speed: {curr.get('wind_speed_10m', 'N/A')} m/s\n"
            weather_info = text

            return CallToolResult(content=[TextContent(type="text",text=weather_info)])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text",text=f"Error fetching weather data: {str(e)}")])
        

    elif tool_name == "web_search":
        query = arguments["query"]
        max_results = arguments.get("max_results", 5)
        try:
            search_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(query)}"

            headers = {
                "User-Agent": "Mozilla/5.0"
            }

            request = urllib.request.Request(search_url, headers=headers)

            with urllib.request.urlopen(request, timeout=10) as response:
                html = response.read().decode("utf-8")

            pattern = r'<a rel="nofollow" class="result__a" href="(.*?)">(.*?)</a>'

            matches = re.findall(pattern, html)

            if not matches:
                return CallToolResult(
                    content=[TextContent(type="text", text="No search results found.")]
                )

            result_text = "Top search results:\n\n"

            for i, (url, title) in enumerate(matches[:max_results], 1):
                clean_title = re.sub("<.*?>", "", unescape(title))
                clean_url = unescape(url)

                result_text += f"{i}. {clean_title}\n{clean_url}\n\n"

            return CallToolResult(
                content=[TextContent(type="text", text=result_text)]
            )

        except Exception as e:
            return CallToolResult(
            content=[TextContent(type="text", text=f"Error performing web search: {str(e)}")]
            )
        
    elif tool_name == "summarize_text":
        text = arguments["text"]
        summary_length = arguments.get("summary_length", 3)
        sentences = text.split(". ")
        if len(sentences) <= summary_length:
            summary = text
        else:
            summary = ". ".join(sentences[:summary_length]) + "..."
        return CallToolResult(content=[TextContent(type="text",text=summary)])

async def main():
    async with mcp.server.stdio.stdio_server() as (reader, writer):
        await server.run(reader, writer,server.create_initialization_options())


if __name__ == "__main__":     
    asyncio.run(main()) 