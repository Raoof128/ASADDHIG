"""
Streamlit Dashboard for Sovereign AI Gateway visualization.
"""
import streamlit as st
import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, List

# Configuration
GATEWAY_URL = os.getenv("GATEWAY_URL", "http://gateway_api:8000")
AUDIT_API_URL = f"{GATEWAY_URL}/audit/recent"

# Page configuration
st.set_page_config(
    page_title="Sovereign AI Gateway Dashboard",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .route-indicator {
        font-size: 1.5rem;
        font-weight: bold;
        padding: 1rem;
        border-radius: 0.5rem;
        text-align: center;
    }
    .route-cloud {
        background-color: #d4edda;
        color: #155724;
    }
    .route-sovereign {
        background-color: #f8d7da;
        color: #721c24;
    }
    .pii-score-high {
        color: #dc3545;
        font-weight: bold;
    }
    .pii-score-medium {
        color: #ffc107;
        font-weight: bold;
    }
    .pii-score-low {
        color: #28a745;
        font-weight: bold;
    }
    </style>
""", unsafe_allow_html=True)


def call_gateway(prompt: str, user_id: str = None, session_id: str = None) -> Dict:
    """Call the gateway API."""
    try:
        payload = {
            "prompt": prompt,
            "user_id": user_id,
            "session_id": session_id
        }
        
        response = requests.post(
            f"{GATEWAY_URL}/gateway",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            return {"error": f"API Error: {response.status_code} - {response.text}"}
    except requests.exceptions.ConnectionError:
        return {"error": "Cannot connect to Gateway API. Ensure the gateway is running."}
    except Exception as e:
        return {"error": f"Request failed: {str(e)}"}


def get_audit_logs(limit: int = 50) -> List[Dict]:
    """Fetch recent audit logs."""
    try:
        response = requests.get(AUDIT_API_URL, params={"limit": limit}, timeout=5)
        if response.status_code == 200:
            return response.json().get("logs", [])
        return []
    except:
        return []


def get_pii_score_color(score: float) -> str:
    """Get color class based on PII score."""
    if score >= 0.7:
        return "pii-score-high"
    elif score >= 0.3:
        return "pii-score-medium"
    else:
        return "pii-score-low"


def get_route_indicator_class(route: str) -> str:
    """Get CSS class for route indicator."""
    return "route-cloud" if route == "cloud" else "route-sovereign"


def main():
    """Main dashboard application."""
    
    # Header
    st.markdown('<div class="main-header">🛡️ Sovereign AI Gateway Dashboard</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")
        st.info("**Australian Data Sovereignty Enforcement**\n\nRoutes sensitive prompts to local LLMs, general prompts to cloud AI.")
        
        st.subheader("Gateway Status")
        try:
            health_response = requests.get(f"{GATEWAY_URL}/health", timeout=2)
            if health_response.status_code == 200:
                st.success("✅ Gateway Operational")
            else:
                st.error("❌ Gateway Unhealthy")
        except:
            st.error("❌ Gateway Unreachable")
        
        st.subheader("Settings")
        auto_refresh = st.checkbox("Auto-refresh logs", value=False)
        refresh_interval = st.slider("Refresh interval (seconds)", 5, 60, 10)
        
        if auto_refresh:
            time.sleep(refresh_interval)
            st.rerun()
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("📝 Prompt Input")
        
        # User input
        prompt = st.text_area(
            "Enter your prompt:",
            height=200,
            placeholder="Type your prompt here...\n\nExample:\n'What is the capital of Australia?'\n\nOr sensitive:\n'My Medicare number is 1234 567 890'"
        )
        
        col_submit1, col_submit2 = st.columns([1, 1])
        with col_submit1:
            submit_button = st.button("🚀 Send to Gateway", type="primary", use_container_width=True)
        with col_submit2:
            clear_button = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_button:
            st.rerun()
        
        # Process request
        if submit_button and prompt:
            with st.spinner("Processing through gateway..."):
                result = call_gateway(prompt)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                else:
                    # Store result in session state for display
                    st.session_state.last_result = result
                    st.rerun()
        
        # Display last result
        if "last_result" in st.session_state and "error" not in st.session_state.last_result:
            result = st.session_state.last_result
            
            st.markdown("---")
            st.subheader("📊 Gateway Decision")
            
            # Route indicator
            route = result.get("route", "unknown")
            route_class = get_route_indicator_class(route)
            route_emoji = "☁️" if route == "cloud" else "🏠"
            route_text = "Cloud AI (OpenAI)" if route == "cloud" else "Sovereign LLM (Local)"
            
            st.markdown(
                f'<div class="route-indicator {route_class}">{route_emoji} {route_text}</div>',
                unsafe_allow_html=True
            )
            
            # PII Score
            pii_score = result.get("pii_score", 0.0)
            score_class = get_pii_score_color(pii_score)
            st.markdown(f"**PII Sensitivity Score:** <span class='{score_class}'>{pii_score:.2%}</span>", unsafe_allow_html=True)
            
            # PII Detections
            pii_detected = result.get("pii_detected", [])
            if pii_detected:
                st.markdown("**Detected PII:**")
                for pii in pii_detected:
                    st.write(f"- **{pii['type'].replace('_', ' ').title()}**: {pii['value']} (confidence: {pii['confidence']:.0%})")
            else:
                st.info("✅ No PII detected")
            
            # Model used
            model_used = result.get("model_used", "unknown")
            st.markdown(f"**Model Used:** `{model_used}`")
            
            # Processing time
            processing_time = result.get("processing_time_ms", 0)
            st.markdown(f"**Processing Time:** {processing_time:.1f} ms")
            
            st.markdown("---")
            st.subheader("🤖 AI Response")
            st.write(result.get("response", "No response"))
    
    with col2:
        st.header("📈 Audit Logs")
        
        # Fetch and display audit logs
        logs = get_audit_logs(limit=20)
        
        if logs:
            st.metric("Total Log Entries", len(logs))
            
            # Summary statistics
            cloud_count = sum(1 for log in logs if log.get("route") == "cloud")
            sovereign_count = sum(1 for log in logs if log.get("route") == "sovereign")
            
            col_stat1, col_stat2 = st.columns(2)
            with col_stat1:
                st.metric("☁️ Cloud Routes", cloud_count)
            with col_stat2:
                st.metric("🏠 Sovereign Routes", sovereign_count)
            
            # Recent logs table
            st.subheader("Recent Activity")
            
            # Prepare log data for display
            log_data = []
            for log in logs[:10]:  # Show last 10
                timestamp = log.get("timestamp", "")
                if timestamp:
                    try:
                        dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                        timestamp = dt.strftime("%Y-%m-%d %H:%M:%S")
                    except:
                        pass
                
                log_data.append({
                    "Time": timestamp,
                    "Route": log.get("route", "unknown").upper(),
                    "PII Score": f"{log.get('pii_score', 0):.2f}",
                    "Model": log.get("model_used", "unknown"),
                    "PII Types": ", ".join(log.get("pii_types", []))[:30] or "None"
                })
            
            if log_data:
                st.dataframe(log_data, use_container_width=True, hide_index=True)
            
            # Detailed log viewer
            with st.expander("🔍 View Raw Logs"):
                st.json(logs[:5])  # Show first 5 as JSON
        
        else:
            st.info("No audit logs available. Send a request to generate logs.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🛡️ Sovereign AI Gateway - Australian Data Sovereignty Enforcement | "
        "Built for Defence, Finance, Healthcare & Government"
        "</div>",
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()

