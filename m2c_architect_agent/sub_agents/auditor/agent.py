"""auditor_agent for auditing a GCP architecture design for security, reliability, and cost."""
from m2c_architect_agent.config import MODEL
from google.adk import Agent
from google.adk.tools import google_search

from . import prompt

auditor_agent = Agent(
    model=MODEL,
    name="auditor_agent",
    instruction=prompt.AUDITOR_PROMPT,
    output_key="audit_result",
    tools=[google_search],
)