
import os
from dotenv import load_dotenv

# This points to the .env file created by 'adk create'
# It contains GOOGLE_CLOUD_PROJECT and other credentials
load_dotenv(os.path.join("m2c_architect_agent", ".env"))

import streamlit as st
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
# Ensure your folder is named 'm2c_architect_agent' and contains agent.py
from m2c_architect_agent.agent import root_agent

# --- CONFIGURATION ---
st.set_page_config(page_title="GCP Architect Agent", layout="centered")
APP_NAME = "m2c_architect_app"
USER_ID = "it_architect_user"
SESSION_ID = "current_session"

st.title("🏗️ GCP M2C Architect Assistant")
st.caption("IT Architect Workbench | Powered by Gemini & Google ADK")

# --- INITIALIZATION ---
# We use st.session_state to ensure the Runner and Session persist across UI refreshes
if "runner" not in st.session_state:
    # 1. Initialize the Session Service
    st.session_state.session_service = InMemorySessionService()
    
    # 2. Initialize the Runner
    st.session_state.runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME, 
        session_service=st.session_state.session_service
    )
    st.session_state.messages = []
    
    # 3. Register the session in the service (Required by ADK)
    asyncio.run(st.session_state.session_service.create_session(
        user_id=USER_ID, 
        session_id=SESSION_ID,
        app_name=APP_NAME
    ))

# --- CHAT INTERFACE ---
# Display chat history from the session state
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT ---
if prompt := st.chat_input("How can I help with your GCP architecture?"):
    # Add user message to UI
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate assistant response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        # 4. Format the input for ADK's internal event loop
        new_message = types.Content(
            role="user",
            parts=[types.Part(text=prompt)]
        )
        
        try:
                    # 5. Execute the agent runner
                    for event in st.session_state.runner.run(
                        user_id=USER_ID,
                        session_id=SESSION_ID,
                        new_message=new_message
                    ):
                        # Check 1: Does the event have content?
                        if hasattr(event, 'content') and event.content is not None:
                            # Check 2: Does the content have parts?
                            if hasattr(event.content, 'parts') and event.content.parts:
                                for part in event.content.parts:
                                    # Check 3: Is it a text part? (Skips function_calls)
                                    if hasattr(part, 'text') and part.text:
                                        full_response += part.text
                                        response_placeholder.markdown(full_response + "▌")
                    
                    # Final render without the cursor
                    response_placeholder.markdown(full_response)
                    
        except Exception as e:
                st.error(f"Execution Error: {str(e)}")
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})