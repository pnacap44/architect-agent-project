import os
import sys
import asyncio
from dotenv import load_dotenv

# --- Path Correction ---
# Add the project root to the Python path. This allows the script to be run directly
# and resolves the "attempted relative import with no known parent package" error.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

# This points to the .env file in the m2c_architect_agent directory.
# Ensure your .env file has GOOGLE_SERVICE_ACCOUNT_FILE and GOOGLE_DRIVE_FOLDER_ID.
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

# The path correction above allows for a stable, absolute import.
from m2c_architect_agent.sub_agents.exporter import exporter_agent

# --- Test Configuration ---
APP_NAME = "exporter_test_app"
USER_ID = "test_user"
SESSION_ID = "test_session"

# --- Mock Data ---
# This is the data that the exporter agent will use to create the document.
MOCK_DOCUMENT_CONTENT = """
# GCP Architecture for Legacy CRM

## TECHNICAL ARCHITECTURE DESCRIPTION
### Overview
This document outlines the proposed Google Cloud Platform (GCP) target architecture for the Legacy CRM application. The migration strategy is a "Replatform" approach, aiming to leverage managed services for improved scalability, reliability, and operational efficiency.

### Components
- **Web Tier:** Google Cloud Run for containerized ASP.NET Core application.
- **App Tier:** Google Compute Engine (GCE) for the .NET Framework components.
- **Database Tier:** Cloud SQL for SQL Server.
- **Authentication:** Managed Service for Microsoft Active Directory.
"""

async def run_test():
    """
    Initializes and runs the exporter agent test.
    """
    print("--- Initializing Exporter Agent Test ---")

    # 1. Set up the runner for the exporter agent
    session_service = InMemorySessionService()
    runner = Runner(
        agent=exporter_agent,
        app_name=APP_NAME,
        session_service=session_service
    )
    await session_service.create_session(
        user_id=USER_ID,
        session_id=SESSION_ID,
        app_name=APP_NAME
    )

    # 2. Create the prompt for the agent.
    # The prompt is now just the markdown content that the exporter agent needs to process.
    # The agent's own instructions will guide it to call the correct tool.
    prompt_text = MOCK_DOCUMENT_CONTENT

    print(f"\n--- Sending Prompt to Agent ---\n{prompt_text}")

    new_message = types.Content(role="user", parts=[types.Part(text=prompt_text)])

    # 3. Run the agent and print the response
    print("\n--- Agent Response ---")
    try:
        # The runner yields events. We need to check for both text and tool outputs within the event parts.
        for event in runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=new_message):
            if event.content and event.content.parts:
                for part in event.content.parts:
                    # Handle text output from the agent
                    if part.text:
                        print(part.text, end="", flush=True)
                    
                    # Handle the result of a tool call. The result is in a `Part` with a `function_response`.
                    if hasattr(part, 'function_response') and part.function_response:
                        print(f"\n\n[TOOL RESULT: {part.function_response.name}]")
                        if 'content' in part.function_response.response:
                            print(part.function_response.response['content'])
    except Exception as e:
        print(f"\nAn error occurred: {e}")

    print("\n\n--- Test Complete ---")


if __name__ == "__main__":
    asyncio.run(run_test())