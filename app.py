import os
import json
from dotenv import load_dotenv

# This points to the .env file created by 'adk create'
load_dotenv(os.path.join("m2c_architect_agent", ".env"))

import streamlit as st
import asyncio
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from m2c_architect_agent.agent import root_agent

# --- MOCK DATA REPOSITORY ---
MOCK_REPOS = {
    "Mock 1: CRM Application (Windows/SQL)": {
        "app_name": "Legacy CRM",
        "app_purpose": "Customer relationship management for sales and marketing.",
        "app_owner": "Sales & Marketing Department",
        "hosting_location": "On-premise datacenter in Frankfurt",
        "ops_team": "Windows Server Ops Team",
        "maintenance_team": "In-house Application Development Team",
        "app_dependencies": "Active Directory, BI-DataWarehouse",
        "can_move_alone": "Yes",
        "special_devices": "Zebra RF barcode scanners",
        "origin": "In-house development",
        "package_details": "N/A",
        "intranet_users": "200 concurrent users",
        "internet_users": "50 remote sales agents via VPN",
        "intranet_s2s": "Nightly batch sync with BI-DataWarehouse",
        "internet_s2s": "N/A",
        "intranet_entry": "Direct via internal DNS",
        "internet_entry": "N/A",
        "web_tier": "2x Windows Server 2019, IIS, ASP.NET Core 6.0, 2 vCpu, 8 GiB Ram, 50 GiB SSD storage",
        "app_tier": "2x Windows Server 2019, .NET Framework 4.8, 4 vCpu, 16 GiB Ram, 50 GiB SSD storage",
        "db_tier": "1 node (failover cluster), MSSQL Server 2017 Enterprise, 4 vCpu, 32 GiB Ram, 100 GiB SSD storage",
    },
    "Mock 2: SAP HANA (Linux/SUSE)": {
        "app_name": "ERP Core - SAP HANA",
        "app_purpose": "Production ERP system for global supply chain and finance.",
        "app_owner": "Finance & Global Supply Chain",
        "hosting_location": "On-premise Private Cloud (VMware)",
        "ops_team": "SAP Basis Operations Team",
        "maintenance_team": "External SAP Platinum Support",
        "app_dependencies": "SAP Fiori Front-end, Solution Manager, SuccessFactors (Cloud)",
        "can_move_alone": "No - requires synchronous migration with Fiori frontend",
        "special_devices": "High-speed label printers in Logistics hubs",
        "origin": "SAP Standard + Heavy Customizations (ABAP)",
        "package_details": "S/4HANA 2022 FPS02",
        "intranet_users": "5000 concurrent users via SAP GUI and Fiori",
        "internet_users": "200 remote buyers via SAP Ariba integration",
        "intranet_s2s": "RFC calls to Warehouse Management System",
        "internet_s2s": "OData API to Salesforce via SAP PI/PO",
        "intranet_entry": "SAP Web Dispatcher",
        "internet_entry": "Citrix NetScaler -> SAP Web Dispatcher",
        "web_tier": "4 nodes, SUSE Linux Enterprise (SLES), SAP Web Dispatcher. Per Node: 4 vCPU, 16GB RAM. Storage: 100GB Standard Persistent Disk (OS/Binaries).",
        "app_tier": "6 nodes, SLES, SAP PAS/AAS (ABAP Application Server). Per Node: 16 vCPU, 64GB RAM. Storage: 250GB Balanced Persistent Disk (SAPS-optimized).",
        "db_tier": "HANA Scale-up, 1 Primary + 1 Secondary (HSR), SLES for SAP. Per Node: 128 vCPU, 4TB RAM (Certified M3-Ultramem-128). Storage: 1TB Extreme PD (Log), 5TB Hyperdisk Balanced (Data), 1TB Balanced PD (Shared/Binary).",
    }
}

# --- CONFIGURATION ---
st.set_page_config(page_title="GCP Architect Agent", layout="wide") # Widened for better code view
APP_NAME = "m2c_architect_app"
USER_ID = "it_architect_user"
SESSION_ID = "current_session"

st.title("🏗️ GCP M2C Architect Assistant")
st.caption("IT Architect Workbench | Powered by Gemini & Google ADK")

# --- INITIALIZATION ---
if "runner" not in st.session_state:
    st.session_state.session_service = InMemorySessionService()
    st.session_state.runner = Runner(
        agent=root_agent, 
        app_name=APP_NAME, 
        session_service=st.session_state.session_service
    )
    # Start with a helpful system message that outlines the requirements
    initial_greeting = """Hello! I'm ready to help you design your GCP target architecture. 
To provide an accurate assessment, please provide the following details:

**1. General Information**
- App Name, Purpose, Owner, Hosting Location, Ops/Maintenance Teams.

**2. Migration Path**
- Dependencies, Special Devices (e.g. Scanners), Origin (Homemade/Package).

**3. Users & Connectivity**
- Intranet/Internet user counts, Entry points (Load Balancers/Firewalls), S2S integrations.

**4. Technical Tiers (Web, App, DB)**
- Per tier: Number of nodes, OS, vCPU, RAM, Storage type/size, and Middlewares."""

    st.session_state.messages = [{"role": "assistant", "content": initial_greeting}]
    
    asyncio.run(st.session_state.session_service.create_session(
        user_id=USER_ID, 
        session_id=SESSION_ID,
        app_name=APP_NAME
    ))
# --- 1. Define the Template for the Prompt ---
REQUEST_TEMPLATE = """
Please analyze the following As-Is Architecture and provide a GCP Target State recommendation:

### General Information
- **App Name:** {app_name}
- **Purpose:** {app_purpose}
- **Owner:** {app_owner}
- **Hosting:** {hosting_location}
- **Operations:** {ops_team}
- **Maintenance:** {maintenance_team}

### Migration Path & Influencers
- **Dependencies:** {app_dependencies}
- **Can Move Alone:** {can_move_alone}
- **Special Devices:** {special_devices}
- **Origin:** {origin}
- **Package Details:** {package_details}

### Users & Connectivity
- **Intranet Users:** {intranet_users}
- **Internet Users:** {internet_users}
- **Intranet S2S:** {intranet_s2s}
- **Internet S2S:** {internet_s2s}
- **Intranet Entry:** {intranet_entry}
- **Internet Entry:** {internet_entry}

### Infrastructure Tiers
- **Web Tier:** {web_tier}
- **App Tier:** {app_tier}
- **DB Tier:** {db_tier}
"""

# --- SIDEBAR TOOLS ---
# --- 2. Update the Sidebar Logic ---
with st.sidebar:
    st.header("Test Tools")
    
    selected_mock_key = st.selectbox("Select Scenario:", list(MOCK_REPOS.keys()))
    selected_mock_data = MOCK_REPOS[selected_mock_key]

    if st.button("🚀 Load Selected Mock"):
        # Format the template with the dictionary values
        formatted_request = REQUEST_TEMPLATE.format(
            app_name=selected_mock_data.get("app_name", "N/A"),
            app_purpose=selected_mock_data.get("app_purpose", "N/A"),
            app_owner=selected_mock_data.get("app_owner", "N/A"),
            hosting_location=selected_mock_data.get("hosting_location", "N/A"),
            ops_team=selected_mock_data.get("ops_team", "N/A"),
            maintenance_team=selected_mock_data.get("maintenance_team", "N/A"),
            app_dependencies=selected_mock_data.get("app_dependencies", "N/A"),
            can_move_alone=selected_mock_data.get("can_move_alone", "N/A"),
            special_devices=selected_mock_data.get("special_devices", "N/A"),
            origin=selected_mock_data.get("origin", "N/A"),
            package_details=selected_mock_data.get("package_details", "N/A"),
            intranet_users=selected_mock_data.get("intranet_users", "N/A"),
            internet_users=selected_mock_data.get("internet_users", "N/A"),
            intranet_s2s=selected_mock_data.get("intranet_s2s", "N/A"),
            internet_s2s=selected_mock_data.get("internet_s2s", "N/A"),
            intranet_entry=selected_mock_data.get("intranet_entry", "N/A"),
            internet_entry=selected_mock_data.get("internet_entry", "N/A"),
            web_tier=selected_mock_data.get("web_tier", "N/A"),
            app_tier=selected_mock_data.get("app_tier", "N/A"),
            db_tier=selected_mock_data.get("db_tier", "N/A")
        )
        
        # Store in session state to be picked up by the chat logic
        st.session_state.pending_mock = formatted_request

    st.divider()
    if st.button("🗑️ Reset Session"):
        st.session_state.clear()
        st.rerun()

# --- CHAT INTERFACE ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- USER INPUT LOGIC ---
# Enhanced placeholder to guide the user visually in the input box
placeholder_text = "Provide App Name, Tiers (vCPU/RAM), Users, and Dependencies..."
prompt = st.chat_input(placeholder_text)

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
            for event in st.session_state.runner.run(
                user_id=USER_ID,
                session_id=SESSION_ID,
                new_message=new_message
            ):
                if hasattr(event, 'content') and event.content:
                    if hasattr(event.content, 'parts') and event.content.parts:
                        for part in event.content.parts:
                            if hasattr(part, 'text') and part.text:
                                full_response += part.text
                                response_placeholder.markdown(full_response + "▌")
                            if hasattr(part, 'function_call') and part.function_call:
                                print(f"DEBUG Tool Call: {part.function_call.name}")
            
            response_placeholder.markdown(full_response)
            
        except Exception as e:
            st.error(f"Execution Error: {str(e)}")
        
    st.session_state.messages.append({"role": "assistant", "content": full_response})