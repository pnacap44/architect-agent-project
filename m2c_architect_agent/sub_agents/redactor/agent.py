""" Redactor_agent for formatting the final deliverable."""
from m2c_architect_agent.config import MODEL
from google.adk import Agent

from . import prompt

redactor_agent = Agent(
    model=MODEL,
    name="redactor_agent",
    instruction=prompt.REDACTOR_PROMPT,
)