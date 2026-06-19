import json 

from mcp.server.fastmcp import FastMCP
from gherkin import Parser

mcp = FastMCP("gherkin-mcp")

parser = Parser()

@mcp.tool()
def parse_gherkin(source: str) -> str:
    """
    Parses a Gherkin source string and returns the resulting AST as JSON
    """
    try:
        ast = parser.parse(source)
        return json.dumps(ast, indent=2)
    except Exception as e:
        return json.dumps({"error": str(e)}, indent=2)

def main():
    mcp.run(transport="stdio")
    
if __name__ == "__main__":
    main()
    