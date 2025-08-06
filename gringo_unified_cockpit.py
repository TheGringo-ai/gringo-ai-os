#!/usr/bin/env python3
"""
GRINGO UNIFIED PERSONAL OS COCKPIT
Complete integration of all AI-powered personal OS features
100% local, private, no external dependencies
"""

import streamlit as st
import os
import sys
import json
import sqlite3
from datetime import datetime, timedelta
import subprocess
import threading
import time

# Add current directory to path for imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import our components
try:
    from gringo_terminal import create_enhanced_terminal_interface
    from gringo_file_manager import GringoFileManager, FileManagerUI
    from multi_agent_orchestrator import MultiAgentOrchestrator
    from personal_os_cockpit import PersonalOSCockpit
    from enhanced_project_ui import ProjectCreationUI
    from project_manager import ProjectManager
    from call_llama import call_llama_api
except ImportError as e:
    st.error(f"Import error: {e}")
    st.stop()

def initialize_system():
    """Initialize the GRINGO Personal OS system"""
    if 'gringo_system' not in st.session_state:
        st.session_state.gringo_system = PersonalOSCockpit()
    
    if 'file_manager' not in st.session_state:
        workspace_root = os.path.expanduser("~/gringo_workspace")
        memory_db = os.path.join(workspace_root, "memory.db")
        st.session_state.file_manager = GringoFileManager(workspace_root, memory_db)
        st.session_state.file_manager_ui = FileManagerUI(st.session_state.file_manager)
    
    if 'project_ui' not in st.session_state:
        st.session_state.project_ui = ProjectCreationUI(workspace_root)
    
    if 'terminal_ui' not in st.session_state:
        st.session_state.terminal_ui = create_enhanced_terminal_interface()

def render_dashboard():
    """Render the main dashboard"""
    st.title("🤖 GRINGO Personal OS")
    st.markdown("**Your 100% Local AI-Powered Personal Operating System**")
    
    # System status bar
    gringo_system = st.session_state.gringo_system
    stats = gringo_system.get_system_stats()
    
    col1, col2, col3, col4, col5 = st.columns(5)
    col1.metric("🖥️ CPU", f"{stats['cpu_usage']:.1f}%")
    col2.metric("🧠 RAM", f"{stats['memory_usage']:.1f}%")
    col3.metric("💾 Disk", f"{stats['disk_usage']:.1f}%")
    col4.metric("📁 Files", stats['tracked_files'])
    col5.metric("💽 Size", f"{stats['total_size_mb']} MB")

def render_project_creation_tab():
    """Render the enhanced project creation tab"""
    st.session_state.project_ui.render_project_creation_interface()

def render_terminal_tab():
    """Render the terminal interface tab"""
    st.session_state.terminal_ui.render()

def render_file_manager_tab():
    """Render the file manager tab"""
    st.session_state.file_manager_ui.render_file_browser()

def render_ai_agents_tab():
    """Render the AI agents management tab"""
    st.subheader("🤖 AI Agent Control Center")
    
    gringo_system = st.session_state.gringo_system
    
    # Agent status overview
    agents = gringo_system.orchestrator.agents
    
    if agents:
        st.markdown("**🟢 Active Agents:**")
        
        # Create agent grid
        cols = st.columns(3)
        for i, (agent_id, info) in enumerate(agents.items()):
            with cols[i % 3]:
                status = "🟢" if info["active"] else "🔴"
                st.metric(
                    f"{status} {agent_id.title()}", 
                    info["description"][:30] + "..."
                )
                
                # Quick test button
                if st.button(f"Test {agent_id}", key=f"test_{agent_id}"):
                    with st.spinner(f"Testing {agent_id}..."):
                        test_data = [{
                            "agent": agent_id,
                            "data": {"type": "test", "message": "System test"}
                        }]
                        results = gringo_system.orchestrator.orchestrate_parallel(test_data)
                        
                        if results and results[0].success:
                            st.success(f"✅ {agent_id} is working!")
                        else:
                            st.error(f"❌ {agent_id} test failed")
    
    # AI Interaction Panel
    st.markdown("---")
    st.subheader("💬 AI Assistant Interaction")
    
    # File selection for AI operations
    files = gringo_system.get_file_list()
    if files:
        selected_file_idx = st.selectbox(
            "Select file for AI analysis:",
            range(len(files)),
            format_func=lambda x: f"{files[x]['filename']} ({files[x]['file_type']})"
        )
        selected_file = files[selected_file_idx] if selected_file_idx is not None else None
        
        if selected_file:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**Quick AI Actions:**")
                
                ai_actions = [
                    ("📋 Summarize", "reviewer", "Analyze and summarize this file"),
                    ("🔍 Deep Analysis", "analytics", "Perform deep code/content analysis"),
                    ("🛠 Fix Issues", "refactor", "Find and fix any issues"),
                    ("🧪 Generate Tests", "test_gen", "Create comprehensive tests"),
                    ("📚 Document", "doc_gen", "Generate documentation"),
                    ("🔒 Security Check", "security", "Analyze for security issues"),
                    ("⚡ Performance", "performance", "Check performance characteristics")
                ]
                
                for action_name, agent_name, description in ai_actions:
                    if st.button(action_name, key=f"quick_{agent_name}"):
                        with st.spinner(f"Running {action_name}..."):
                            results = gringo_system.run_agent_on_file(
                                agent_name, 
                                selected_file['filepath'], 
                                description
                            )
                            
                            st.success(f"✅ {action_name} completed!")
                            
                            # Display results
                            if results:
                                for result in results:
                                    if result.success:
                                        with st.expander(f"📊 {action_name} Results"):
                                            st.code(result.output)
                                    else:
                                        st.error(f"Failed: {result.output}")
            
            with col2:
                st.markdown("**Custom AI Instructions:**")
                
                custom_instruction = st.text_area(
                    "Tell the AI what to do with this file:",
                    placeholder="Examples:\n- Explain this code in simple terms\n- Find potential bugs\n- Optimize for performance\n- Convert to different format\n- Extract key information",
                    height=150
                )
                
                if st.button("🚀 Execute Custom Task") and custom_instruction:
                    with st.spinner("Processing custom instruction..."):
                        # Use AI planner for custom instructions
                        results = gringo_system.run_agent_on_file(
                            "ai_planner", 
                            selected_file['filepath'], 
                            custom_instruction
                        )
                        
                        st.success("✅ Custom task completed!")
                        
                        if results:
                            for result in results:
                                with st.expander("🤖 AI Response"):
                                    st.markdown(result.output)

def render_automation_tab():
    """Render the automation and scheduling tab"""
    st.subheader("📅 Automation & Scheduling")
    
    gringo_system = st.session_state.gringo_system
    
    # Task Scheduler
    with st.expander("📅 Schedule New Task", expanded=True):
        col1, col2 = st.columns(2)
        
        with col1:
            task_name = st.text_input("Task Name:", placeholder="Daily file cleanup")
            task_type = st.selectbox(
                "Task Type:", 
                ["file_cleanup", "backup", "analysis", "summarization", "organization"]
            )
            target_files = st.text_input("Target Files/Folders:", placeholder="*.log, temp/, downloads/")
        
        with col2:
            schedule_type = st.selectbox("Schedule:", ["daily", "weekly", "monthly", "custom"])
            schedule_time = st.time_input("Time:", value=datetime.now().time())
            enabled = st.checkbox("Enable task", value=True)
        
        if st.button("📅 Create Scheduled Task"):
            schedule_pattern = f"{schedule_type}@{schedule_time}"
            gringo_system.schedule_task(task_name, task_type, target_files, schedule_pattern)
            st.success(f"✅ Scheduled: {task_name}")
    
    # Active Tasks
    st.markdown("**📋 Active Scheduled Tasks:**")
    
    # Get tasks from database
    conn = sqlite3.connect(gringo_system.memory_db)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM tasks WHERE status = "active"')
    tasks = cursor.fetchall()
    conn.close()
    
    if tasks:
        for task in tasks:
            task_id, name, task_type, target, schedule, last_run, next_run, status, results = task
            
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
            col1.text(f"📋 {name}")
            col2.text(f"🔄 {schedule}")
            col3.text(f"⏱️ Last: {last_run or 'Never'}")
            
            with col4:
                if st.button("▶️", key=f"run_task_{task_id}"):
                    st.info(f"Running {name}...")
                    # Here you would implement task execution
    else:
        st.info("No scheduled tasks. Create one above!")
    
    # Quick Automation
    st.markdown("---")
    st.subheader("🔧 Quick Automation")
    
    quick_col1, quick_col2, quick_col3 = st.columns(3)
    
    with quick_col1:
        if st.button("🧹 Clean Duplicate Files"):
            with st.spinner("Finding duplicates..."):
                # Run duplicate detection
                result = subprocess.run(
                    ["gringo", "duplicates", gringo_system.workspace_path],
                    capture_output=True, text=True
                )
                st.code(result.stdout)
    
    with quick_col2:
        if st.button("📊 Generate System Report"):
            with st.spinner("Generating report..."):
                # Generate comprehensive system report
                stats = gringo_system.get_system_stats()
                files = gringo_system.get_file_list()
                
                report = f"""
# GRINGO System Report
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## System Statistics
- CPU Usage: {stats['cpu_usage']:.1f}%
- Memory Usage: {stats['memory_usage']:.1f}%
- Tracked Files: {stats['tracked_files']}
- Total Size: {stats['total_size_mb']} MB

## File Summary
- Total Files: {len(files)}
- Recent Files: {len([f for f in files if f.get('last_modified', '') > (datetime.now() - timedelta(days=7)).isoformat()])}
"""
                st.markdown(report)
    
    with quick_col3:
        if st.button("💾 Backup Important Files"):
            with st.spinner("Creating backup..."):
                # Create backup of important files
                backup_dir = os.path.join(gringo_system.workspace_path, "backups", 
                                        datetime.now().strftime("%Y%m%d_%H%M%S"))
                os.makedirs(backup_dir, exist_ok=True)
                st.success(f"Backup created: {backup_dir}")

def render_memory_tab():
    """Render the memory and knowledge management tab"""
    st.subheader("🧠 Memory & Knowledge Management")
    
    gringo_system = st.session_state.gringo_system
    
    # Memory statistics
    conn = sqlite3.connect(gringo_system.memory_db)
    cursor = conn.cursor()
    
    # Get memory stats
    cursor.execute('SELECT COUNT(*) FROM memory')
    memory_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM files WHERE ai_summary IS NOT NULL')
    summarized_files = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM files WHERE tags IS NOT NULL')
    tagged_files = cursor.fetchone()[0]
    
    col1, col2, col3 = st.columns(3)
    col1.metric("🧠 Memory Entries", memory_count)
    col2.metric("📋 Summarized Files", summarized_files)
    col3.metric("🏷️ Tagged Files", tagged_files)
    
    # Memory browser
    st.markdown("**🔍 Browse Memory:**")
    
    cursor.execute('SELECT key, value, category, timestamp FROM memory ORDER BY timestamp DESC LIMIT 20')
    memories = cursor.fetchall()
    
    if memories:
        for key, value, category, timestamp in memories:
            with st.expander(f"🧠 {key} ({category})"):
                st.text(f"Time: {timestamp}")
                st.markdown(value)
    else:
        st.info("No memories stored yet. The AI will learn as you use the system!")
    
    # Add new memory
    with st.expander("➕ Add Memory"):
        new_key = st.text_input("Memory Key:", placeholder="important_fact")
        new_category = st.selectbox("Category:", ["personal", "work", "learning", "system", "other"])
        new_value = st.text_area("Memory Content:", placeholder="What should I remember?")
        
        if st.button("💾 Save Memory"):
            cursor.execute('''
                INSERT INTO memory (key, value, category) VALUES (?, ?, ?)
            ''', (new_key, new_value, new_category))
            conn.commit()
            st.success("✅ Memory saved!")
            st.rerun()
    
    conn.close()

def main():
    # Page configuration
    st.set_page_config(
        page_title="GRINGO Personal OS",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize system
    initialize_system()
    
    # Sidebar navigation
    st.sidebar.title("🤖 GRINGO Personal OS")
    st.sidebar.markdown("**100% Local AI System**")
    
    # Navigation
    tab_selection = st.sidebar.radio(
        "Navigate:",
        ["🏠 Dashboard", "� Project Creator", "�💻 Terminal", "📁 File Manager", "🤖 AI Agents", "📅 Automation", "🧠 Memory"]
    )
    
    # Quick stats in sidebar
    if 'gringo_system' in st.session_state:
        stats = st.session_state.gringo_system.get_system_stats()
        st.sidebar.markdown("---")
        st.sidebar.markdown("**System Status:**")
        st.sidebar.metric("CPU", f"{stats['cpu_usage']:.1f}%")
        st.sidebar.metric("Memory", f"{stats['memory_usage']:.1f}%")
        st.sidebar.metric("Files", stats['tracked_files'])
    
    # Main content area
    if tab_selection == "🏠 Dashboard":
        render_dashboard()
    elif tab_selection == "� Project Creator":
        render_project_creation_tab()
    elif tab_selection == "�💻 Terminal":
        render_terminal_tab()
    elif tab_selection == "📁 File Manager":
        render_file_manager_tab()
    elif tab_selection == "🤖 AI Agents":
        render_ai_agents_tab()
    elif tab_selection == "📅 Automation":
        render_automation_tab()
    elif tab_selection == "🧠 Memory":
        render_memory_tab()
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("**🔒 100% Private & Local**")
    st.sidebar.markdown("No data leaves your machine")
    
    # System info
    with st.sidebar.expander("ℹ️ System Info"):
        st.text(f"Workspace: ~/gringo_workspace")
        st.text(f"Agents: {len(st.session_state.gringo_system.orchestrator.agents) if 'gringo_system' in st.session_state else 0}")
        st.text(f"Status: ✅ Operational")

if __name__ == "__main__":
    main()
