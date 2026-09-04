import streamlit as st
import requests
import json
import re
from typing import Any, Dict

st.set_page_config(page_title="API Call Tool", layout="wide")

st.title("🔌 API Call Tool")
st.markdown("Make HTTP POST requests to any endpoint and view the response")

def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by:
    1. Replacing 'None' with 'null'
    2. Removing trailing commas
    """
    # Replace Python's None with JSON's null
    json_str = re.sub(r'\bNone\b', 'null', json_str)
    
    # Remove trailing commas before closing brackets/braces
    json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
    
    return json_str

# Sidebar configuration
with st.sidebar:
    st.header("Connection Settings")
    
    # Endpoint URL
    endpoint = st.text_input(
        "Endpoint URL",
        placeholder="https://api.example.com/endpoint",
        help="Full URL of the API endpoint"
    )
    
    # Headers section
    st.subheader("Headers")
    headers_json = st.text_area(
        "Headers (JSON)",
        value='{"Content-Type": "application/json"}',
        height=100,
        help="Provide headers as JSON object"
    )
    
    # Token/API Key
    st.subheader("Authentication")
    token = st.text_input(
        "Token/API Key (Optional)",
        type="password",
        placeholder="your-token-here",
        help="Bearer token or API key if needed"
    )
    
    if token:
        st.caption("✅ Token will be added to Authorization header")
    
    # Timeout
    timeout = st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=10)

# Main content area
col1, col2 = st.columns([1, 1])

# Left column - Request configuration
with col1:
    st.subheader("📝 Request Body")
    request_body = st.text_area(
        "Body (JSON)",
        value='{}',
        height=250,
        help="Provide request body as JSON (supports trailing commas and None values)"
    )

# Right column - Query Parameters
with col2:
    st.subheader("🔍 Query Parameters")
    query_params = st.text_area(
        "Query Parameters (JSON)",
        value='{}',
        height=250,
        help="Provide query parameters as JSON object (supports trailing commas and None values)"
    )

# Send button
st.divider()
if st.button("🚀 Send POST Request", type="primary", use_container_width=True):
    if not endpoint:
        st.error("❌ Please enter an endpoint URL")
    else:
        try:
            # Parse headers
            try:
                headers_cleaned = clean_json_string(headers_json)
                headers = json.loads(headers_cleaned) if headers_cleaned.strip() else {}
            except json.JSONDecodeError as e:
                st.error(f"Invalid Headers JSON: {e}")
                headers = {}
            
            # Add token to headers if provided
            if token:
                headers["Authorization"] = f"Bearer {token}"
            
            # Parse query parameters
            try:
                params_cleaned = clean_json_string(query_params)
                params = json.loads(params_cleaned) if params_cleaned.strip() else {}
            except json.JSONDecodeError as e:
                st.error(f"Invalid Query Parameters JSON: {e}")
                params = {}
            
            # Parse request body
            try:
                body_cleaned = clean_json_string(request_body)
                body = json.loads(body_cleaned) if body_cleaned.strip() else None
            except json.JSONDecodeError as e:
                st.error(f"Invalid Request Body JSON: {e}")
                body = None
            
            # Make POST request
            with st.spinner("Sending POST request..."):
                response = requests.post(endpoint, headers=headers, params=params, json=body, timeout=timeout)
            
            st.session_state.response = response
            st.session_state.response_time = response.elapsed.total_seconds()
            st.session_state.request_details = {
                "method": "POST",
                "endpoint": endpoint
            }
        
        except requests.exceptions.Timeout:
            st.error("⏱️ Request timed out. Try increasing the timeout value.")
        except requests.exceptions.ConnectionError:
            st.error("🔌 Connection error. Check the endpoint URL and your internet connection.")
        except requests.exceptions.RequestException as e:
            st.error(f"❌ Request failed: {str(e)}")
        except Exception as e:
            st.error(f"❌ Error: {str(e)}")

# Display response
if "response" in st.session_state:
    response = st.session_state.response
    response_time = st.session_state.response_time
    
    st.divider()
    st.subheader("📤 Response")
    
    # Response metadata
    col1, col2, col3 = st.columns(3)
    with col1:
        status_color = "🟢" if response.status_code < 400 else "🔴"
        st.metric("Status Code", f"{status_color} {response.status_code}")
    with col2:
        st.metric("Response Time", f"{response_time:.2f}s")
    with col3:
        st.metric("Content Length", f"{len(response.content)} bytes")
    
    # Response headers
    with st.expander("📋 Response Headers"):
        header_dict = dict(response.headers)
        st.json(header_dict)
    
    # Response body
    st.subheader("Response Body")
    
    try:
        # Try to parse as JSON
        response_json = response.json()
        st.json(response_json)
        
        # Option to download as JSON
        st.download_button(
            label="📥 Download JSON",
            data=json.dumps(response_json, indent=2),
            file_name="response.json",
            mime="application/json"
        )
    except:
        # Display as text if not JSON
        st.text(response.text if response.text else "(Empty response)")
        
        st.download_button(
            label="📥 Download Response",
            data=response.text,
            file_name="response.txt",
            mime="text/plain"
        )

# History section
st.divider()
with st.expander("📜 Request History"):
    if "history" not in st.session_state:
        st.session_state.history = []
    
    if "response" in st.session_state and "request_details" in st.session_state:
        details = st.session_state.request_details
        history_entry = {
            **details,
            "status_code": st.session_state.response.status_code,
            "response_time": response_time
        }
        
        if history_entry not in st.session_state.history:
            st.session_state.history.insert(0, history_entry)
    
    if st.session_state.history:
        for idx, entry in enumerate(st.session_state.history[:10]):  # Show last 10
            st.text(f"{idx+1}. POST {entry['endpoint']} - {entry['status_code']} ({entry['response_time']:.2f}s)")
    else:
        st.info("No requests made yet")
