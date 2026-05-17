import asyncio
import os

import mcp.server.stdio
from mcp.server import Server
from mcp.types import Tool,TextContent,CallToolResult,GetPromptResult,Prompt,PromptMessage, PromptArgument


server = Server("My MCP Day1 Server", "0.1.0")

## Tool Definitions

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="add",
            description="Add two numbers together when user wants to add, sum or combine numeric values",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number to add"},
                    "b": {"type": "number", "description": "Second number to add"}
                },
                "required": ["a", "b"]

            }
            
        ),
        Tool(
            name="subtract",
            description="subtract two numbers together when user wants to find difference between numeric values",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number to subtract"},
                    "b": {"type": "number", "description": "Second number to subtract"}
                },
                "required": ["a", "b"]

            }
            
        ),
        Tool(
            name="multiply",
            description="multiply two numbers together when user wants to find the product of numeric values",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number to multiply"},
                    "b": {"type": "number", "description": "Second number to multiply"}
                },
                "required": ["a", "b"]

            }
            
        ),
        Tool(
            name="divide",
            description="divide two numbers together when user wants to find the quotient of numeric values",
            inputSchema={
                "type": "object",
                "properties": {
                    "a": {"type": "number", "description": "First number to divide"},
                    "b": {"type": "number", "description": "Second number to divide"}
                },
                "required": ["a", "b"]

            }
            
        ),
        Tool(
            name="convert units",
            description="convert units of measurement when user wants to convert between different units (e.g., inches to centimeters, miles to kilometers, etc.)",
            inputSchema={
                "type": "object",
                "properties": {
                    "value": {"type": "number", "description": "The numeric value to convert"},
                    "from_unit": {"type": "string", "description": "The unit to convert from (e.g., 'inches', 'miles', etc.)"},
                    "to_unit": {"type": "string", "description": "The unit to convert to (e.g., 'centimeters', 'kilometers',   etc.)"}
                },
                "required": ["value", "from_unit", "to_unit"]
            }
        ),
        Tool(
            name = "list directory",
            description = "List the contents of a directory on the server when user wants to see files or folders in a specific directory",
            inputSchema = {
                "type": "object",   
                "properties": {
                    "directory_path": {"type": "string", "description": "The path of the directory to list"}
                }
            }
        ),
        Tool(
            name = "read file",
            description = "Read the contents of a file on the server when user wants to see the contents of a specific file",
            inputSchema = {
                "type": "object",
                "properties": {
                    "file_path": {"type": "string", "description": "The path of the file to read"}
                },
                "required": ["file_path"]
            }
            )

    ]


## Tool Handlers
@server.call_tool()
async def call_tool(tool_name: str, arguments: dict) -> CallToolResult:
    if tool_name in ["add", "subtract", "multiply", "divide"]:
        a = float(arguments["a"])
        b = float(arguments["b"])
        if tool_name == "add":
            result = a + b
        elif tool_name == "subtract":
            result = a - b
        elif tool_name == "multiply":
            result = a * b
        elif tool_name == "divide":
            if b == 0:
                return CallToolResult(content=[TextContent(type="text",text="Error: Division by zero is not allowed.")])
            result = a / b
        return CallToolResult(content=[TextContent(type="text",text=str(result))])

    elif tool_name == "convert units":
        value = float(arguments["value"])
        from_unit = arguments["from_unit"].lower()
        to_unit = arguments["to_unit"].lower()

        # Simple conversion logic for demonstration purposes
        if from_unit == "inches" and to_unit == "centimeters":
            result = value * 2.54
        elif from_unit == "miles" and to_unit == "kilometers":
            result = value * 1.60934
        elif from_unit == "kilometers" and to_unit == "miles":
            result = value / 1.60934
        elif from_unit == "celsius" and to_unit == "fahrenheit":
            result = (value * 9/5) + 32
        elif from_unit == "kg" and to_unit == "lbs":
            result = value * 2.20462
        else:
            return CallToolResult(content=[TextContent(type="text",text=f"Conversion from {from_unit} to {to_unit} is not supported.")])
        
        return CallToolResult(content=[TextContent(type="text",text=str(result))])

    elif tool_name == "list directory":
        directory_path = arguments["directory_path"]
        try:
            contents = os.listdir(directory_path)
            return CallToolResult(content=[TextContent(type="text",text=f"Contents of {directory_path}: {', '.join(contents)}")])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text",text=str(e))])
        
    elif tool_name == "read file":
        file_path = arguments["file_path"]
        try:
            with open(file_path, 'r') as file:
                content = file.read()
            return CallToolResult(content=[TextContent(type="text",text=content)])
        except Exception as e:
            return CallToolResult(content=[TextContent(type="text",text=str(e))])


async def main():
    async with mcp.server.stdio.stdio_server() as (reader, writer):
        await server.run(reader, writer,server.create_initialization_options())


if __name__ == "__main__":     
    asyncio.run(main()) 