#!/usr/bin/env python3
"""
SIMPLE GRINGO Personal OS - Working Version Without Complex Dependencies
"""

import streamlit as st
import os
import sys
import json
import subprocess
from datetime import datetime
import tempfile
import sqlite3

# Simple classes to avoid import issues
class SimpleProjectManager:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.projects_dir = os.path.join(workspace_root, "projects")
        os.makedirs(self.projects_dir, exist_ok=True)
    
    def create_simple_project(self, name: str, project_type: str, description: str):
        """Create a simple project"""
        project_path = os.path.join(self.projects_dir, name)
        os.makedirs(project_path, exist_ok=True)
        
        # Create basic files based on type
        if project_type == "python":
            with open(os.path.join(project_path, "main.py"), "w") as f:
                f.write(f'''#!/usr/bin/env python3
"""
{description}
"""

def main():
    print("Hello from {name}!")
    # TODO: Implement your logic here

if __name__ == "__main__":
    main()
''')
            
            with open(os.path.join(project_path, "README.md"), "w") as f:
                f.write(f'''# {name}

{description}

## Usage
```bash
python main.py
```
''')
        
        elif project_type == "web":
            with open(os.path.join(project_path, "index.html"), "w") as f:
                f.write(f'''<!DOCTYPE html>
<html>
<head>
    <title>{name}</title>
</head>
<body>
    <h1>{name}</h1>
    <p>{description}</p>
</body>
</html>
''')
        
        return {"name": name, "path": project_path, "type": project_type}
    
    def list_projects(self):
        """List all projects"""
        projects = []
        if os.path.exists(self.projects_dir):
            for item in os.listdir(self.projects_dir):
                item_path = os.path.join(self.projects_dir, item)
                if os.path.isdir(item_path):
                    projects.append({
                        "name": item,
                        "path": item_path,
                        "created": datetime.fromtimestamp(os.path.getctime(item_path)).strftime("%Y-%m-%d")
                    })
        return projects

class SimpleTerminal:
    def __init__(self):
        self.history = []
    
    def render(self):
        """Render terminal interface"""
        st.subheader("💻 Terminal")
        
        command = st.text_input("Command:", placeholder="ls, pwd, python --version")
        
        if st.button("Execute") and command:
            self.execute_command(command)
        
        # Show recent commands
        if self.history:
            st.markdown("**Recent Commands:**")
            for cmd, output in self.history[-3:]:
                with st.expander(f"$ {cmd}"):
                    st.code(output)
    
    def execute_command(self, command):
        """Execute command"""
        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=10
            )
            output = f"Exit: {result.returncode}\n{result.stdout}\n{result.stderr}"
            self.history.append((command, output))
            st.success("Command executed")
            st.code(output)
        except Exception as e:
            error = f"Error: {e}"
            self.history.append((command, error))
            st.error(error)

class SimpleFileManager:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
    
    def render(self):
        """Render file manager"""
        st.subheader("📁 File Manager")
        
        # File upload
        uploaded_file = st.file_uploader("Upload file:", type=['py', 'txt', 'md', 'json'])
        
        if uploaded_file:
            # Save uploaded file
            upload_dir = os.path.join(self.workspace_root, "uploads")
            os.makedirs(upload_dir, exist_ok=True)
            
            file_path = os.path.join(upload_dir, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getvalue())
            
            st.success(f"File saved: {file_path}")
            
            # Show content preview
            if uploaded_file.name.endswith(('.py', '.txt', '.md', '.json')):
                with st.expander("File Preview"):
                    with open(file_path, 'r') as f:
                        content = f.read()
                        st.code(content[:1000] + "..." if len(content) > 1000 else content)
        
        # Browse files
        if os.path.exists(self.workspace_root):
            st.markdown("**Workspace Files:**")
            self.show_directory(self.workspace_root)
    
    def show_directory(self, path: str, level: int = 0):
        """Show directory contents"""
        if level > 2:  # Limit depth
            return
        
        try:
            items = sorted(os.listdir(path))
            for item in items[:10]:  # Limit items
                item_path = os.path.join(path, item)
                indent = "  " * level
                
                if os.path.isdir(item_path):
                    st.text(f"{indent}📁 {item}/")
                    if level < 1:  # Only show one level deep
                        self.show_directory(item_path, level + 1)
                else:
                    st.text(f"{indent}📄 {item}")
        except PermissionError:
            st.text(f"{indent}❌ Permission denied")

def main():
    """Main application"""
    st.set_page_config(
        page_title="🤖 GRINGO Personal OS - Simple",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 GRINGO Personal OS")
    st.markdown("**Simple, Working Version - 100% Local AI Assistant**")
    
    # Initialize workspace
    workspace_root = os.path.expanduser("~/gringo_workspace")
    os.makedirs(workspace_root, exist_ok=True)
    
    # Initialize components
    if 'project_manager' not in st.session_state:
        st.session_state.project_manager = SimpleProjectManager(workspace_root)
    
    if 'terminal' not in st.session_state:
        st.session_state.terminal = SimpleTerminal()
    
    if 'file_manager' not in st.session_state:
        st.session_state.file_manager = SimpleFileManager(workspace_root)
    
    # Sidebar navigation
    st.sidebar.title("🤖 GRINGO")
    st.sidebar.markdown("**Simple Mode**")
    
    tab = st.sidebar.radio(
        "Navigate:",
        ["🏠 Dashboard", "🚀 Create Project", "💻 Terminal", "📁 Files", "🤖 Chat"]
    )
    
    # Show system info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**System Info:**")
    st.sidebar.text(f"Workspace: ~/gringo_workspace")
    
    projects = st.session_state.project_manager.list_projects()
    st.sidebar.metric("Projects", len(projects))
    
    # Main content
    if tab == "🏠 Dashboard":
        st.subheader("🏠 Dashboard")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("📁 Projects", len(projects))
        col2.metric("💾 Workspace", f"{workspace_root}")
        col3.metric("🟢 Status", "Running")
        
        # Recent projects
        if projects:
            st.markdown("**Recent Projects:**")
            for project in projects[-3:]:
                with st.expander(f"📁 {project['name']}"):
                    st.text(f"Path: {project['path']}")
                    st.text(f"Created: {project['created']}")
                    
                    if st.button(f"Open {project['name']}", key=f"open_{project['name']}"):
                        st.info(f"Opening {project['path']}")
    
    elif tab == "🚀 Create Project":
        st.subheader("🚀 Create New Project")
        
        project_name = st.text_input("Project name:", placeholder="my_awesome_project")
        project_type = st.selectbox("Project type:", ["python", "web", "data", "automation"])
        description = st.text_area("Description:", placeholder="What does this project do?")
        
        if st.button("🚀 Create Project") and project_name:
            try:
                result = st.session_state.project_manager.create_simple_project(
                    project_name, project_type, description
                )
                st.success(f"✅ Created project: {result['name']}")
                st.info(f"📁 Location: {result['path']}")
                
                # Show created files
                if os.path.exists(result['path']):
                    files = os.listdir(result['path'])
                    st.markdown("**Created files:**")
                    for file in files:
                        st.text(f"📄 {file}")
                
            except Exception as e:
                st.error(f"❌ Failed to create project: {e}")
    
    elif tab == "💻 Terminal":
        st.session_state.terminal.render()
    
    elif tab == "📁 Files":
        st.session_state.file_manager.render()
    
    elif tab == "🤖 Chat":
        st.subheader("🤖 AI Chat")
        
        # Simple chat with Ollama
        user_input = st.text_area("Message:", placeholder="Ask me anything...")
        
        if st.button("Send") and user_input:
            with st.spinner("🤖 Thinking..."):
                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "llama3", "prompt": user_input},
                        stream=True,
                        timeout=30
                    )
                    
                    full_response = ""
                    for line in response.iter_lines():
                        if line:
                            data = json.loads(line)
                            full_response += data.get("response", "")
                    
                    st.markdown(f"**🧠 You:** {user_input}")
                    st.markdown(f"**🤖 AI:** {full_response}")
                    
                except Exception as e:
                    st.error(f"❌ AI chat failed: {e}")
                    st.info("💡 Make sure Ollama is running: `ollama serve`")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔒 **100% Local & Private**")
    st.sidebar.markdown("No data leaves your machine")

if __name__ == "__main__":
    main()
