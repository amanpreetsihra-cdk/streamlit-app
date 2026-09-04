import streamlit as st
import requests
import json
from typing import Any, Dict, List

st.set_page_config(page_title="API Call Tool", layout="wide")

st.title("🔌 API Call Tool")
st.markdown("Make HTTP POST requests to any endpoint and view the response")

# Sidebar configuration
with st.sidebar:
    st.header("Request Configuration")
    
    # Connection Type
    connection_type = st.selectbox(
        "Connection Type",
        ["Generic API", "Databricks (Optional)"]
    )
    
    if connection_type == "Databricks (Optional)":
        st.subheader("Databricks Configuration")
        st.info("💡 Use Databricks token-based API calls. Token is optional - leave empty for public endpoints.")
        
        databricks_host = st.text_input(
            "Databricks Host",
            placeholder="https://your-workspace.cloud.databricks.com",
            help="Your Databricks workspace URL"
        )
        databricks_token = st.text_input(
            "Personal Access Token",
            type="password",
            placeholder="dapi...",
            help="Your Databricks PAT (required for Unity Catalog access)"
        )
        
        # Databricks preset endpoints
        preset_endpoints = {
            "Run Query": "/api/2.0/sql/statements",
            "Create Job": "/api/2.0/jobs/create",
            "Get Warehouse Info": "/api/2.0/sql/warehouses",
            "Browse Unity Catalog": "unity_catalog",
            "Custom Endpoint": ""
        }
        
        endpoint_selection = st.selectbox(
            "Databricks Endpoint",
            list(preset_endpoints.keys())
        )
        
        selected_path = preset_endpoints[endpoint_selection]
        
        # Unity Catalog Browser
        if endpoint_selection == "Browse Unity Catalog":
            st.subheader("🗂️ Unity Catalog Browser")
            
            if not databricks_host or not databricks_token:
                st.error("❌ Please enter Databricks host and token to browse Unity Catalog")
                api_path = ""
                request_body = "{}"
                query_params = "{}"
            else:
                headers = {
                    "Authorization": f"Bearer {databricks_token}",
                    "Content-Type": "application/json",
                    "User-Agent": "Streamlit-API-Tool"
                }
                
                try:
                    # Fetch catalogs
                    catalogs_url = f"{databricks_host}/api/2.0/unity-catalog/catalogs"
                    catalogs_response = requests.get(catalogs_url, headers=headers, timeout=10)
                    catalogs_response.raise_for_status()
                    catalogs_data = catalogs_response.json()
                    catalogs = [cat.get("name", "") for cat in catalogs_data.get("catalogs", [])]
                    
                    if not catalogs:
                        st.warning("No catalogs found")
                        api_path = ""
                        request_body = "{}"
                        query_params = "{}"
                    else:
                        # Select catalog
                        selected_catalog = st.selectbox("Select Catalog", catalogs, key="catalog_select")
                        
                        # Fetch schemas for selected catalog
                        schemas_url = f"{databricks_host}/api/2.0/unity-catalog/schemas?catalog_name={selected_catalog}"
                        schemas_response = requests.get(schemas_url, headers=headers, timeout=10)
                        schemas_response.raise_for_status()
                        schemas_data = schemas_response.json()
                        schemas = [sch.get("name", "") for sch in schemas_data.get("schemas", [])]
                        
                        if not schemas:
                            st.warning(f"No schemas found in catalog '{selected_catalog}'")
                            api_path = ""
                            request_body = "{}"
                            query_params = "{}"
                        else:
                            # Select schema
                            selected_schema = st.selectbox("Select Schema", schemas, key="schema_select")
                            
                            # Fetch tables for selected schema
                            tables_url = f"{databricks_host}/api/2.0/unity-catalog/tables?catalog_name={selected_catalog}&schema_name={selected_schema}"
                            tables_response = requests.get(tables_url, headers=headers, timeout=10)
                            tables_response.raise_for_status()
                            tables_data = tables_response.json()
                            tables = [tbl.get("name", "") for tbl in tables_data.get("tables", [])]
                            
                            if not tables:
                                st.warning(f"No tables found in schema '{selected_schema}'")
                                api_path = ""
                                request_body = "{}"
                                query_params = "{}"
                            else:
                                # Select table
                                selected_table = st.selectbox("Select Table", tables, key="table_select")
                                
                                st.success(f"✅ Selected: {selected_catalog}.{selected_schema}.{selected_table}")
                                
                                # Set the request body with table info
                                api_path = "/api/2.0/unity-catalog/tables"
                                request_body = json.dumps({
                                    "full_name": f"{selected_catalog}.{selected_schema}.{selected_table}"
                                })
                                query_params = "{}"
                
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Error connecting to Databricks: {str(e)}")
                    api_path = ""
                    request_body = "{}"
                    query_params = "{}"
        
        elif endpoint_selection == "Custom Endpoint":
            api_path = st.text_input(
                "Custom API Path",
                placeholder="/api/2.0/jobs/list",
                help="Databricks API path (without host)"
            )
            
            request_body = st.text_area(
                "Request Body (JSON)",
                value='{}',
                height=150,
                help="Provide request body as JSON"
            )
            
            query_params = st.text_area(
                "Query Parameters (JSON)",
                value='{}',
                height=80,
                help="Optional query parameters as JSON"
            )
        
        else:  # Other preset endpoints
            api_path = selected_path
            st.caption(f"Path: {api_path}")
            
            request_body = st.text_area(
                "Request Body (JSON)",
                value='{}',
                height=150,
                help="Provide request body as JSON"
            )
            
            query_params = st.text_area(
                "Query Parameters (JSON)",
                value='{}',
                height=80,
                help="Optional query parameters as JSON"
            )
    
    else:  # Generic API
        # Endpoint URL
        endpoint = st.text_input(
            "Endpoint URL",
            placeholder="https://api.example.com/endpoint",
            help="Full URL of the API endpoint"
        )
        
        # Headers
        st.subheader("Headers")
        headers_json = st.text_area(
            "Headers (JSON)",
            value='{"Content-Type": "application/json"}',
            height=100,
            help="Provide headers as JSON object"
        )
        
        # Request Body for POST
        st.subheader("Request Body")
        request_body = st.text_area(
            "Body (JSON)",
            value='{}',
            height=150,
            help="Provide request body as JSON"
        )
        
        # Query Parameters
        st.subheader("Query Parameters")
        query_params = st.text_area(
            "Query Parameters (JSON)",
            value='{}',
            height=100,
            help="Provide query parameters as JSON object"
        )
    
    # Timeout
    timeout = st.number_input("Timeout (seconds)", min_value=1, max_value=300, value=10)

# Main content area
if st.button("🚀 Send POST Request", type="primary", use_container_width=True):
    try:
        if connection_type == "Databricks (Optional)":
            # Databricks connection
            if not databricks_host:
                st.error("❌ Please enter Databricks host")
            else:
                with st.spinner("Calling Databricks API..."):
                    # Build full URL
                    full_url = f"{databricks_host}{api_path}"
                    
                    # Build headers
                    headers = {
                        "Content-Type": "application/json",
                        "User-Agent": "Streamlit-API-Tool"
                    }
                    
                    # Add auth if token provided
                    if databricks_token:
                        headers["Authorization"] = f"Bearer {databricks_token}"
                    
                    # Parse query parameters
                    try:
                        params = json.loads(query_params) if query_params.strip() else {}
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid Query Parameters JSON: {e}")
                        params = {}
                    
                    # Parse request body
                    try:
                        body = json.loads(request_body) if request_body.strip() else None
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid Request Body JSON: {e}")
                        body = None
                    
                    # Make POST request
                    response = requests.post(full_url, headers=headers, params=params, json=body, timeout=timeout)
                    
                    st.session_state.response = response
                    st.session_state.response_time = response.elapsed.total_seconds()
                    st.session_state.connection_type = "Databricks"
                    st.session_state.request_details = {
                        "type": "Databricks",
                        "method": "POST",
                        "endpoint": api_path,
                        "host": databricks_host,
                        "has_token": bool(databricks_token)
                    }
        
        else:  # Generic API
            if not endpoint:
                st.error("❌ Please enter an endpoint URL")
            else:
                try:
                    # Parse headers
                    try:
                        headers = json.loads(headers_json) if headers_json.strip() else {}
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid Headers JSON: {e}")
                        headers = {}
                    
                    # Parse query parameters
                    try:
                        params = json.loads(query_params) if query_params.strip() else {}
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid Query Parameters JSON: {e}")
                        params = {}
                    
                    # Parse request body
                    try:
                        body = json.loads(request_body) if request_body.strip() else None
                    except json.JSONDecodeError as e:
                        st.error(f"Invalid Request Body JSON: {e}")
                        body = None
                    
                    # Make POST request
                    with st.spinner("Sending POST request..."):
                        response = requests.post(endpoint, headers=headers, params=params, json=body, timeout=timeout)
                    
                    st.session_state.response = response
                    st.session_state.response_time = response.elapsed.total_seconds()
                    st.session_state.connection_type = "Generic API"
                    st.session_state.request_details = {
                        "type": "Generic API",
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
    
    except requests.exceptions.Timeout:
        st.error("⏱️ Request timed out. Try increasing the timeout value.")
    except requests.exceptions.ConnectionError:
        st.error("🔌 Connection error. Check the host and your internet connection.")
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
            if entry["type"] == "Databricks":
                auth_status = "🔐" if entry.get("has_token") else "🔓"
                st.text(f"{idx+1}. {auth_status} Databricks POST {entry['endpoint']} - {entry['status_code']} ({entry['response_time']:.2f}s)")
            else:
                st.text(f"{idx+1}. POST {entry['endpoint']} - {entry['status_code']} ({entry['response_time']:.2f}s)")
    else:
        st.info("No requests made yet")
