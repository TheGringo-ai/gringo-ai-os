#!/usr/bin/env python3
"""
GRINGO Full Project Creation Interface - Working Version
Complete project management with file upload and natural language creation
"""

import streamlit as st
import os
import sys
import json
import tempfile
import zipfile
import shutil
from datetime import datetime
import subprocess
import sqlite3
from pathlib import Path
from custom_tools_manager import CustomToolsManager
from multi_agent_orchestrator import MultiAgentOrchestrator, AgentResult

# Set page config first
st.set_page_config(
    page_title="🤖 GRINGO Project Creator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

class FullProjectManager:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.projects_dir = os.path.join(workspace_root, "projects")
        self.uploads_dir = os.path.join(workspace_root, "uploads")
        self.templates_dir = os.path.join(workspace_root, "templates")
        self.db_path = os.path.join(workspace_root, "projects.db")
        self._init_directories()
        self._init_database()
    
    def _init_directories(self):
        """Initialize all directories"""
        for dir_path in [self.projects_dir, self.uploads_dir, self.templates_dir]:
            os.makedirs(dir_path, exist_ok=True)
    
    def _init_database(self):
        """Initialize projects database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                type TEXT,
                description TEXT,
                path TEXT,
                status TEXT DEFAULT 'active',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_project_from_prompt(self, prompt: str, project_name: str = None) -> dict:
        """Create a project from natural language prompt"""
        
        # Analyze prompt to determine project type
        project_info = self._analyze_prompt(prompt)
        
        if not project_name:
            project_name = project_info.get('suggested_name', f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Create project directory
        project_path = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Generate project files
        files_created = self._generate_project_files(project_path, project_info, prompt)
        
        # Save to database
        self._save_project_to_db(project_name, project_info, project_path, prompt)
        
        return {
            "name": project_name,
            "path": project_path,
            "type": project_info['type'],
            "language": project_info['language'],
            "files_created": files_created,
            "description": prompt,
            "status": "created"
        }
    
    def _analyze_prompt(self, prompt: str) -> dict:
        """Analyze prompt to determine project type and language"""
        prompt_lower = prompt.lower()
        
        # Detect project type
        if any(word in prompt_lower for word in ['web', 'website', 'frontend', 'html', 'css', 'react', 'vue']):
            project_type = 'web'
        elif any(word in prompt_lower for word in ['api', 'backend', 'server', 'flask', 'django', 'fastapi']):
            project_type = 'backend'
        elif any(word in prompt_lower for word in ['data', 'analysis', 'pandas', 'csv', 'charts', 'visualization']):
            project_type = 'data_science'
        elif any(word in prompt_lower for word in ['game', 'pygame', '2d', 'platformer', 'arcade']):
            project_type = 'game'
        elif any(word in prompt_lower for word in ['automation', 'script', 'tool', 'file', 'organize']):
            project_type = 'automation'
        elif any(word in prompt_lower for word in ['calculator', 'math', 'compute', 'calculate']):
            project_type = 'utility'
        else:
            project_type = 'general'
        
        # Detect language
        if any(word in prompt_lower for word in ['python', 'py', 'pygame', 'flask', 'django', 'pandas']):
            language = 'python'
        elif any(word in prompt_lower for word in ['javascript', 'js', 'node', 'react', 'html']):
            language = 'javascript'
        else:
            language = 'python'  # Default
        
        return {
            'type': project_type,
            'language': language,
            'suggested_name': self._suggest_name(prompt, project_type),
            'features': self._extract_features(prompt_lower)
        }
    
    def _suggest_name(self, prompt: str, project_type: str) -> str:
        """Suggest a project name"""
        words = [w for w in prompt.lower().split() if len(w) > 3 and w not in ['create', 'build', 'make', 'develop']]
        if words:
            name = '_'.join(words[:3])
        else:
            name = project_type
        return f"{name}_{datetime.now().strftime('%m%d')}"
    
    def _extract_features(self, prompt: str) -> list:
        """Extract features from prompt"""
        features = []
        if 'database' in prompt or 'db' in prompt or 'sqlite' in prompt:
            features.append('database')
        if 'web' in prompt or 'html' in prompt:
            features.append('web_interface')
        if 'api' in prompt:
            features.append('api')
        if 'file' in prompt:
            features.append('file_handling')
        return features
    
    def _generate_project_files(self, project_path: str, project_info: dict, prompt: str) -> list:
        """Generate project files based on type and prompt"""
        files_created = []
        
        # Create basic structure
        os.makedirs(os.path.join(project_path, 'src'), exist_ok=True)
        os.makedirs(os.path.join(project_path, 'tests'), exist_ok=True)
        files_created.extend(['📁 src/', '📁 tests/'])
        
        if project_info['language'] == 'python':
            files_created.extend(self._create_python_project(project_path, project_info, prompt))
        elif project_info['language'] == 'javascript':
            files_created.extend(self._create_javascript_project(project_path, project_info, prompt))
        
        return files_created
    
    def _create_python_project(self, project_path: str, project_info: dict, prompt: str) -> list:
        """Create Python project files"""
        files = []
        
        # main.py
        main_content = self._generate_python_main(project_info, prompt)
        with open(os.path.join(project_path, 'main.py'), 'w') as f:
            f.write(main_content)
        files.append('🐍 main.py')
        
        # requirements.txt
        requirements = self._get_python_requirements(project_info)
        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(requirements))
        files.append('📦 requirements.txt')
        
        # README.md
        readme_content = self._generate_readme(project_info, prompt)
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        files.append('📖 README.md')
        
        # run.py
        run_content = f'''#!/usr/bin/env python3
"""
Run script for {project_info.get('suggested_name', 'project')}
"""

if __name__ == "__main__":
    from main import main
    main()
'''
        with open(os.path.join(project_path, 'run.py'), 'w') as f:
            f.write(run_content)
        files.append('🚀 run.py')
        
        return files
    
    def _generate_python_main(self, project_info: dict, prompt: str) -> str:
        """Generate Python main file based on project type"""
        
        project_type = project_info['type']
        
        if project_type == 'web':
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

import streamlit as st

def main():
    st.title("🌐 {project_info.get('suggested_name', 'Web App')}")
    st.markdown("**{prompt[:100]}...**")
    
    # TODO: Implement your web application here
    st.write("Welcome to your new web application!")
    
    user_input = st.text_input("Enter something:")
    if user_input:
        st.success(f"You entered: {{user_input}}")

if __name__ == "__main__":
    main()
'''
        
        elif project_type == 'data_science':
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

import pandas as pd
import matplotlib.pyplot as plt

def main():
    print("📊 Data Science Project: {project_info.get('suggested_name', 'Data Analysis')}")
    print("🎯 Goal: {prompt[:100]}...")
    
    # TODO: Load your data
    # df = pd.read_csv('your_data.csv')
    
    # Sample data for demonstration
    data = {{'x': [1, 2, 3, 4, 5], 'y': [2, 4, 6, 8, 10]}}
    df = pd.DataFrame(data)
    
    print("\\n📈 Sample data:")
    print(df.head())
    
    # TODO: Implement your analysis here
    print("\\n✅ Project ready for your data analysis!")

if __name__ == "__main__":
    main()
'''
        
        elif project_type == 'game':
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

import pygame
import sys

# Initialize Pygame
pygame.init()

# Game settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

def main():
    """Main game loop"""
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("{project_info.get('suggested_name', 'Game')}")
    clock = pygame.time.Clock()
    
    # Game variables
    player_x = SCREEN_WIDTH // 2
    player_y = SCREEN_HEIGHT // 2
    
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            player_x -= 5
        if keys[pygame.K_RIGHT]:
            player_x += 5
        if keys[pygame.K_UP]:
            player_y -= 5
        if keys[pygame.K_DOWN]:
            player_y += 5
        
        # Draw everything
        screen.fill((0, 0, 0))  # Black background
        pygame.draw.circle(screen, (255, 255, 255), (player_x, player_y), 20)
        
        pygame.display.flip()
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
'''
        
        elif project_type == 'automation':
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

import os
import shutil
from datetime import datetime

def main():
    """Main automation script"""
    print("🤖 Automation Script: {project_info.get('suggested_name', 'Automation')}")
    print("🎯 Purpose: {prompt[:100]}...")
    
    # TODO: Implement your automation logic here
    
    # Example: File organization
    print("\\n📁 Example: Organizing files by extension...")
    
    # Get current directory files
    current_dir = "."
    files = [f for f in os.listdir(current_dir) if os.path.isfile(f)]
    
    print(f"Found {{len(files)}} files to process")
    
    # Group by extension
    extensions = {{}}
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if ext not in extensions:
            extensions[ext] = []
        extensions[ext].append(file)
    
    print("\\nFile types found:")
    for ext, file_list in extensions.items():
        print(f"  {{ext or 'no extension'}}: {{len(file_list)}} files")
    
    print("\\n✅ Automation script ready for customization!")

if __name__ == "__main__":
    main()
'''
        
        elif project_type == 'utility':
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

def main():
    """Main utility application"""
    print("🔧 Utility: {project_info.get('suggested_name', 'Utility')}")
    print("🎯 Purpose: {prompt[:100]}...")
    
    while True:
        print("\\n" + "="*40)
        print("Choose an operation:")
        print("1. Basic calculation")
        print("2. Text processing")
        print("3. File operations")
        print("4. Exit")
        
        choice = input("\\nEnter your choice (1-4): ").strip()
        
        if choice == "1":
            # TODO: Implement calculation logic
            try:
                expr = input("Enter expression: ")
                result = eval(expr)  # Note: Use ast.literal_eval for safety
                print(f"Result: {{result}}")
            except Exception as e:
                print(f"Error: {{e}}")
        
        elif choice == "2":
            # TODO: Implement text processing
            text = input("Enter text: ")
            print(f"Length: {{len(text)}} characters")
            print(f"Words: {{len(text.split())}} words")
        
        elif choice == "3":
            # TODO: Implement file operations
            print("File operations placeholder")
        
        elif choice == "4":
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == "__main__":
    main()
'''
        
        else:  # general
            return f'''#!/usr/bin/env python3
"""
{prompt}
"""

def main():
    """Main application function"""
    print("🚀 Project: {project_info.get('suggested_name', 'New Project')}")
    print("📝 Description: {prompt[:100]}...")
    
    # TODO: Implement your project logic here
    print("\\n✅ Project template ready!")
    print("Edit this file to implement your specific requirements.")

if __name__ == "__main__":
    main()
'''
    
    def _get_python_requirements(self, project_info: dict) -> list:
        """Get Python requirements based on project type"""
        base_requirements = ['requests']
        
        if project_info['type'] == 'web':
            base_requirements.extend(['streamlit', 'pandas'])
        elif project_info['type'] == 'data_science':
            base_requirements.extend(['pandas', 'matplotlib', 'numpy', 'jupyter'])
        elif project_info['type'] == 'game':
            base_requirements.extend(['pygame'])
        elif project_info['type'] == 'automation':
            base_requirements.extend(['beautifulsoup4', 'selenium'])
        
        if 'database' in project_info.get('features', []):
            base_requirements.append('sqlite3')
        
        return base_requirements
    
    def _generate_readme(self, project_info: dict, prompt: str) -> str:
        """Generate README.md"""
        return f'''# {project_info.get('suggested_name', 'New Project')}

{prompt}

## Project Details
- **Type**: {project_info['type']}
- **Language**: {project_info['language']}
- **Created**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Installation
```bash
pip install -r requirements.txt
```

## Usage
```bash
python main.py
# or
python run.py
```

## Features
{chr(10).join(f"- {feature}" for feature in project_info.get('features', ['Basic functionality']))}

## Development
1. Edit `main.py` to implement your specific requirements
2. Add dependencies to `requirements.txt`
3. Write tests in the `tests/` directory
4. Update this README with your progress

---
*Generated by GRINGO Personal OS*
'''
    
    def _save_project_to_db(self, name: str, project_info: dict, path: str, prompt: str):
        """Save project to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO projects (name, type, description, path, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            project_info['type'],
            prompt,
            path,
            json.dumps(project_info)
        ))
        
        conn.commit()
        conn.close()
    
    def list_projects(self) -> list:
        """List all projects"""
        if not os.path.exists(self.db_path):
            return []
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM projects ORDER BY created_at DESC')
        projects = []
        
        for row in cursor.fetchall():
            projects.append({
                'id': row[0],
                'name': row[1],
                'type': row[2],
                'description': row[3],
                'path': row[4],
                'status': row[5],
                'created_at': row[6]
            })
        
        conn.close()
        return projects
    
    def run_project(self, project_name: str) -> dict:
        """Run a project"""
        projects = self.list_projects()
        project = next((p for p in projects if p['name'] == project_name), None)
        
        if not project:
            return {"error": "Project not found"}
        
        project_path = project['path']
        
        # Try different run methods
        run_files = ['run.py', 'main.py', 'app.py']
        
        for run_file in run_files:
            file_path = os.path.join(project_path, run_file)
            if os.path.exists(file_path):
                try:
                    result = subprocess.run(
                        ['python', run_file],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=10
                    )
                    
                    return {
                        "success": True,
                        "output": result.stdout,
                        "errors": result.stderr,
                        "return_code": result.returncode
                    }
                    
                except subprocess.TimeoutExpired:
                    return {"error": "Project execution timed out"}
                except Exception as e:
                    return {"error": f"Failed to run: {e}"}
        
        return {"error": "No runnable file found"}

def render_project_creator():
    """Render the main project creator interface"""
    
    st.title("🚀 GRINGO Project Creator")
    st.markdown("**Create any project through natural language prompts**")
    
    # Initialize project manager
    workspace_root = os.path.expanduser("~/gringo_workspace")
    if 'project_manager' not in st.session_state:
        st.session_state.project_manager = FullProjectManager(workspace_root)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "💬 Create from Prompt", 
        "📁 Upload Files", 
        "🔧 Manage Projects",
        "🎯 Quick Tasks"
    ])
    
    with tab1:
        st.subheader("🧠 Create Project from Description")
        
        # Examples
        with st.expander("💡 Example Prompts", expanded=False):
            st.markdown("""
**Try these examples:**
- `Create a simple calculator with a web interface`
- `Build a file organization script that sorts files by type`
- `Make a 2D game with Pygame where a player moves around`
- `Create a data analysis tool for CSV files with charts`
- `Build a web scraper that collects news articles`
- `Make an automation script for backing up files`
""")
        
        # Main prompt input
        prompt = st.text_area(
            "Describe what you want to build:",
            placeholder="Create a simple calculator with a web interface using Streamlit",
            height=100
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            project_name = st.text_input(
                "Project name (optional):",
                placeholder="Leave empty for auto-generated name"
            )
        with col2:
            auto_run = st.checkbox("Auto-run after creation", value=False)
        
        if st.button("🚀 Create Project", type="primary") and prompt:
            with st.spinner("🤖 Creating your project..."):
                try:
                    result = st.session_state.project_manager.create_project_from_prompt(
                        prompt, project_name if project_name else None
                    )
                    
                    st.success(f"✅ Project '{result['name']}' created successfully!")
                    
                    # Show details
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown("**📊 Project Details:**")
                        st.text(f"Name: {result['name']}")
                        st.text(f"Type: {result['type']}")
                        st.text(f"Language: {result['language']}")
                        st.text(f"Location: {result['path']}")
                    
                    with col2:
                        st.markdown("**📁 Files Created:**")
                        for file in result['files_created']:
                            st.text(file)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        if st.button("▶️ Run Project"):
                            run_result = st.session_state.project_manager.run_project(result['name'])
                            if run_result.get('success'):
                                st.success("✅ Project executed!")
                                with st.expander("📊 Output"):
                                    st.code(run_result['output'])
                            else:
                                st.error(f"❌ Error: {run_result.get('error')}")
                    
                    with col2:
                        if st.button("📁 Open Folder"):
                            st.info(f"📂 Project location: {result['path']}")
                    
                    with col3:
                        if st.button("📋 Show Code"):
                            main_file = os.path.join(result['path'], 'main.py')
                            if os.path.exists(main_file):
                                with open(main_file, 'r') as f:
                                    code = f.read()
                                with st.expander("📄 main.py", expanded=True):
                                    st.code(code, language='python')
                    
                    # Auto-run if requested
                    if auto_run:
                        st.info("🔄 Auto-running project...")
                        run_result = st.session_state.project_manager.run_project(result['name'])
                        if run_result.get('success'):
                            st.success("✅ Auto-run completed!")
                            st.code(run_result['output'])
                    
                except Exception as e:
                    st.error(f"❌ Failed to create project: {e}")
    
    with tab2:
        st.subheader("📁 File Upload & Analysis")
        
        uploaded_files = st.file_uploader(
            "Upload files:",
            accept_multiple_files=True,
            type=['py', 'js', 'html', 'css', 'txt', 'md', 'json', 'csv']
        )
        
        if uploaded_files:
            st.markdown(f"**📊 {len(uploaded_files)} files uploaded:**")
            
            for file in uploaded_files:
                with st.expander(f"📄 {file.name}"):
                    # Save file
                    upload_path = os.path.join(workspace_root, "uploads", file.name)
                    with open(upload_path, "wb") as f:
                        f.write(file.getvalue())
                    
                    st.success(f"✅ Saved to: {upload_path}")
                    
                    # Show preview
                    if file.name.endswith(('.py', '.js', '.html', '.css', '.txt', '.md', '.json')):
                        try:
                            content = file.getvalue().decode('utf-8')
                            st.code(content[:500] + "..." if len(content) > 500 else content)
                        except:
                            st.text("Binary file - preview not available")
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if st.button(f"🔍 Analyze {file.name}", key=f"analyze_{file.name}"):
                            st.info("File analysis would go here")
                    with col2:
                        if st.button(f"🚀 Create Project", key=f"project_{file.name}"):
                            st.info("Project creation from file would go here")
                    with col3:
                        if st.button(f"🤖 AI Review", key=f"review_{file.name}"):
                            st.info("AI review would go here")
    
    with tab3:
        st.subheader("🔧 Project Management")
        
        projects = st.session_state.project_manager.list_projects()
        
        if not projects:
            st.info("No projects created yet. Use the 'Create from Prompt' tab to get started!")
        else:
            st.markdown(f"**📁 {len(projects)} Projects Found:**")
            
            # Display projects in grid
            cols = st.columns(2)
            for i, project in enumerate(projects):
                with cols[i % 2]:
                    with st.container():
                        st.markdown(f"**📁 {project['name']}**")
                        st.text(f"Type: {project['type']}")
                        st.text(f"Created: {project['created_at'][:10]}")
                        st.caption(project['description'][:100] + "..." if len(project['description']) > 100 else project['description'])
                        
                        # Action buttons
                        button_cols = st.columns(3)
                        with button_cols[0]:
                            if st.button("▶️", key=f"run_{project['id']}", help="Run Project"):
                                run_result = st.session_state.project_manager.run_project(project['name'])
                                if run_result.get('success'):
                                    st.success("✅ Executed!")
                                    st.code(run_result['output'])
                                else:
                                    st.error(f"❌ {run_result.get('error')}")
                        
                        with button_cols[1]:
                            if st.button("📁", key=f"open_{project['id']}", help="Open Folder"):
                                st.info(f"📂 {project['path']}")
                        
                        with button_cols[2]:
                            if st.button("📋", key=f"code_{project['id']}", help="Show Code"):
                                main_file = os.path.join(project['path'], 'main.py')
                                if os.path.exists(main_file):
                                    with open(main_file, 'r') as f:
                                        code = f.read()
                                    st.code(code[:500] + "..." if len(code) > 500 else code, language='python')
    
    with tab4:
        st.subheader("🎯 Quick Tasks")
        
        st.markdown("**Execute any task through natural language:**")
        
        task_prompt = st.text_area(
            "What task do you want to perform?",
            placeholder="""Examples:
- List all my Python projects
- Show me the code structure of my calculator project  
- Create a backup of all my projects
- Find projects that use Streamlit
- Generate a report of all my projects""",
            height=100
        )
        
        if st.button("🚀 Execute Task") and task_prompt:
            with st.spinner("🤖 Processing task..."):
                # Simple task processing
                task_lower = task_prompt.lower()
                
                if 'list' in task_lower and 'project' in task_lower:
                    projects = st.session_state.project_manager.list_projects()
                    st.success(f"✅ Found {len(projects)} projects:")
                    for project in projects:
                        st.text(f"📁 {project['name']} ({project['type']}) - {project['created_at'][:10]}")
                
                elif 'backup' in task_lower:
                    st.success("✅ Backup task simulated!")
                    st.info("In a full implementation, this would create backups of all projects")
                
                elif 'report' in task_lower:
                    projects = st.session_state.project_manager.list_projects()
                    st.success("✅ Project Report Generated:")
                    
                    if projects:
                        types = {}
                        for project in projects:
                            ptype = project['type']
                            types[ptype] = types.get(ptype, 0) + 1
                        
                        st.markdown("**📊 Project Types:**")
                        for ptype, count in types.items():
                            st.text(f"  {ptype}: {count} projects")
                        
                        st.markdown(f"**📅 Total Projects:** {len(projects)}")
                        st.markdown(f"**📍 Workspace:** {workspace_root}")
                    else:
                        st.info("No projects to report on")
                
                else:
                    st.info("🤖 Task processing simulated. In a full implementation, this would use AI to understand and execute your request.")

def render_custom_tools():
    """Render the custom tools interface"""
    st.title("🛠️ Custom Tools Manager")
    st.markdown("**Create, save, and run custom development tools**")
    
    # Initialize tools manager
    workspace_root = os.path.expanduser("~/gringo_workspace")
    if 'tools_manager' not in st.session_state:
        st.session_state.tools_manager = CustomToolsManager(workspace_root)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🔧 Create Tool",
        "📚 Tool Library", 
        "▶️ Run Tools",
        "📦 Import/Export"
    ])
    
    with tab1:
        st.subheader("🔨 Create New Tool")
        
        # Tool creation form
        col1, col2 = st.columns(2)
        
        with col1:
            tool_name = st.text_input("Tool Name:", placeholder="File Organizer")
            tool_category = st.selectbox(
                "Category:",
                st.session_state.tools_manager.tools["categories"]
            )
            tool_language = st.selectbox(
                "Language:",
                ["python", "javascript", "bash"]
            )
        
        with col2:
            tool_description = st.text_area(
                "Description:",
                placeholder="Organize files by extension into folders",
                height=100
            )
        
        # Code editor
        st.markdown("**Code:**")
        
        # Template selector
        template_options = ["Custom Code"] + list(st.session_state.tools_manager.get_tool_templates().keys())
        selected_template = st.selectbox("Use Template:", template_options)
        
        if selected_template != "Custom Code":
            templates = st.session_state.tools_manager.get_tool_templates()
            template_code = templates[selected_template]["code"]
            tool_name = tool_name or templates[selected_template]["name"]
            tool_description = tool_description or templates[selected_template]["description"]
            tool_category = templates[selected_template]["category"]
            tool_language = templates[selected_template]["language"]
        else:
            template_code = ""
        
        tool_code = st.text_area(
            "Code:",
            value=template_code,
            height=300,
            placeholder='''# Example Python tool
import sys

def main():
    print("Hello from custom tool!")
    if len(sys.argv) > 1:
        print(f"Args: {sys.argv[1:]}")

if __name__ == "__main__":
    main()
'''
        )
        
        # Arguments schema
        with st.expander("⚙️ Arguments Schema (Optional)"):
            st.markdown("Define what arguments this tool accepts:")
            args_schema = st.text_area(
                "Arguments (JSON format):",
                placeholder='{"file_path": "Path to file", "operation": "Operation to perform"}',
                height=100
            )
        
        if st.button("🚀 Create Tool", type="primary"):
            if tool_name and tool_code:
                try:
                    # Parse args schema
                    import json
                    parsed_args = json.loads(args_schema) if args_schema else {}
                    
                    # Create tool
                    result = st.session_state.tools_manager.create_tool(
                        name=tool_name,
                        description=tool_description,
                        category=tool_category,
                        language=tool_language,
                        code=tool_code,
                        args_schema=parsed_args
                    )
                    
                    st.success(f"✅ Tool '{result['name']}' created successfully!")
                    st.info(f"📁 Saved to: {result['file_path']}")
                    
                except Exception as e:
                    st.error(f"❌ Failed to create tool: {e}")
            else:
                st.error("❌ Please provide tool name and code")
    
    with tab2:
        st.subheader("📚 Tool Library")
        
        # Category filter
        categories = ["All"] + st.session_state.tools_manager.tools["categories"]
        selected_category = st.selectbox("Filter by category:", categories)
        
        # Get tools
        if selected_category == "All":
            tools = st.session_state.tools_manager.get_tools_by_category()
        else:
            tools = st.session_state.tools_manager.get_tools_by_category(selected_category)
        
        if not tools:
            st.info("No tools found. Create your first tool in the 'Create Tool' tab!")
        else:
            st.markdown(f"**📊 {len(tools)} Tools Found:**")
            
            # Display tools in grid
            for i in range(0, len(tools), 2):
                col1, col2 = st.columns(2)
                
                for j, col in enumerate([col1, col2]):
                    if i + j < len(tools):
                        tool = tools[i + j]
                        
                        with col:
                            with st.container():
                                st.markdown(f"**🔧 {tool['name']}**")
                                st.text(f"Category: {tool['category']}")
                                st.text(f"Language: {tool['language']}")
                                st.text(f"Uses: {tool['usage_count']}")
                                st.caption(tool['description'])
                                
                                # Action buttons
                                button_cols = st.columns(4)
                                
                                with button_cols[0]:
                                    if st.button("▶️", key=f"run_tool_{tool['id']}", help="Run Tool"):
                                        st.session_state[f"run_tool_{tool['id']}"] = True
                                
                                with button_cols[1]:
                                    if st.button("📋", key=f"view_tool_{tool['id']}", help="View Code"):
                                        with open(tool['file_path'], 'r') as f:
                                            code = f.read()
                                        st.code(code, language=tool['language'])
                                
                                with button_cols[2]:
                                    if st.button("📁", key=f"open_tool_{tool['id']}", help="Open File"):
                                        st.info(f"📂 {tool['file_path']}")
                                
                                with button_cols[3]:
                                    if st.button("🗑️", key=f"delete_tool_{tool['id']}", help="Delete Tool"):
                                        if st.session_state.tools_manager.delete_tool(tool['id']):
                                            st.success("✅ Tool deleted!")
                                            st.rerun()
                                        else:
                                            st.error("❌ Failed to delete tool")
    
    with tab3:
        st.subheader("▶️ Run Tools")
        
        tools = st.session_state.tools_manager.get_tools_by_category()
        
        if not tools:
            st.info("No tools available. Create tools first!")
        else:
            # Tool selector
            tool_options = [(f"{tool['name']} ({tool['category']})", tool['id']) for tool in tools]
            selected_tool_name, selected_tool_id = st.selectbox(
                "Select tool to run:",
                options=tool_options,
                format_func=lambda x: x[0]
            )
            
            # Get selected tool
            selected_tool = next(t for t in tools if t['id'] == selected_tool_id)
            
            st.markdown(f"**📝 Description:** {selected_tool['description']}")
            
            # Arguments input
            if selected_tool['args_schema']:
                st.markdown("**⚙️ Arguments:**")
                args = []
                for arg_name, arg_desc in selected_tool['args_schema'].items():
                    arg_value = st.text_input(f"{arg_name}:", placeholder=arg_desc)
                    if arg_value:
                        args.append(arg_value)
            else:
                args = []
                custom_args = st.text_input("Custom arguments (space-separated):")
                if custom_args:
                    args = custom_args.split()
            
            # Run button
            if st.button("🚀 Run Tool", type="primary"):
                with st.spinner("🔄 Running tool..."):
                    result = st.session_state.tools_manager.run_tool(selected_tool_id, args)
                    
                    if result.get('success'):
                        st.success("✅ Tool executed successfully!")
                        
                        if result['output']:
                            with st.expander("📊 Output", expanded=True):
                                st.code(result['output'])
                        
                        if result['errors']:
                            with st.expander("⚠️ Errors"):
                                st.code(result['errors'])
                    
                    else:
                        st.error(f"❌ Tool failed: {result.get('error')}")
    
    with tab4:
        st.subheader("📦 Import/Export Tools")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📤 Export Tool**")
            
            tools = st.session_state.tools_manager.get_tools_by_category()
            if tools:
                export_tool = st.selectbox(
                    "Select tool to export:",
                    options=[(t['name'], t['id']) for t in tools],
                    format_func=lambda x: x[0],
                    key="export_select"
                )
                
                if st.button("📤 Export Tool"):
                    export_data = st.session_state.tools_manager.export_tool(export_tool[1])
                    if 'error' not in export_data:
                        st.download_button(
                            label="💾 Download Tool",
                            data=json.dumps(export_data, indent=2),
                            file_name=f"{export_tool[0].lower().replace(' ', '_')}_tool.json",
                            mime="application/json"
                        )
                    else:
                        st.error(export_data['error'])
            else:
                st.info("No tools to export")
        
        with col2:
            st.markdown("**📥 Import Tool**")
            
            uploaded_file = st.file_uploader(
                "Upload tool JSON:",
                type=['json'],
                key="tool_import"
            )
            
            if uploaded_file is not None:
                try:
                    import_data = json.load(uploaded_file)
                    
                    # Show preview
                    st.markdown("**🔍 Tool Preview:**")
                    st.text(f"Name: {import_data['name']}")
                    st.text(f"Category: {import_data['category']}")
                    st.text(f"Language: {import_data['language']}")
                    st.caption(import_data['description'])
                    
                    if st.button("📥 Import Tool"):
                        result = st.session_state.tools_manager.import_tool(import_data)
                        st.success(f"✅ Tool '{result['name']}' imported successfully!")
                        st.rerun()
                
                except Exception as e:
                    st.error(f"❌ Invalid tool file: {e}")

def render_agent_control():
    """Render the multi-agent control interface"""
    st.title("🤖 Multi-Agent Control Center")
    st.markdown("**Orchestrate specialized AI agents for complex tasks**")
    
    # Initialize orchestrator
    workspace_root = os.path.expanduser("~/gringo_workspace")
    if 'orchestrator' not in st.session_state:
        st.session_state.orchestrator = MultiAgentOrchestrator(workspace_root)
        
        # Register all available agents
        agent_configs = {
            "planner": ("agents/planner_agent.py", "Task planning and breakdown"),
            "refactor": ("agents/refactor_agent.py", "Code refactoring and optimization"),
            "test_gen": ("agents/test_generator_agent.py", "Automated test generation"),
            "doc_gen": ("agents/doc_generator_agent.py", "Documentation generation"),
            "reviewer": ("agents/review_agent.py", "Code review and quality check"),
            "security": ("agents/security_agent.py", "Security analysis and hardening"),
            "performance": ("agents/performance_agent.py", "Performance optimization"),
            "api": ("agents/api_agent.py", "API development and testing"),
            "deploy": ("agents/deploy_agent.py", "Deployment and DevOps"),
            "analytics": ("agents/analytics_agent.py", "Data analysis and metrics")
        }
        
        for name, (script, description) in agent_configs.items():
            st.session_state.orchestrator.register_agent(name, script, description)
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎼 Orchestrate Agents",
        "🚀 Feature Pipeline", 
        "📊 Agent Status",
        "📋 Execution History"
    ])
    
    with tab1:
        st.subheader("🎼 Parallel Agent Orchestration")
        
        # Available agents
        available_agents = list(st.session_state.orchestrator.agents.keys())
        
        st.markdown("**🤖 Available Agents:**")
        for agent_name, agent_info in st.session_state.orchestrator.agents.items():
            status = "🟢 Active" if agent_info["active"] else "🔴 Inactive"
            st.text(f"{status} {agent_name}: {agent_info['description']}")
        
        st.markdown("---")
        
        # Agent task configuration
        st.markdown("**⚙️ Configure Agent Tasks:**")
        
        num_agents = st.slider("Number of agents to run:", 1, min(5, len(available_agents)), 3)
        
        tasks = []
        for i in range(num_agents):
            col1, col2 = st.columns([1, 2])
            
            with col1:
                selected_agent = st.selectbox(
                    f"Agent {i+1}:",
                    available_agents,
                    key=f"agent_select_{i}"
                )
            
            with col2:
                task_config = st.text_area(
                    f"Task config (JSON):",
                    value='{"target": "code_quality", "focus": "performance"}',
                    height=60,
                    key=f"task_config_{i}"
                )
            
            if selected_agent and task_config:
                try:
                    import json
                    task_data = json.loads(task_config)
                    tasks.append({"agent": selected_agent, "data": task_data})
                except:
                    st.error(f"❌ Invalid JSON in Agent {i+1} config")
        
        # Run orchestration
        if st.button("🚀 Run Parallel Orchestration", type="primary"):
            if tasks:
                with st.spinner("🤖 Orchestrating agents..."):
                    results = st.session_state.orchestrator.orchestrate_parallel(tasks)
                    
                    # Display results
                    st.success(f"✅ Orchestration completed! {len(results)} agents finished.")
                    
                    for result in results:
                        with st.expander(f"🤖 {result.agent_name} - {'✅ Success' if result.success else '❌ Failed'}"):
                            st.text(f"Status: {'Success' if result.success else 'Failed'}")
                            st.text(f"Timestamp: {result.timestamp}")
                            if result.output:
                                st.code(result.output)
                            if result.artifacts:
                                st.text(f"Artifacts: {', '.join(result.artifacts)}")
            else:
                st.error("❌ Please configure at least one valid agent task")
    
    with tab2:
        st.subheader("🚀 Feature Development Pipeline")
        st.markdown("**Complete feature pipeline: Plan → Code → Test → Doc → Review**")
        
        # Feature request input
        feature_request = st.text_area(
            "Describe the feature you want to develop:",
            placeholder="Add user authentication with JWT tokens and role-based access control",
            height=100
        )
        
        # Pipeline configuration
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Pipeline Stages:**")
            st.text("1. 🧠 Planning Agent - Break down requirements")
            st.text("2. 🔧 Refactor Agent - Code quality improvements")
            st.text("3. 🧪 Test Agent - Generate comprehensive tests")
            st.text("4. 📖 Doc Agent - Create documentation")
            st.text("5. 👥 Review Agent - Quality assurance")
        
        with col2:
            st.markdown("**Pipeline Settings:**")
            parallel_execution = st.checkbox("Parallel execution where possible", value=True)
            include_security = st.checkbox("Include security analysis", value=True)
            include_performance = st.checkbox("Include performance optimization", value=True)
        
        # Run pipeline
        if st.button("🚀 Run Feature Pipeline", type="primary"):
            if feature_request:
                with st.spinner("🏭 Running complete feature pipeline..."):
                    
                    # Show pipeline progress
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    # Phase 1: Planning
                    status_text.text("🧠 Phase 1: Planning and analysis...")
                    progress_bar.progress(20)
                    
                    # Phase 2: Implementation 
                    status_text.text("🔧 Phase 2: Code generation and refactoring...")
                    progress_bar.progress(40)
                    
                    # Phase 3: Testing
                    status_text.text("🧪 Phase 3: Test generation...")
                    progress_bar.progress(60)
                    
                    # Phase 4: Documentation
                    status_text.text("📖 Phase 4: Documentation generation...")
                    progress_bar.progress(80)
                    
                    # Phase 5: Review
                    status_text.text("👥 Phase 5: Quality review...")
                    progress_bar.progress(100)
                    
                    # Run the actual pipeline
                    success = st.session_state.orchestrator.run_feature_pipeline(feature_request)
                    
                    if success:
                        st.success("🎉 Feature pipeline completed successfully!")
                        status_text.text("✅ Pipeline completed successfully!")
                    else:
                        st.warning("⚠️ Pipeline completed with issues - check individual agent outputs")
                        status_text.text("⚠️ Pipeline completed with issues")
                    
                    # Show summary
                    summary = st.session_state.orchestrator.get_summary()
                    
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Total Agents", summary["total_agents"])
                    col2.metric("Successful", summary["successful"])
                    col3.metric("Success Rate", f"{summary['success_rate']:.1f}%")
            else:
                st.error("❌ Please describe the feature you want to develop")
    
    with tab3:
        st.subheader("📊 Agent Status Dashboard")
        
        # Agent health check
        if st.button("🔄 Refresh Agent Status"):
            st.rerun()
        
        # Display agent status
        st.markdown("**🤖 Registered Agents:**")
        
        for agent_name, agent_info in st.session_state.orchestrator.agents.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                status_emoji = "🟢" if agent_info["active"] else "🔴"
                st.markdown(f"**{status_emoji} {agent_name}**")
                st.caption(agent_info["description"])
            
            with col2:
                st.text("Active" if agent_info["active"] else "Inactive")
                st.caption(f"Script: {agent_info['script']}")
            
            with col3:
                if st.button("🧪 Test", key=f"test_{agent_name}"):
                    test_data = {"test": True, "agent": agent_name}
                    result = st.session_state.orchestrator.spawn_agent(agent_name, test_data)
                    if result.success:
                        st.success(f"✅ {agent_name} test passed")
                    else:
                        st.error(f"❌ {agent_name} test failed")
        
        # System resources
        st.markdown("---")
        st.markdown("**🖥️ System Resources:**")
        
        try:
            import psutil
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("CPU Usage", f"{cpu_percent}%")
            col2.metric("Memory Usage", f"{memory.percent}%")
            col3.metric("Available Memory", f"{memory.available // (1024**3)} GB")
        except ImportError:
            st.info("Install psutil for system monitoring: `pip install psutil`")
    
    with tab4:
        st.subheader("📋 Execution History")
        
        # Execution summary
        if st.session_state.orchestrator.results:
            summary = st.session_state.orchestrator.get_summary()
            
            st.markdown("**📊 Overall Statistics:**")
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Executions", summary["total_agents"])
            col2.metric("Successful", summary["successful"])
            col3.metric("Failed", summary["failed"])
            col4.metric("Success Rate", f"{summary['success_rate']:.1f}%")
            
            # Recent executions
            st.markdown("**🕒 Recent Executions:**")
            
            for result in reversed(st.session_state.orchestrator.results[-10:]):  # Last 10
                with st.expander(f"{'✅' if result.success else '❌'} {result.agent_name} - {result.timestamp[:19]}"):
                    st.text(f"Agent: {result.agent_name}")
                    st.text(f"Status: {'Success' if result.success else 'Failed'}")
                    st.text(f"Timestamp: {result.timestamp}")
                    
                    if result.output:
                        st.markdown("**Output:**")
                        st.code(result.output[:500] + "..." if len(result.output) > 500 else result.output)
                    
                    if result.artifacts:
                        st.markdown("**Artifacts:**")
                        for artifact in result.artifacts:
                            st.text(f"📄 {artifact}")
            
            # Clear history
            if st.button("🗑️ Clear History"):
                st.session_state.orchestrator.results = []
                st.success("✅ Execution history cleared")
                st.rerun()
        
        else:
            st.info("No execution history yet. Run some agents to see results here!")

def render_documentation():
    """Render the documentation interface"""
    st.title("📖 GRINGO Documentation")
    st.markdown("**Complete guide to your personal development OS**")
    
    # Documentation tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "📋 Quick Start",
        "🚀 Features Guide", 
        "🛠️ Advanced Usage",
        "💡 Tips & Tricks"
    ])
    
    with tab1:
        st.markdown("""
# 🚀 Quick Start Guide

## Getting Started in 3 Steps

### 1. 🎯 Create Your First Project
- Go to **"💬 Create from Prompt"** tab
- Try: `"Create a simple calculator with a web interface"`
- Click **"🚀 Create Project"**
- Click **"▶️ Run Project"** to test

### 2. 🛠️ Build Custom Tools
- Go to **"🛠️ Custom Tools"** section
- Use templates or write custom code
- Save tools for future use
- Run tools with different arguments

### 3. 🤖 Chat with AI
- Go to **"🤖 AI Chat"** section
- Ask LLaMA for project advice
- Get code reviews and suggestions
- Plan complex applications

## 💡 Example Prompts That Work

```
"Create a file organization script that sorts files by type"
"Build a 2D platformer game with Pygame"
"Make a data analysis tool for CSV files with charts"
"Create a web scraper for news articles"
"Build a password generator with different complexity levels"
```

## 🎯 Pro Tips
- Be specific in your prompts
- Use the templates in Custom Tools
- Export your favorite tools for backup
- Chat with AI for complex planning
""")
    
    with tab2:
        st.markdown("""
# 🚀 Complete Features Guide

## 💬 Project Creator
**Transform ideas into working code instantly**

### Supported Project Types:
- **🌐 Web Apps** - Streamlit, HTML/CSS/JS interfaces
- **🔧 APIs** - Flask, FastAPI backend services  
- **📊 Data Science** - Pandas, Matplotlib analysis tools
- **🎮 Games** - Pygame 2D games and simulations
- **🤖 Automation** - File processing, web scraping
- **⚙️ Utilities** - Calculators, converters, system tools

### What You Get:
- ✅ Complete project structure (`src/`, `tests/`)
- ✅ Working `main.py` with functional code
- ✅ `requirements.txt` with dependencies
- ✅ `README.md` with documentation
- ✅ `run.py` for easy execution

## 🛠️ Custom Tools Manager
**Build your personal toolkit**

### Tool Categories:
- **📁 File Operations** - File management, organization
- **📝 Text Processing** - Text analysis, conversion
- **📊 Data Analysis** - CSV processing, statistics
- **🖥️ System Utilities** - Monitoring, maintenance
- **🌐 Web Tools** - Scraping, API testing
- **🤖 Automation** - Task scheduling, workflows

### Features:
- Create tools in Python, JavaScript, Bash
- Save and organize by category
- Export/import for sharing
- Run with custom arguments
- Usage tracking and statistics

## 📁 File Management
**Complete project lifecycle**

- Upload existing code files
- Convert uploads to full projects
- Organize by project type
- Export projects as packages
- Database-backed project tracking

## 🤖 AI Integration
**Local LLaMA assistance**

- Code review and optimization
- Project architecture planning
- Debugging assistance
- Best practices guidance
- Technology recommendations
""")
    
    with tab3:
        st.markdown("""
# 🛠️ Advanced Usage Guide

## 🏗️ Project Architecture

### Generated Structure:
```
project_name/
├── main.py          # Main application code
├── run.py           # Execution script
├── requirements.txt # Dependencies
├── README.md        # Documentation
├── src/            # Source code modules
└── tests/          # Test files
```

## 🔧 Custom Tool Development

### Python Tool Template:
```python
#!/usr/bin/env python3
import sys

def main():
    # Your tool logic here
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        # Process file
    
if __name__ == "__main__":
    main()
```

### JavaScript Tool Template:
```javascript
#!/usr/bin/env node
const fs = require('fs');

function main() {
    const args = process.argv.slice(2);
    // Your tool logic here
}

main();
```

## 🗄️ Database Integration

### Project Storage:
- SQLite database for metadata
- Full project history tracking
- Search and filter capabilities
- Backup and restore functions

### Custom Tools Database:
- JSON-based tool registry
- Usage statistics tracking
- Category organization
- Import/export functionality

## 🚀 Performance Optimization

### Best Practices:
- Regular cleanup of test projects
- Monitor workspace disk usage
- Use AI chat for code optimization
- Export important tools for backup

### System Requirements:
- Python 3.8+ recommended
- 4GB RAM minimum
- 1GB disk space for workspace
- Ollama for AI features
""")
    
    with tab4:
        st.markdown("""
# 💡 Tips & Tricks

## 🎯 Effective Project Prompts

### Be Specific:
❌ "Create a web app"
✅ "Create a task manager web app with categories and due dates"

### Include Technology:
❌ "Make a game"
✅ "Make a 2D platformer game with Pygame and level progression"

### Specify Features:
❌ "Build a data tool"
✅ "Build a CSV analyzer with charts, filtering, and export options"

## 🛠️ Tool Development Tips

### Modular Design:
- Keep tools focused on single tasks
- Use clear argument schemas
- Include error handling
- Add usage examples in comments

### Code Organization:
```python
# Good tool structure
def main_function(args):
    # Core logic here
    pass

def validate_inputs(args):
    # Input validation
    pass

if __name__ == "__main__":
    import sys
    args = sys.argv[1:]
    validate_inputs(args)
    main_function(args)
```

## 🤖 AI Chat Best Practices

### Effective Questions:
- "Review this code for performance issues"
- "Help me plan a machine learning project architecture"
- "What's the best way to structure a Flask API?"
- "Suggest improvements for this data processing script"

### Code Review Process:
1. Paste your code in chat
2. Ask specific questions
3. Implement suggested improvements
4. Test and iterate

## 📊 Project Management

### Organization Tips:
- Use descriptive project names
- Keep project descriptions updated
- Regular backup of workspace
- Delete unused test projects

### Backup Strategy:
1. Export important tools regularly
2. Use version control for complex projects
3. Create workspace backups weekly
4. Document custom modifications

## 🔧 Troubleshooting

### Common Issues:

**Import Errors:**
```bash
pip install missing_package
```

**AI Chat Not Working:**
```bash
ollama serve
ollama pull llama3
```

**Project Won't Run:**
1. Check `requirements.txt`
2. Install dependencies
3. Verify Python version
4. Check file permissions

### Debug Mode:
- Use terminal for detailed error messages
- Check project logs in dashboard
- Verify all dependencies installed
- Test tools individually

## 🚀 Workflow Optimization

### Daily Development:
1. Start with AI planning session
2. Create project from prompt
3. Build supporting tools as needed
4. Test and iterate quickly
5. Export successful patterns

### Tool Building Workflow:
1. Identify repetitive tasks
2. Create focused tools
3. Test with different inputs
4. Share useful tools via export
5. Build tool library over time
""")
    
    # Download documentation
    if st.button("📥 Download Complete Documentation"):
        try:
            with open("GRINGO_DOCUMENTATION.md", "r") as f:
                doc_content = f.read()
            
            st.download_button(
                label="💾 Download Documentation",
                data=doc_content,
                file_name="GRINGO_Complete_Documentation.md",
                mime="text/markdown"
            )
        except FileNotFoundError:
            st.error("❌ Documentation file not found")

def main():
    """Main application"""
    
    # Sidebar
    st.sidebar.title("🤖 GRINGO Personal OS")
    st.sidebar.markdown("**Full Project Creator**")
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate:",
        ["🚀 Project Creator", "�️ Custom Tools", "📖 Documentation", "�💻 Terminal", "🤖 AI Chat", "📊 Dashboard"]
    )
    
    # Show system info
    st.sidebar.markdown("---")
    st.sidebar.markdown("**System Info:**")
    workspace_root = os.path.expanduser("~/gringo_workspace")
    st.sidebar.text(f"Workspace: {workspace_root}")
    
    if 'project_manager' in st.session_state:
        projects = st.session_state.project_manager.list_projects()
        st.sidebar.metric("Projects", len(projects))
    
    # Page routing
    if page == "🚀 Project Creator":
        render_project_creator()
    
    elif page == "�️ Custom Tools":
        render_custom_tools()
    
    elif page == "📖 Documentation":
        render_documentation()
    
    elif page == "�💻 Terminal":
        st.title("💻 Terminal")
        st.markdown("**In-browser command line interface**")
        
        command = st.text_input("Command:", placeholder="ls, pwd, python --version")
        
        if st.button("Execute") and command:
            try:
                result = subprocess.run(
                    command, shell=True, capture_output=True, text=True, timeout=10
                )
                st.code(f"$ {command}\n{result.stdout}\n{result.stderr}")
            except Exception as e:
                st.error(f"Error: {e}")
    
    elif page == "🤖 AI Chat":
        st.title("🤖 AI Chat")
        st.markdown("**Chat with your local AI assistant**")
        
        user_input = st.text_area("Message:", placeholder="Ask me anything about your projects...")
        
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
    
    elif page == "📊 Dashboard":
        st.title("📊 Dashboard")
        st.markdown("**System Overview**")
        
        workspace_root = os.path.expanduser("~/gringo_workspace")
        
        # System metrics
        col1, col2, col3 = st.columns(3)
        
        if 'project_manager' in st.session_state:
            projects = st.session_state.project_manager.list_projects()
            col1.metric("📁 Projects", len(projects))
        else:
            col1.metric("📁 Projects", 0)
        
        col2.metric("💾 Workspace", workspace_root.split('/')[-1])
        col3.metric("🟢 Status", "Running")
        
        # Recent activity
        if 'project_manager' in st.session_state:
            projects = st.session_state.project_manager.list_projects()
            if projects:
                st.markdown("**📋 Recent Projects:**")
                for project in projects[-3:]:
                    with st.expander(f"📁 {project['name']}"):
                        st.text(f"Type: {project['type']}")
                        st.text(f"Created: {project['created_at']}")
                        st.caption(project['description'][:150] + "..." if len(project['description']) > 150 else project['description'])
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("🔒 **100% Local & Private**")
    st.sidebar.markdown("No data leaves your machine")

if __name__ == "__main__":
    main()
