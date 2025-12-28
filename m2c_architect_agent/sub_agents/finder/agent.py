"""finder_agent for Researching GCP product equivalents for on-premise infrastructure."""
from m2c_architect_agent.config import MODEL
from google.adk import Agent
from google.adk.tools import google_search


from . import prompt

MODEL = 'gemini-2.0-flash'


finder_agent = Agent(
    model=MODEL,
    name="finder_agent",
    instruction=prompt.FINDER_PROMPT,
    output_key="target_services",
    tools=[google_search],
)