#!/usr/bin/env python3
"""
GRINGO PERSONAL OS COCKPIT
Complete AI-powered personal operating system interface
100% local, no external API calls, full privacy
"""

import streamlit as st
import os
import json
import subprocess
import shutil
import zipfile
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
import psutil
from typing import List, Dict, Any
import tempfile
import threading
import time

# Optional imports
try:
    import pandas as pd
    PANDAS_AVAILABLE = True
except ImportError:
    PANDAS_AVAILABLE = False
    pd = None

try:
    import schedule
    SCHEDULE_AVAILABLE = True
except ImportError:
    SCHEDULE_AVAILABLE = False
    schedule = None

# Import our existing agents
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from multi_agent_orchestrator import MultiAgentOrchestrator
    from call_llama import call_llama_api
except ImportError:
    st.error("Missing required modules. Make sure all agent files are present.")

class PersonalOSCockpit:
    def __init__(self):
        self.workspace_root = os.path.expanduser("~/gringo_workspace")
        self.memory_db = os.path.join(self.workspace_root, "memory.db")
        self.orchestrator = MultiAgentOrchestrator()
        self.setup_workspace()
        self.setup_database()
        self.setup_agents()
        
    def setup_workspace(self):
        """Initialize workspace directory"""
        os.makedirs(self.workspace_root, exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "uploads"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "processed"), exist_ok=True)
        os.makedirs(os.path.join(self.workspace_root, "automated"), exist_ok=True)
        
    def setup_database(self):
        """Initialize SQLite database for memory and tracking"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        # Files table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filepath TEXT UNIQUE,
                filename TEXT,
                file_type TEXT,
                size_bytes INTEGER,
                created_at TIMESTAMP,
                last_modified TIMESTAMP,
                last_accessed TIMESTAMP,
                tags TEXT,
                importance_score INTEGER DEFAULT 5,
                ai_summary TEXT,
                agent_actions TEXT
            )
        ''')
        
        # Tasks table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_name TEXT,
                task_type TEXT,
                target_files TEXT,
                schedule_pattern TEXT,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                status TEXT DEFAULT 'active',
                results TEXT
            )
        ''')
        
        # Memory table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS memory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE,
                value TEXT,
                category TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
    def setup_agents(self):
        """Register all available agents"""
        agents_dir = os.path.join(os.path.dirname(__file__), "agents")
        
        agents = [
            ("planner", "planner_agent.py", "🧠 Task planning and breakdown"),
            ("refactor", "refactor_agent.py", "⚙️ Code refactoring and optimization"),
            ("test_gen", "test_generator_agent.py", "🧪 Automated test generation"),
            ("doc_gen", "doc_generator_agent.py", "📚 Documentation generation"),
            ("reviewer", "review_agent.py", "🔍 Code review and quality check"),
            ("performance", "performance_agent.py", "⚡ Performance monitoring"),
            ("ai_planner", "ai_planning_agent.py", "🤖 AI-powered planning with LLaMA"),
            ("deploy", "deploy_agent.py", "🚀 Deployment automation"),
            ("security", "security_agent.py", "🔒 Security analysis"),
            ("analytics", "analytics_agent.py", "📊 Code analytics"),
            ("api", "api_agent.py", "🌐 API detection and management"),
        ]
        
        for agent_id, script, description in agents:
            script_path = os.path.join(agents_dir, script)
            if os.path.exists(script_path):
                self.orchestrator.register_agent(agent_id, script_path, description)

    def execute_cli_command(self, command: str) -> Dict[str, Any]:
        """Execute CLI command and return results"""
        try:
            if command.startswith("gringo "):
                # Execute our AI assistant commands
                result = subprocess.run(
                    command.split(),
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
            elif command.startswith("cd "):
                # Handle directory changes
                target_dir = command[3:].strip()
                if os.path.exists(target_dir):
                    os.chdir(target_dir)
                    return {"success": True, "output": f"Changed to {os.getcwd()}"}
                else:
                    return {"success": False, "error": f"Directory not found: {target_dir}"}
            else:
                # Execute regular shell commands
                result = subprocess.run(
                    command,
                    shell=True,
                    cwd=self.workspace_root,
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                return {
                    "success": result.returncode == 0,
                    "output": result.stdout,
                    "error": result.stderr
                }
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def upload_and_process_files(self, uploaded_files):
        """Process uploaded files and add to workspace"""
        processed_files = []
        
        for uploaded_file in uploaded_files:
            # Save uploaded file
            upload_path = os.path.join(self.workspace_root, "uploads", uploaded_file.name)
            with open(upload_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Process based on file type
            if uploaded_file.name.endswith('.zip'):
                # Extract zip files
                extract_dir = os.path.join(self.workspace_root, "uploads", 
                                         uploaded_file.name.replace('.zip', ''))
                os.makedirs(extract_dir, exist_ok=True)
                
                with zipfile.ZipFile(upload_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_dir)
                
                # Add extracted files to tracking
                for root, dirs, files in os.walk(extract_dir):
                    for file in files:
                        file_path = os.path.join(root, file)
                        self.track_file(file_path)
                        processed_files.append(file_path)
            else:
                # Track individual file
                self.track_file(upload_path)
                processed_files.append(upload_path)
        
        return processed_files

    def track_file(self, file_path: str):
        """Add file to database tracking"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        file_stat = os.stat(file_path)
        file_info = {
            "filepath": file_path,
            "filename": os.path.basename(file_path),
            "file_type": os.path.splitext(file_path)[1],
            "size_bytes": file_stat.st_size,
            "created_at": datetime.fromtimestamp(file_stat.st_ctime),
            "last_modified": datetime.fromtimestamp(file_stat.st_mtime),
            "last_accessed": datetime.now()
        }
        
        cursor.execute('''
            INSERT OR REPLACE INTO files 
            (filepath, filename, file_type, size_bytes, created_at, last_modified, last_accessed)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            file_info["filepath"], file_info["filename"], file_info["file_type"],
            file_info["size_bytes"], file_info["created_at"], 
            file_info["last_modified"], file_info["last_accessed"]
        ))
        
        conn.commit()
        conn.close()

    def get_file_list(self) -> List[Dict]:
        """Get list of tracked files"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT filepath, filename, file_type, size_bytes, 
                   last_modified, tags, importance_score, ai_summary
            FROM files 
            ORDER BY importance_score DESC, last_modified DESC
        ''')
        
        files = []
        for row in cursor.fetchall():
            files.append({
                "filepath": row[0],
                "filename": row[1],
                "file_type": row[2],
                "size_bytes": row[3],
                "last_modified": row[4],
                "tags": row[5] or "",
                "importance_score": row[6],
                "ai_summary": row[7] or ""
            })
        
        conn.close()
        return files

    def run_agent_on_file(self, agent_name: str, file_path: str, instruction: str = ""):
        """Run specific agent on a file"""
        task_data = [{
            "agent": agent_name,
            "data": {
                "file_path": file_path,
                "instruction": instruction,
                "type": "process"
            }
        }]
        
        results = self.orchestrator.orchestrate_parallel(task_data)
        
        # Log agent action
        self.log_agent_action(file_path, agent_name, str(results))
        
        return results

    def log_agent_action(self, file_path: str, agent_name: str, result: str):
        """Log agent action to database"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE files 
            SET agent_actions = COALESCE(agent_actions, '') || ? 
            WHERE filepath = ?
        ''', (f"\n{datetime.now()}: {agent_name} - {result[:100]}...", file_path))
        
        conn.commit()
        conn.close()

    def schedule_task(self, task_name: str, task_type: str, target_files: str, 
                     schedule_pattern: str):
        """Schedule automated task"""
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO tasks (task_name, task_type, target_files, schedule_pattern, status)
            VALUES (?, ?, ?, ?, 'active')
        ''', (task_name, task_type, target_files, schedule_pattern))
        
        conn.commit()
        conn.close()

    def get_system_stats(self) -> Dict:
        """Get system performance statistics"""
        cpu_usage = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get file statistics
        conn = sqlite3.connect(self.memory_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM files')
        file_count = cursor.fetchone()[0]
        cursor.execute('SELECT SUM(size_bytes) FROM files')
        total_size = cursor.fetchone()[0] or 0
        conn.close()
        
        return {
            "cpu_usage": cpu_usage,
            "memory_usage": memory.percent,
            "disk_usage": (disk.used / disk.total) * 100,
            "tracked_files": file_count,
            "total_size_mb": round(total_size / 1024 / 1024, 2)
        }

def main():
    st.set_page_config(
        page_title="GRINGO Personal OS",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize the system
    if 'cockpit' not in st.session_state:
        st.session_state.cockpit = PersonalOSCockpit()
    
    cockpit = st.session_state.cockpit
    
    # Main header
    st.title("🤖 GRINGO Personal OS Cockpit")
    st.markdown("**100% Local AI-Powered Personal Operating System**")
    
    # Sidebar - File Browser & System Stats
    st.sidebar.title("📁 File Browser")
    
    # System stats
    stats = cockpit.get_system_stats()
    st.sidebar.metric("CPU Usage", f"{stats['cpu_usage']:.1f}%")
    st.sidebar.metric("Memory Usage", f"{stats['memory_usage']:.1f}%")
    st.sidebar.metric("Tracked Files", stats['tracked_files'])
    st.sidebar.metric("Total Size", f"{stats['total_size_mb']} MB")
    
    # File upload
    st.sidebar.subheader("📤 Upload Files")
    uploaded_files = st.sidebar.file_uploader(
        "Drop files or folders", 
        accept_multiple_files=True,
        type=None
    )
    
    if uploaded_files:
        with st.sidebar.spinner("Processing uploads..."):
            processed = cockpit.upload_and_process_files(uploaded_files)
            st.sidebar.success(f"Processed {len(processed)} files")
    
    # File list
    files = cockpit.get_file_list()
    st.sidebar.subheader("📋 Your Files")
    
    selected_file = None
    if files:
        file_options = [f"{f['filename']} ({f['file_type']})" for f in files]
        selected_idx = st.sidebar.selectbox("Select file:", range(len(file_options)), 
                                          format_func=lambda x: file_options[x])
        selected_file = files[selected_idx] if selected_idx is not None else None
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Terminal Interface
        st.subheader("💻 Terminal Interface")
        
        # Command input
        command = st.text_input("Enter command:", placeholder="ls, gringo help, python script.py, etc.")
        
        if st.button("Execute") and command:
            with st.spinner("Executing command..."):
                result = cockpit.execute_cli_command(command)
                
                if result["success"]:
                    st.success("Command executed successfully")
                    if result["output"]:
                        st.code(result["output"], language="bash")
                else:
                    st.error("Command failed")
                    if result.get("error"):
                        st.code(result["error"], language="bash")
        
        # File Content Viewer/Editor
        if selected_file:
            st.subheader(f"📄 File: {selected_file['filename']}")
            
            file_path = selected_file['filepath']
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Show file info
                    col_a, col_b, col_c = st.columns(3)
                    col_a.metric("Size", f"{selected_file['size_bytes']} bytes")
                    col_b.metric("Type", selected_file['file_type'])
                    col_c.metric("Score", selected_file['importance_score'])
                    
                    # File content
                    if len(content) < 10000:  # Only show small files directly
                        edited_content = st.text_area("File content:", content, height=300)
                        
                        if st.button("💾 Save Changes"):
                            with open(file_path, 'w', encoding='utf-8') as f:
                                f.write(edited_content)
                            st.success("File saved!")
                    else:
                        st.info(f"File too large to edit ({len(content)} chars). Use terminal or agent actions.")
                        st.code(content[:1000] + "...", language="text")
                        
                except Exception as e:
                    st.error(f"Cannot read file: {e}")
    
    with col2:
        # Agent Actions Panel
        st.subheader("🤖 AI Agent Actions")
        
        if selected_file:
            st.write(f"**Target:** {selected_file['filename']}")
            
            # Quick actions
            agent_actions = [
                ("📋 Summarize", "reviewer"),
                ("🔍 Analyze", "analytics"), 
                ("🛠 Fix/Refactor", "refactor"),
                ("🧪 Generate Tests", "test_gen"),
                ("📚 Document", "doc_gen"),
                ("🔒 Security Check", "security"),
                ("⚡ Performance", "performance")
            ]
            
            for action_name, agent_name in agent_actions:
                if st.button(action_name, key=f"action_{agent_name}"):
                    with st.spinner(f"Running {action_name}..."):
                        results = cockpit.run_agent_on_file(agent_name, selected_file['filepath'])
                        st.success(f"{action_name} completed!")
                        
                        # Show results
                        if results:
                            for result in results:
                                if result.success:
                                    st.code(result.output[:500] + "..." if len(result.output) > 500 else result.output)
                                else:
                                    st.error(f"Agent failed: {result.output}")
            
            # Custom instruction
            st.subheader("💬 Custom AI Instruction")
            custom_instruction = st.text_area(
                "Tell the AI what to do:",
                placeholder="Explain this code, find bugs, optimize performance, etc."
            )
            
            if st.button("🚀 Execute Custom Task") and custom_instruction:
                with st.spinner("Processing custom instruction..."):
                    # Use AI planner for custom instructions
                    results = cockpit.run_agent_on_file("ai_planner", selected_file['filepath'], 
                                                      custom_instruction)
                    st.success("Custom task completed!")
                    
                    if results:
                        for result in results:
                            st.code(result.output[:1000] + "..." if len(result.output) > 1000 else result.output)
        
        # Automation & Scheduling
        st.subheader("📅 Automation")
        
        with st.expander("Schedule Tasks"):
            task_name = st.text_input("Task name:", "Daily file cleanup")
            task_type = st.selectbox("Task type:", ["cleanup", "backup", "analyze", "summarize"])
            schedule_pattern = st.selectbox("Schedule:", ["daily", "weekly", "monthly"])
            
            if st.button("📅 Schedule Task"):
                cockpit.schedule_task(task_name, task_type, "all", schedule_pattern)
                st.success(f"Scheduled: {task_name}")
        
        # Memory & Tags
        st.subheader("🧠 Memory System")
        
        if selected_file:
            # File tags
            current_tags = selected_file['tags']
            new_tags = st.text_input("Tags:", current_tags, 
                                    placeholder="work, important, project-x")
            
            # Importance score
            importance = st.slider("Importance:", 1, 10, selected_file['importance_score'])
            
            if st.button("💾 Update File Info"):
                conn = sqlite3.connect(cockpit.memory_db)
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE files SET tags = ?, importance_score = ? WHERE filepath = ?
                ''', (new_tags, importance, selected_file['filepath']))
                conn.commit()
                conn.close()
                st.success("File info updated!")

    # Footer with agent status
    st.markdown("---")
    st.subheader("🤖 Agent Status")
    
    agent_cols = st.columns(4)
    agent_list = list(cockpit.orchestrator.agents.items())
    
    for i, (agent_id, info) in enumerate(agent_list):
        with agent_cols[i % 4]:
            status = "🟢" if info["active"] else "🔴"
            st.metric(f"{status} {agent_id}", info["description"][:20] + "...")

if __name__ == "__main__":
    main()
