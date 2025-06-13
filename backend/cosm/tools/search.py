from datetime import datetime

from google.adk.agents import Agent
from google.adk.tools import google_search
from google.adk.tools.agent_tool import AgentTool


def get_current_date() -> dict:
    """
    Get the current date in the format YYYY-MM-DD
    """
    return {"current_date": datetime.now().strftime("%Y-%m-%d")}


search_agent = Agent(
    model="gemini-2.5-flash-preview-05-20",
    name="search_agent",
    instruction="""
    You're a specialist in Google Search.
    """,
    tools=[google_search, get_current_date],
)

search_tool = AgentTool(search_agent)
