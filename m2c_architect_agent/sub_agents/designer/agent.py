""" Designer_agent for Generating a formal technical architecture document."""
from m2c_architect_agent.config import MODEL
from google.adk import Agent

from . import prompt

designer_agent = Agent(
    model=MODEL,
    name="designer_agent",
    instruction=prompt.DESIGNER_PROMPT,
    output_key="target_architecture",
)