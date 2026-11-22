import json
from pathlib import Path
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("studio-software-inutile")
SUBMISSIONS_DIR = Path("./submissions")

@mcp.resource("ui://inutile/{student_slug}")
def get_student_applet(student_slug: str) -> str:
    """Serves the single-file HTML applet as an embeddable MCP UI resource."""
    html_path = SUBMISSIONS_DIR / student_slug / "index.html"
    return html_path.read_text(encoding="utf-8")

@mcp.tool()
def disturb_applet_air(student_slug: str, impulse: float = 0.4, temperature: str = "cool") -> dict:
    """Sends a conversational air current payload to a student's embedded applet."""
    return {
        "target_resource": f"ui://inutile/{student_slug}",
        "postMessage": {
            "type": "applet:action",
            "action": "disturb_air",
            "params": {"impulse": impulse, "temperature": temperature}
        }
    }
