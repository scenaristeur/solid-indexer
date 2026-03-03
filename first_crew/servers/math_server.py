""" A simple MCP server that implements the Model Contect Protocol
This server provides mathematical operations as tools that can be discovered and used bu=y MCP clients
"""

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("Math")

@mcp.tool()
def add (a: float, b: float) -> float: 
    """Add two numbers (ints or floats)"""
    return a + b

@mcp.tool()
def substract (a: float, b: float) -> float: 
    """Substract two numbers (ints or floats)"""
    return a - b

@mcp.tool()
def multiply (a: float, b: float) -> float: 
    """Multiply two numbers (ints or floats)"""
    return a * b

@mcp.tool()
def divide (numerator: float, denominator: float) -> float: 
    """Divide two numbers (floats ok)"""
    if denominator == 0:
        raise ValueError("Cannot divide by zero")
    return numerator / denominator

@mcp.tool()
def power (base: float, exponent: float) -> float: 
    """Raise the base to the power of exponent (floats ok)"""
    return base ** exponent

@mcp.tool()
def sqrt (number: float) -> float: 
    """Calculate the square root of a number"""
    if number < 0:
        raise ValueError("Cannot calculate squre root of a negative number")
    return number ** 0.5

if __name__ == "__main__":
    mcp.run(transport="stdio")