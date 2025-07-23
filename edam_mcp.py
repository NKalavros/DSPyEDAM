
from mcp.server.fastmcp import FastMCP
from typing import Optional, Dict, Any
import os

# Import the vignette-based matcher
from vignette_edam_matcher import VignetteEDAMMatcher

# Load EDAM matcher system (singleton)
edam_csv_path = os.getenv("EDAM_CSV_PATH", "EDAM.csv")

# Use vignette-based matcher for MCP
matcher_system = VignetteEDAMMatcher(edam_csv_path=edam_csv_path)

mcp = FastMCP("EDAM Ontology MCP Server (Vignette-based)")

@mcp.tool()
def edam_match(name: str) -> Dict[str, Any]:
    """
    Match a Bioconductor package to EDAM ontology using vignette-based matching.
    Auto-discovers and processes vignettes, returns structured output with suggestions.
    Truncates or summarizes the description to 200 characters using GPT-4o if needed.
    """
    import openai
    results = matcher_system.process_packages([name])
    if not results["packages"]:
        return {"error": f"No vignette or match found for package: {name}"}
    pkg = results["packages"][0]
    desc = pkg.get("description")
    if desc and len(desc) > 200:
        try:
            client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            prompt = f"Summarize the following text in 200 characters or less, preserving the main point and technical context:\n\n{desc}"
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=200,
                temperature=0.3,
            )
            message = response.choices[0].message
            if message and message.content:
                summary = message.content.strip()
                pkg["description"] = summary[:200]
            else:
                pkg["description"] = desc[:200] + "..."
        except Exception as e:
            # Fallback: just truncate
            pkg["description"] = desc[:200] + "..."
    return pkg

if __name__ == "__main__":
    mcp.run(transport="streamable-http")