import streamlit as st
import requests
import json
import os
import sys
from datetime import datetime

# Enhanced GRINGO integration
st.set_page_config(
    page_title="🤖 GRINGO AI Personal OS", 
    page_icon="🤖",
    layout="wide"
)

# Add the current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Check if GRINGO cockpit is available
try:
    from gringo_unified_cockpit import main as gringo_main, initialize_system
    GRINGO_AVAILABLE = True
except ImportError:
    GRINGO_AVAILABLE = False

# Sidebar for mode selection
st.sidebar.title("🤖 GRINGO Personal OS")
st.sidebar.markdown("**Choose your interface:**")

if GRINGO_AVAILABLE:
    interface_mode = st.sidebar.radio(
        "Interface:",
        ["💬 Simple Chat", "🚀 Full GRINGO Cockpit"]
    )
else:
    interface_mode = "💬 Simple Chat"
    st.sidebar.warning("🔧 GRINGO Cockpit not available - using simple chat mode")

# Route to appropriate interface
if interface_mode == "🚀 Full GRINGO Cockpit" and GRINGO_AVAILABLE:
    # Launch the full GRINGO interface
    st.title("🤖 GRINGO Personal OS")
    st.markdown("**Your 100% Local AI-Powered Personal Operating System**")
    
    # Initialize and run GRINGO
    initialize_system()
    
    # Import and run the cockpit components
    from gringo_unified_cockpit import (
        render_dashboard, render_terminal_tab, render_file_manager_tab, 
        render_ai_agents_tab, render_automation_tab, render_memory_tab
    )
    
    # Tab navigation
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🏠 Dashboard", "💻 Terminal", "📁 Files", "🤖 AI Agents", "📅 Automation", "🧠 Memory"
    ])
    
    with tab1:
        render_dashboard()
    with tab2:
        render_terminal_tab()
    with tab3:
        render_file_manager_tab()
    with tab4:
        render_ai_agents_tab()
    with tab5:
        render_automation_tab()
    with tab6:
        render_memory_tab()

else:
    # Original simple chat interface
    st.title("🦙 Chat with LLaMA")
    st.markdown("*Simple chat mode - upgrade to GRINGO Cockpit for full features*")
    
    if "history" not in st.session_state:
        st.session_state.history = []

    # Enhanced chat interface
    col1, col2 = st.columns([3, 1])
    
    with col1:
        prompt = st.text_area("Your message:", key="user_input", height=100)
    
    with col2:
        st.markdown("**Quick Actions:**")
        if st.button("📋 Summarize"):
            prompt = "Please provide a summary of our conversation so far."
        if st.button("🔍 Analyze"):
            prompt = "Please analyze the key points from our discussion."
        if st.button("💡 Suggest"):
            prompt = "What suggestions do you have based on our conversation?"

    if st.button("Send", type="primary"):
        if prompt:
            with st.spinner("🦙 LLaMA is thinking..."):
                try:
                    res = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "llama3", "prompt": prompt},
                        stream=True,
                        timeout=30
                    )

                    full_response = ""
                    response_container = st.empty()
                    
                    for line in res.iter_lines():
                        if line:
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            full_response += chunk
                            # Show streaming response
                            response_container.markdown(f"**🦙 LLaMA:** {full_response}")

                    # Log + display
                    st.session_state.history.append((prompt, full_response))

                    # Append to memory.json
                    try:
                        with open("memory.json", "r") as f:
                            logs = json.load(f)
                    except (FileNotFoundError, json.JSONDecodeError):
                        logs = []
                    
                    logs.append({
                        "timestamp": datetime.now().isoformat(),
                        "prompt": prompt,
                        "response": full_response
                    })
                    
                    with open("memory.json", "w") as f:
                        json.dump(logs, f, indent=2)
                    
                    st.success("✅ Response saved to memory!")
                    
                except requests.exceptions.RequestException as e:
                    st.error(f"❌ Connection error: {e}")
                    st.info("💡 Make sure Ollama is running: `ollama serve`")
                except Exception as e:
                    st.error(f"❌ Error: {e}")
        else:
            st.warning("Please enter a message!")

    # Display chat history
    if st.session_state.history:
        st.markdown("---")
        st.subheader("💬 Chat History")
        
        # Option to clear history
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
        
        # Display in reverse order (newest first)
        for i, (q, a) in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"💬 Conversation {len(st.session_state.history) - i + 1}"):
                st.markdown(f"**🧠 You:** {q}")
                st.markdown(f"**🦙 LLaMA:** {a}")

# Sidebar enhancements
st.sidebar.markdown("---")
st.sidebar.markdown("**🔧 System Status:**")

# Check Ollama connection
try:
    response = requests.get("http://localhost:11434/api/tags", timeout=2)
    if response.status_code == 200:
        st.sidebar.success("🟢 Ollama Connected")
        models = response.json().get("models", [])
        if models:
            st.sidebar.text(f"📚 Models: {len(models)}")
    else:
        st.sidebar.error("🔴 Ollama Error")
except:
    st.sidebar.error("🔴 Ollama Offline")
    st.sidebar.info("Start with: `ollama serve`")

# Memory stats
try:
    with open("memory.json", "r") as f:
        logs = json.load(f)
        st.sidebar.metric("🧠 Memories", len(logs))
except:
    st.sidebar.metric("🧠 Memories", 0)

# Quick setup
st.sidebar.markdown("---")
if st.sidebar.button("🚀 Upgrade to Full GRINGO"):
    st.sidebar.info("Run: `python launch_gringo.py`")

st.sidebar.markdown("**🔒 100% Local & Private**")
st.sidebar.markdown("*No data leaves your machine*")
