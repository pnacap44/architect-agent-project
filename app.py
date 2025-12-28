import os
import json
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

# --- MOCK DATA ---
MOCK_DATA = {
    "app_purpose": "This is a customer relationship management (CRM) application used by the sales and marketing teams to track leads, opportunities, and customer interactions.",
    "app_owner": "Sales Department",
    "hosting_location": "On-premise datacenter in Frankfurt, Germany",
    "ops_team": "Corporate IT Operations",
    "maintenance_team": "Internal Application Development Team",
    "app_dependencies": "Depends on the corporate Active Directory for authentication and the 'BI-DataWarehouse' for nightly data syncs.",
    "can_move_alone": "No",
    "special_devices": "Connects to a fleet of Zebra RF barcode scanners in the main warehouse for inventory lookup.",
    "origin": "Homemade",
    "package_details": "",
    "intranet_users": "500 users, primarily in EU (Germany, France), connecting via internal network. Identity Provider: Microsoft Active Directory.",
    "internet_users": "50 remote users, global, connecting via VPN. Identity Provider: Microsoft Active Directory.",
    "intranet_s2s": "1 system (BI-DataWarehouse), JDBC, Service Account Credentials",
    "internet_s2s": "None",
    "intranet_entry": "F5 BIG-IP Load Balancer",
    "internet_entry": "Palo Alto Firewall -> F5 BIG-IP",
    "web_tier": "VM, 2 nodes, 4 vCPU, 16GB RAM, 100GB SSD Storage, Windows Server 2019, IIS 10.0, ASP.NET Core 6.0",
    "app_tier": "VM, 2 nodes, 8 vCPU, 32GB RAM, 100GB SSD Storage, Windows Server 2019, Custom Windows Service, .NET Framework 4.8",
    "db_tier": "VM, 1 node (failover cluster), 16 vCPU, 64GB RAM, 2TB SAN Storage, Windows Server 2019, Microsoft SQL Server 2017 Enterprise",
}

# --- CONFIGURATION ---
st.set_page_config(page_title="GCP Architect Agent", layout="centered")
APP_NAME = "m2c_architect_app"
USER_ID = "it_architect_user"
SESSION_ID = "current_session"

st.title("🏗️ GCP M2C Architect Assistant")
st.caption("IT Architect Workbench | Powered by Gemini & Google ADK")

# --- INITIALIZATION ---
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

# --- SIDEBAR TOOLS ---
with st.sidebar:
    st.header("Test Tools")
    if st.button("🚀 Load Mock As-Is Data"):
        mock_prompt = "Here is my current As-Is Architecture for the CRM app:\n\n"
        mock_prompt += json.dumps(MOCK_DATA, indent=2)
        st.session_state.pending_mock = mock_prompt

    if st.button("🗑️ Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT LOGIC ---
prompt = st.chat_input("How can I help with your GCP architecture?")

if "pending_mock" in st.session_state:
    prompt = st.session_state.pop("pending_mock")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
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
                # Check for content and parts before iterating
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            # Render text parts
                            if hasattr(part, 'text') and part.text:
                                full_response += part.text
                                response_placeholder.markdown(full_response + "▌")
                            
                            # Log tool calls to the console for debugging
                            if hasattr(part, 'function_call') and part.function_call:
                                print(f"DEBUG Tool Call: {part.function_call.name}")
            
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})