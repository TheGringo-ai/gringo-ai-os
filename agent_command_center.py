#!/usr/bin/env python3
"""
🔥 Gringo's AI Agent Command Center 🔥
Multi-Agent Orchestration with Ollama Integration
"""

import streamlit as st
import json
import subprocess
import time
from datetime import datetime
import multi_agent_orchestrator
import fredfix_agent

# Page config
st.set_page_config(
    page_title="🔥 Gringo's Agent Command Center",
    page_icon="🤖",
    layout="wide"
)

st.title("🔥 Gringo's AI Agent Command Center")
st.markdown("*Multi-Agent Orchestration • Parallel Execution • AI-Powered Planning*")

# Initialize session state
if "orchestrator" not in st.session_state:
    st.session_state.orchestrator = multi_agent_orchestrator.MultiAgentOrchestrator()
    
    # Register all agents
    st.session_state.orchestrator.register_agent("planner", "agents/planner_agent.py", "Task planning and breakdown")
    st.session_state.orchestrator.register_agent("refactor", "agents/refactor_agent.py", "Code refactoring and optimization")
    st.session_state.orchestrator.register_agent("test_gen", "agents/test_generator_agent.py", "Automated test generation")
    st.session_state.orchestrator.register_agent("doc_gen", "agents/doc_generator_agent.py", "Documentation generation")
    st.session_state.orchestrator.register_agent("reviewer", "agents/review_agent.py", "Code review and quality check")

if "execution_history" not in st.session_state:
    st.session_state.execution_history = []

# Sidebar - Agent Status
with st.sidebar:
    st.header("🤖 Agent Status")
    
    agents = st.session_state.orchestrator.agents
    for name, info in agents.items():
        status = "🟢 Active" if info["active"] else "🔴 Inactive"
        st.write(f"**{name.title()}** {status}")
        st.caption(info["description"])
    
    st.divider()
    
    # Quick Actions
    st.header("⚡ Quick Actions")
    
    if st.button("🚀 Full Validation", use_container_width=True):
        with st.spinner("Running full validation..."):
            success = fredfix_agent.run_full_validation()
            if success:
                st.success("✅ All systems operational!")
            else:
                st.error("❌ Issues detected - check logs")
    
    if st.button("🧪 Run All Tests", use_container_width=True):
        with st.spinner("Running parallel tests..."):
            success = fredfix_agent.run_parallel_tests()
            if success:
                st.success("✅ All tests passed!")
            else:
                st.error("❌ Some tests failed")

# Main interface tabs
tab1, tab2, tab3, tab4 = st.tabs(["🎯 Mission Control", "🔧 Individual Agents", "📊 Analytics", "⚙️ Settings"])

with tab1:
    st.header("🎯 Mission Control")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("🚀 Feature Request Pipeline")
        
        feature_request = st.text_area(
            "Describe the feature you want to implement:",
            placeholder="e.g., Add user authentication API endpoint with JWT tokens",
            height=100
        )
        
        execution_mode = st.selectbox(
            "Execution Mode:",
            ["🎼 Full Pipeline (Plan → Code → Test → Doc → Review)", 
             "⚡ Parallel Agents Only", 
             "🧠 Planning Only"]
        )
        
        if st.button("🚀 Execute Mission", type="primary", use_container_width=True):
            if feature_request:
                with st.spinner("Orchestrating agents..."):
                    start_time = time.time()
                    
                    if "Full Pipeline" in execution_mode:
                        success = st.session_state.orchestrator.run_feature_pipeline(feature_request)
                    elif "Parallel Agents" in execution_mode:
                        tasks = [
                            {"agent": "refactor", "data": {"target": "code_quality", "workspace": "."}},
                            {"agent": "test_gen", "data": {"coverage_target": 80, "workspace": "."}},
                            {"agent": "doc_gen", "data": {"format": "markdown", "workspace": "."}}
                        ]
                        results = st.session_state.orchestrator.orchestrate_parallel(tasks)
                        success = all(r.success for r in results)
                    else:  # Planning only
                        result = subprocess.run([
                            "python3", "agents/planner_agent.py", 
                            json.dumps({"request": feature_request, "workspace": "."})
                        ], capture_output=True, text=True)
                        success = result.returncode == 0
                    
                    execution_time = time.time() - start_time
                    
                    # Log execution
                    st.session_state.execution_history.append({
                        "timestamp": datetime.now().isoformat(),
                        "request": feature_request,
                        "mode": execution_mode,
                        "success": success,
                        "duration": execution_time
                    })
                    
                if success:
                    st.success(f"✅ Mission completed in {execution_time:.1f}s!")
                else:
                    st.error("❌ Mission encountered issues")
            else:
                st.warning("Please enter a feature request")
    
    with col2:
        st.subheader("📈 Live Status")
        
        summary = st.session_state.orchestrator.get_summary()
        
        if summary["total_agents"] > 0:
            st.metric("Success Rate", f"{summary['success_rate']:.1f}%")
            st.metric("Agents Run", summary["total_agents"])
            st.metric("Successful", summary["successful"])
        else:
            st.info("No agents executed yet")
        
        st.subheader("🕒 Recent Executions")
        
        for execution in st.session_state.execution_history[-3:]:
            status = "✅" if execution["success"] else "❌"
            st.write(f"{status} {execution['request'][:30]}...")
            st.caption(f"{execution['duration']:.1f}s ago")

with tab2:
    st.header("🔧 Individual Agent Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🧠 Planning Agent")
        plan_request = st.text_input("Feature to plan:")
        if st.button("📋 Generate Plan", key="plan"):
            if plan_request:
                with st.spinner("Planning..."):
                    result = subprocess.run([
                        "python3", "agents/planner_agent.py",
                        json.dumps({"request": plan_request, "workspace": "."})
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        st.success("✅ Plan generated!")
                        try:
                            plan_data = json.loads(result.stdout.split('\n', 1)[1])
                            st.json(plan_data)
                        except:
                            st.code(result.stdout)
                    else:
                        st.error("❌ Planning failed")
                        st.code(result.stderr)
        
        st.subheader("⚙️ Refactor Agent")
        if st.button("🔧 Analyze Code Quality", key="refactor"):
            with st.spinner("Analyzing..."):
                result = subprocess.run([
                    "python3", "agents/refactor_agent.py",
                    json.dumps({"target": "quality", "workspace": "."})
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    st.success("✅ Analysis complete!")
                    st.code(result.stdout)
                else:
                    st.error("❌ Analysis failed")
    
    with col2:
        st.subheader("🧪 Test Generator")
        coverage_target = st.slider("Coverage Target %", 0, 100, 80)
        if st.button("🧪 Generate Tests", key="test_gen"):
            with st.spinner("Generating tests..."):
                result = subprocess.run([
                    "python3", "agents/test_generator_agent.py",
                    json.dumps({"coverage_target": coverage_target, "workspace": "."})
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    st.success("✅ Tests generated!")
                    st.code(result.stdout)
                else:
                    st.error("❌ Test generation failed")
        
        st.subheader("📚 Documentation Generator")
        doc_format = st.selectbox("Format:", ["markdown", "html", "rst"])
        if st.button("📝 Generate Docs", key="doc_gen"):
            with st.spinner("Generating documentation..."):
                result = subprocess.run([
                    "python3", "agents/doc_generator_agent.py",
                    json.dumps({"format": doc_format, "workspace": "."})
                ], capture_output=True, text=True)
                
                if result.returncode == 0:
                    st.success("✅ Documentation generated!")
                    st.code(result.stdout)
                else:
                    st.error("❌ Documentation generation failed")

with tab3:
    st.header("📊 Analytics Dashboard")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Execution Statistics")
        
        if st.session_state.execution_history:
            total_executions = len(st.session_state.execution_history)
            successful_executions = sum(1 for e in st.session_state.execution_history if e["success"])
            avg_duration = sum(e["duration"] for e in st.session_state.execution_history) / total_executions
            
            st.metric("Total Missions", total_executions)
            st.metric("Success Rate", f"{successful_executions/total_executions*100:.1f}%")
            st.metric("Avg Duration", f"{avg_duration:.1f}s")
        else:
            st.info("No execution data yet")
    
    with col2:
        st.subheader("🤖 Agent Performance")
        
        agent_summary = st.session_state.orchestrator.get_summary()
        if agent_summary["results"]:
            st.json(agent_summary)
        else:
            st.info("No agent data yet")

with tab4:
    st.header("⚙️ System Settings")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🔧 Agent Configuration")
        st.write("Registered Agents:")
        for name, info in st.session_state.orchestrator.agents.items():
            st.write(f"• **{name}**: {info['description']}")
        
        if st.button("🔄 Refresh Agent Status"):
            st.rerun()
    
    with col2:
        st.subheader("📁 Workspace Info")
        st.write("Current workspace: `./`")
        
        # Show recent file changes
        try:
            result = subprocess.run(["ls", "-la"], capture_output=True, text=True)
            st.code(result.stdout)
        except:
            st.write("Could not list files")

# Footer
st.divider()
st.markdown("🔥 **Gringo's AI Agent Command Center** - Powered by Multi-Agent Orchestration")
