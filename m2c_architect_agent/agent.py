from .config import MODEL, MAX_REJECTIONS
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool

from . import prompt
from .sub_agents.auditor import auditor_agent
from .sub_agents.designer import designer_agent
from .sub_agents.finder import finder_agent
from .sub_agents.redactor import redactor_agent

from .config import MODEL, MAX_REJECTIONS

root_agent = LlmAgent(
    model=MODEL, 
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction=prompt.COORDINATOR_PROMPT.format(
        MAX_REJECTIONS=MAX_REJECTIONS,
        ATTEMPT_COUNT=0
    ),
    output_key="seminal_paper",
    tools=[
        AgentTool(agent=finder_agent),
        AgentTool(agent=designer_agent),
        AgentTool(agent=auditor_agent),
        AgentTool(agent=redactor_agent),
    ],
)