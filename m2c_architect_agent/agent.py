from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.websearch import websearch_agent

MODEL = 'gemini-2.0-flash'

root_agent = LlmAgent(
    model=MODEL, 
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=prompt.COORDINATOR_PROMPT,
    output_key="seminal_paper",
    tools=[
        AgentTool(agent=websearch_agent),
    ],
)