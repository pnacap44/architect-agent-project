"""Exporter agent for saving the final deliverable to GCS."""
from m2c_architect_agent.config import MODEL
from m2c_architect_agent.tools.gcs_bucket_tool import upload_docx_to_gcs
from google.adk import Agent

from . import prompt

exporter_agent = Agent(
    model=MODEL,
    name="exporter_agent",
    description='Specialized agent for exporting a document in .docx format to a Google Cloud Storage bucket.',
    instruction=prompt.EXPORTER_PROMPT,
    tools=[upload_docx_to_gcs]
)