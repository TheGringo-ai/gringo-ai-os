#!/usr/bin/env python3
"""
GRINGO Ultimate Project Creator with Multi-Agent Control
Complete development dashboard with agent orchestration
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
    page_title="🤖 GRINGO AI OS - Ultimate Development Environment",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for GRINGO branding
st.markdown("""
<style>
    .gringo-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
        padding: 1rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        border: 2px solid #06b6d4;
        box-shadow: 0 0 20px rgba(6, 182, 212, 0.3);
    }
    .gringo-logo {
        font-size: 3rem;
        font-weight: bold;
        background: linear-gradient(45deg, #06b6d4, #3b82f6, #8b5cf6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-align: center;
        margin-bottom: 0.5rem;
        text-shadow: 0 0 10px rgba(6, 182, 212, 0.5);
    }
    .gringo-tagline {
        color: #06b6d4;
        text-align: center;
        font-size: 1.2rem;
        font-weight: 500;
        margin-bottom: 1rem;
    }
    .gringo-subtitle {
        color: #e2e8f0;
        text-align: center;
        font-size: 1rem;
        opacity: 0.9;
    }
    .feature-card {
        background: rgba(6, 182, 212, 0.1);
        border: 1px solid #06b6d4;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    .stButton > button {
        background: linear-gradient(45deg, #06b6d4, #3b82f6);
        border: none;
        border-radius: 8px;
        color: white;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        box-shadow: 0 0 15px rgba(6, 182, 212, 0.5);
        transform: translateY(-2px);
    }
</style>
""", unsafe_allow_html=True)

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
    
    def learn_from_files(self, uploaded_files, learn_prompt: str, project_name: str = None) -> dict:
        """Learn from uploaded files to create similar projects"""
        if not project_name:
            project_name = f"learned_project_{datetime.now().strftime('%m%d_%H%M')}"
        
        project_path = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Save uploaded files
        file_info = []
        for uploaded_file in uploaded_files:
            file_path = os.path.join(project_path, uploaded_file.name)
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            file_info.append({
                'name': uploaded_file.name,
                'size': len(uploaded_file.getbuffer()),
                'type': uploaded_file.type
            })
        
        # Analyze files with AI (if available)
        analysis = self._analyze_uploaded_files(project_path, learn_prompt)
        
        # Store learning data
        learning_data = {
            'project_name': project_name,
            'files': file_info,
            'analysis': analysis,
            'learn_prompt': learn_prompt,
            'created_at': datetime.now().isoformat()
        }
        
        # Save to database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, path, type, status, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_name, project_path, 'learning', 'analyzed', 
              datetime.now().isoformat(), json.dumps(learning_data)))
        conn.commit()
        conn.close()
        
        return {
            'name': project_name,
            'path': project_path,
            'analysis': analysis,
            'files_count': len(file_info)
        }
    
    def _analyze_uploaded_files(self, project_path: str, prompt: str) -> dict:
        """Analyze uploaded files to understand patterns and structure"""
        analysis = {
            'file_types': {},
            'structure': [],
            'patterns': [],
            'suggestions': []
        }
        
        try:
            # Analyze file structure
            for root, dirs, files in os.walk(project_path):
                rel_root = os.path.relpath(root, project_path)
                for file in files:
                    ext = os.path.splitext(file)[1]
                    analysis['file_types'][ext] = analysis['file_types'].get(ext, 0) + 1
                    analysis['structure'].append(os.path.join(rel_root, file))
            
            # Basic pattern detection
            if '.py' in analysis['file_types']:
                analysis['patterns'].append('Python project')
            if '.js' in analysis['file_types']:
                analysis['patterns'].append('JavaScript project')
            if '.html' in analysis['file_types']:
                analysis['patterns'].append('Web project')
            
            # Generate suggestions based on analysis
            analysis['suggestions'] = [
                f"Found {sum(analysis['file_types'].values())} files",
                f"Primary language: {self._detect_primary_language(analysis['file_types'])}",
                "Can create similar project with improvements"
            ]
            
        except Exception as e:
            analysis['error'] = str(e)
        
        return analysis
    
    def _detect_primary_language(self, file_types: dict) -> str:
        """Detect primary programming language"""
        lang_map = {
            '.py': 'Python',
            '.js': 'JavaScript', 
            '.html': 'HTML',
            '.css': 'CSS',
            '.java': 'Java',
            '.cpp': 'C++',
            '.c': 'C'
        }
        
        max_count = 0
        primary_lang = 'Unknown'
        
        for ext, count in file_types.items():
            if ext in lang_map and count > max_count:
                max_count = count
                primary_lang = lang_map[ext]
        
        return primary_lang
    
    def apply_learning(self, learning_project: str, enhancement_prompt: str) -> dict:
        """Apply learning from analyzed project to create enhanced version"""
        enhanced_name = f"enhanced_{learning_project}_{datetime.now().strftime('%H%M')}"
        
        # Get learning data
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT metadata FROM projects WHERE name = ?', (learning_project,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError(f"Learning project {learning_project} not found")
        
        learning_data = json.loads(result[0])
        
        # Create enhanced project using learning insights
        combined_prompt = f"""
        Based on analysis of uploaded project:
        - File types: {learning_data['analysis'].get('file_types', {})}
        - Patterns: {learning_data['analysis'].get('patterns', [])}
        - Structure: {len(learning_data['analysis'].get('structure', []))} files
        
        Enhancement request: {enhancement_prompt}
        
        Create an improved version incorporating best practices and requested enhancements.
        """
        
        return self.create_project_from_prompt(combined_prompt, enhanced_name)
    
    def link_external_folder(self, folder_path: str, project_name: str, copy_mode: bool = True) -> dict:
        """Link or copy external folder as a project"""
        if not os.path.exists(folder_path):
            raise ValueError(f"Folder {folder_path} does not exist")
        
        project_path = os.path.join(self.projects_dir, project_name)
        
        if copy_mode:
            # Copy folder to workspace
            if os.path.exists(project_path):
                shutil.rmtree(project_path)
            shutil.copytree(folder_path, project_path)
            status = 'copied'
        else:
            # Create symlink (work in place)
            if os.path.exists(project_path):
                os.remove(project_path)
            os.symlink(folder_path, project_path)
            status = 'linked'
        
        # Analyze linked folder
        analysis = self._analyze_uploaded_files(project_path, f"Analyze linked folder: {folder_path}")
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO projects (name, path, type, status, created_at, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (project_name, project_path, 'linked', status,
              datetime.now().isoformat(), json.dumps({
                  'original_path': folder_path,
                  'copy_mode': copy_mode,
                  'analysis': analysis
              })))
        conn.commit()
        conn.close()
        
        return {
            'name': project_name,
            'path': project_path,
            'status': status,
            'analysis': analysis
        }
    
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
        
        # main.py with basic template based on type
        main_content = f'''#!/usr/bin/env python3
"""
{prompt}
"""

def main():
    """Main application function"""
    print("🚀 Project: {project_info.get('suggested_name', 'New Project')}")
    print("📝 Description: {prompt[:100]}...")
    
    # TODO: Implement your project logic here
    print("\\n✅ Project template ready!")

if __name__ == "__main__":
    main()
'''
        
        with open(os.path.join(project_path, 'main.py'), 'w') as f:
            f.write(main_content)
        files.append('🐍 main.py')
        
        # requirements.txt
        requirements = ['requests']  # Basic requirements
        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write('\n'.join(requirements))
        files.append('📦 requirements.txt')
        
        # README.md
        readme_content = f'''# {project_info.get('suggested_name', 'New Project')}

{prompt}

## Usage
```bash
python main.py
```

---
*Generated by GRINGO Personal OS*
'''
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        files.append('📖 README.md')
        
        return files
    
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
        main_file = os.path.join(project_path, 'main.py')
        
        if os.path.exists(main_file):
            try:
                result = subprocess.run(
                    ['python', 'main.py'],
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
                
            except Exception as e:
                return {"error": f"Failed to run: {e}"}
        
        return {"error": "No runnable file found"}

def render_project_creator():
    """Render the project creation interface with folder learning"""
    st.title("🚀 AI Project Creator")
    st.markdown("**Describe any project and AI will build it for you - or learn from existing folders**")
    
    # Initialize project manager
    workspace_root = os.path.expanduser("~/gringo_workspace")
    if 'project_manager' not in st.session_state:
        st.session_state.project_manager = FullProjectManager(workspace_root)
    
    # Tab layout for different creation modes
    tab1, tab2, tab3 = st.tabs(["🆕 Create New", "📁 Learn from Folder", "🔗 Link Existing"])
    
    with tab1:
        st.subheader("Create from Description")
        prompt = st.text_area(
            "Describe what you want to build:",
            placeholder="Create a simple calculator with a web interface using Streamlit",
            height=100
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            project_name = st.text_input("Project name (optional):")
        with col2:
            auto_run = st.checkbox("Auto-run after creation", value=False)
        
        if st.button("🚀 Create Project", type="primary") and prompt:
            with st.spinner("🤖 Creating your project..."):
                try:
                    result = st.session_state.project_manager.create_project_from_prompt(
                        prompt, project_name if project_name else None
                    )
                    
                    st.success(f"✅ Project '{result['name']}' created successfully!")
                    st.info(f"📂 Location: {result['path']}")
                    
                    if auto_run:
                        run_result = st.session_state.project_manager.run_project(result['name'])
                        if run_result.get('success'):
                            st.success("✅ Auto-run completed!")
                            st.code(run_result['output'])
                    
                except Exception as e:
                    st.error(f"❌ Failed to create project: {e}")
    
    with tab2:
        st.subheader("Learn from Existing Folder")
        st.markdown("Upload a folder and AI will analyze it, learn patterns, and help build similar projects")
        
        uploaded_files = st.file_uploader(
            "Upload project files or folder",
            accept_multiple_files=True,
            help="Upload files from an existing project for AI to learn from"
        )
        
        if uploaded_files:
            learn_prompt = st.text_area(
                "What should AI learn from these files?",
                placeholder="Analyze this codebase and help me build a similar project with better architecture",
                height=80
            )
            
            col1, col2 = st.columns(2)
            with col1:
                learn_name = st.text_input("Learning project name:", placeholder="learned_project")
            with col2:
                apply_learning = st.checkbox("Apply learning to new project", value=True)
            
            if st.button("🧠 Learn & Create", type="primary") and learn_prompt:
                with st.spinner("🧠 AI is analyzing and learning..."):
                    try:
                        # Create learning project from uploaded files
                        result = st.session_state.project_manager.learn_from_files(
                            uploaded_files, learn_prompt, learn_name
                        )
                        
                        st.success(f"✅ AI learned from {len(uploaded_files)} files!")
                        st.info(f"📂 Learning project: {result['name']}")
                        
                        if apply_learning:
                            # Apply learning to create enhanced project
                            enhanced_result = st.session_state.project_manager.apply_learning(
                                result['name'], learn_prompt
                            )
                            st.success(f"✅ Enhanced project created: {enhanced_result['name']}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to learn from files: {e}")
    
    with tab3:
        st.subheader("Link External Folder")
        st.markdown("Connect an existing folder on your system to work with AI agents")
        
        folder_path = st.text_input(
            "Folder path to link:",
            placeholder="/path/to/your/project/folder",
            help="Enter the full path to a folder you want to work with"
        )
        
        if folder_path and os.path.exists(folder_path):
            st.success(f"✅ Found folder: {folder_path}")
            
            col1, col2 = st.columns(2)
            with col1:
                link_name = st.text_input("Project name:", placeholder="linked_project")
            with col2:
                copy_mode = st.selectbox("Link mode:", ["Copy to workspace", "Work in place"])
            
            if st.button("🔗 Link Folder", type="primary") and link_name:
                with st.spinner("🔗 Linking folder..."):
                    try:
                        result = st.session_state.project_manager.link_external_folder(
                            folder_path, link_name, copy_mode == "Copy to workspace"
                        )
                        
                        st.success(f"✅ Folder linked as project: {result['name']}")
                        st.info(f"📂 Location: {result['path']}")
                        
                    except Exception as e:
                        st.error(f"❌ Failed to link folder: {e}")
        
        elif folder_path:
            st.error("❌ Folder not found. Please check the path.")

def render_agent_control():
    """Render the multi-agent control interface with project awareness"""
    st.title("🤖 Multi-Agent Control Center")
    st.markdown("**Orchestrate specialized AI agents for complex tasks and project analysis**")
    
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
            "reviewer": ("agents/review_agent.py", "Code review and quality analysis"),
            "security": ("agents/security_agent.py", "Security analysis and hardening"),
            "performance": ("agents/performance_agent.py", "Performance optimization"),
            "api": ("agents/api_agent.py", "API development and testing"),
            "deploy": ("agents/deploy_agent.py", "Deployment and DevOps"),
            "analytics": ("agents/analytics_agent.py", "Data analysis and insights")
        }
        
        for agent_id, (path, desc) in agent_configs.items():
            st.session_state.orchestrator.register_agent(agent_id, path, desc)
    
    # Project-aware agent control
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Quick Actions", "🔄 Agent Pipelines", "📁 Project Analysis", "📊 Agent Status"])
    
    with tab1:
        st.subheader("AI Agent Quick Actions")
        
        # Get available projects
        projects = get_available_projects(workspace_root)
        
        col1, col2 = st.columns(2)
        with col1:
            selected_project = st.selectbox(
                "Target Project (optional):",
                ["All Projects"] + projects,
                help="Choose a specific project or work globally"
            )
        
        with col2:
            action_type = st.selectbox(
                "Quick Action:",
                [
                    "Analyze & Summarize",
                    "Code Review",
                    "Generate Tests",
                    "Refactor Code",
                    "Security Audit",
                    "Performance Check",
                    "Generate Docs",
                    "Plan Improvements"
                ]
            )
        
        task_description = st.text_area(
            "Describe the task:",
            placeholder="Review the authentication module and suggest improvements",
            height=100
        )
        
        if st.button("🚀 Run Quick Action", type="primary") and task_description:
            with st.spinner(f"🤖 Running {action_type}..."):
                try:
                    # Map action to appropriate agent
                    agent_mapping = {
                        "Analyze & Summarize": "analytics",
                        "Code Review": "reviewer", 
                        "Generate Tests": "test_gen",
                        "Refactor Code": "refactor",
                        "Security Audit": "security",
                        "Performance Check": "performance",
                        "Generate Docs": "doc_gen",
                        "Plan Improvements": "planner"
                    }
                    
                    agent_id = agent_mapping.get(action_type, "planner")
                    
                    # Add project context if selected
                    context = task_description
                    if selected_project != "All Projects":
                        context = f"Project: {selected_project}\nTask: {task_description}"
                    
                    result = st.session_state.orchestrator.run_single_agent(agent_id, context)
                    
                    st.success(f"✅ {action_type} completed!")
                    st.markdown("### Results:")
                    st.markdown(result.output)
                    
                    if result.files_created:
                        st.info(f"📁 Files created: {', '.join(result.files_created)}")
                    
                except Exception as e:
                    st.error(f"❌ Action failed: {e}")
    
    with tab2:
        st.subheader("Multi-Agent Workflows")
        
        # Predefined pipelines
        col1, col2 = st.columns(2)
        with col1:
            pipeline_type = st.selectbox(
                "Workflow Type:",
                [
                    "Full Development Cycle",
                    "Code Quality Audit", 
                    "Security Hardening",
                    "Performance Optimization",
                    "Documentation Suite",
                    "Custom Pipeline"
                ]
            )
        
        with col2:
            target_project = st.selectbox(
                "Target Project:",
                ["Select Project"] + projects,
                help="Choose which project to process"
            )
        
        pipeline_description = st.text_area(
            "Pipeline Description:",
            placeholder="Add user authentication, review security, generate tests, and create documentation",
            height=100
        )
        
        # Show pipeline preview
        if pipeline_type != "Custom Pipeline":
            pipeline_agents = get_pipeline_agents(pipeline_type)
            st.info(f"🔄 Pipeline: {' → '.join(pipeline_agents)}")
        
        if st.button("⚡ Run Pipeline", type="primary") and pipeline_description and target_project != "Select Project":
            with st.spinner("🔄 Running multi-agent pipeline..."):
                try:
                    # Add project context
                    context = f"Project: {target_project}\nObjective: {pipeline_description}"
                    
                    if pipeline_type == "Custom Pipeline":
                        # Let AI decide which agents to use
                        results = st.session_state.orchestrator.run_intelligent_pipeline(context)
                    else:
                        # Use predefined pipeline
                        agent_sequence = get_pipeline_agents(pipeline_type)
                        results = st.session_state.orchestrator.run_agent_pipeline(agent_sequence, context)
                    
                    st.success(f"✅ Pipeline completed! Ran {len(results)} agents")
                    
                    # Show results
                    for i, result in enumerate(results):
                        with st.expander(f"Agent {i+1}: {result.agent_id}"):
                            st.markdown(result.output)
                            if result.files_created:
                                st.info(f"Files created: {', '.join(result.files_created)}")
                    
                except Exception as e:
                    st.error(f"❌ Pipeline failed: {e}")
    
    with tab3:
        st.subheader("Project Deep Analysis")
        
        if projects:
            analysis_project = st.selectbox("Project to Analyze:", projects)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📊 Full Analysis"):
                    analyze_project_full(analysis_project, workspace_root)
            
            with col2:
                if st.button("🔍 Code Quality"):
                    analyze_project_quality(analysis_project, workspace_root)
            
            with col3:
                if st.button("🚀 Optimization"):
                    analyze_project_optimization(analysis_project, workspace_root)
        
        else:
            st.info("📁 No projects found. Create or link a project first.")
    
    with tab4:
        st.subheader("Agent Health & Performance")
        
        # Agent status monitoring
        agents = st.session_state.orchestrator.get_registered_agents()
        
        for agent_id, agent_info in agents.items():
            with st.expander(f"🤖 {agent_id.title()} Agent"):
                col1, col2 = st.columns(2)
                with col1:
                    st.write(f"**Description:** {agent_info['description']}")
                    st.write(f"**Status:** {'✅ Ready' if agent_info['healthy'] else '❌ Error'}")
                
                with col2:
                    if st.button(f"Test {agent_id}", key=f"test_{agent_id}"):
                        test_agent(agent_id)

def get_available_projects(workspace_root):
    """Get list of available projects"""
    projects_dir = os.path.join(workspace_root, "projects")
    if not os.path.exists(projects_dir):
        return []
    
    return [d for d in os.listdir(projects_dir) 
            if os.path.isdir(os.path.join(projects_dir, d))]

def get_pipeline_agents(pipeline_type):
    """Get agent sequence for predefined pipelines"""
    pipelines = {
        "Full Development Cycle": ["planner", "refactor", "test_gen", "security", "doc_gen", "deploy"],
        "Code Quality Audit": ["reviewer", "refactor", "test_gen", "performance"],
        "Security Hardening": ["security", "reviewer", "test_gen", "doc_gen"], 
        "Performance Optimization": ["performance", "refactor", "test_gen", "analytics"],
        "Documentation Suite": ["analytics", "doc_gen", "reviewer"]
    }
    return pipelines.get(pipeline_type, ["planner"])

def analyze_project_full(project_name, workspace_root):
    """Run comprehensive project analysis"""
    with st.spinner("🔍 Running full project analysis..."):
        try:
            orchestrator = st.session_state.orchestrator
            context = f"Analyze project '{project_name}' comprehensively - architecture, code quality, security, performance, and documentation"
            
            agents = ["analytics", "reviewer", "security", "performance", "doc_gen"]
            results = orchestrator.run_agent_pipeline(agents, context)
            
            st.success("✅ Full analysis completed!")
            
            # Display comprehensive results
            for result in results:
                with st.expander(f"📋 {result.agent_id.title()} Analysis"):
                    st.markdown(result.output)
            
        except Exception as e:
            st.error(f"❌ Analysis failed: {e}")

def analyze_project_quality(project_name, workspace_root):
    """Analyze code quality"""
    with st.spinner("🔍 Analyzing code quality..."):
        try:
            orchestrator = st.session_state.orchestrator
            context = f"Review code quality for project '{project_name}' - check for bugs, improvements, and best practices"
            
            result = orchestrator.run_single_agent("reviewer", context)
            
            st.success("✅ Quality analysis completed!")
            st.markdown("### Code Quality Report:")
            st.markdown(result.output)
            
        except Exception as e:
            st.error(f"❌ Quality analysis failed: {e}")

def analyze_project_optimization(project_name, workspace_root):
    """Analyze optimization opportunities"""
    with st.spinner("🚀 Finding optimization opportunities..."):
        try:
            orchestrator = st.session_state.orchestrator
            context = f"Find optimization opportunities for project '{project_name}' - performance, architecture, and efficiency improvements"
            
            agents = ["performance", "refactor", "planner"]
            results = orchestrator.run_agent_pipeline(agents, context)
            
            st.success("✅ Optimization analysis completed!")
            
            for result in results:
                with st.expander(f"⚡ {result.agent_id.title()} Recommendations"):
                    st.markdown(result.output)
            
        except Exception as e:
            st.error(f"❌ Optimization analysis failed: {e}")

def test_agent(agent_id):
    """Test individual agent"""
    with st.spinner(f"Testing {agent_id} agent..."):
        try:
            orchestrator = st.session_state.orchestrator
            result = orchestrator.run_single_agent(agent_id, "Health check test")
            
            st.success(f"✅ {agent_id} agent is working!")
            st.code(result.output[:200] + "..." if len(result.output) > 200 else result.output)
            
        except Exception as e:
            st.error(f"❌ {agent_id} agent test failed: {e}")
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
        
        # Quick agent tasks
        st.markdown("**⚡ Quick Agent Tasks:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("🧠 Plan New Feature"):
                feature_desc = st.text_input("Feature description:", key="quick_plan")
                if feature_desc:
                    task = {"agent": "planner", "data": {"request": feature_desc}}
                    result = st.session_state.orchestrator.spawn_agent("planner", task["data"])
                    st.write(result.output if result.success else result.output)
        
        with col2:
            if st.button("🔧 Code Review"):
                st.info("Select files to review in the file manager")
        
        with col3:
            if st.button("🧪 Generate Tests"):
                st.info("Automated test generation for current project")
        
        # Custom agent configuration
        st.markdown("**⚙️ Custom Agent Configuration:**")
        
        selected_agent = st.selectbox("Select Agent:", available_agents)
        task_config = st.text_area(
            "Task Configuration (JSON):",
            value='{"target": "code_quality", "focus": "performance"}',
            height=100
        )
        
        if st.button("🚀 Run Single Agent"):
            try:
                task_data = json.loads(task_config)
                result = st.session_state.orchestrator.spawn_agent(selected_agent, task_data)
                
                if result.success:
                    st.success(f"✅ {selected_agent} completed successfully!")
                    st.code(result.output)
                else:
                    st.error(f"❌ {selected_agent} failed: {result.output}")
                    
            except Exception as e:
                st.error(f"❌ Error: {e}")
    
    with tab2:
        st.subheader("🚀 Feature Development Pipeline")
        st.markdown("**Complete feature pipeline: Plan → Code → Test → Doc → Review**")
        
        feature_request = st.text_area(
            "Describe the feature you want to develop:",
            placeholder="Add user authentication with JWT tokens and role-based access control",
            height=100
        )
        
        if st.button("🚀 Run Feature Pipeline", type="primary"):
            if feature_request:
                with st.spinner("🏭 Running complete feature pipeline..."):
                    progress_bar = st.progress(0)
                    status_text = st.empty()
                    
                    status_text.text("🧠 Phase 1: Planning and analysis...")
                    progress_bar.progress(20)
                    
                    status_text.text("🔧 Phase 2: Implementation...")
                    progress_bar.progress(60)
                    
                    status_text.text("👥 Phase 3: Review and testing...")
                    progress_bar.progress(100)
                    
                    success = st.session_state.orchestrator.run_feature_pipeline(feature_request)
                    
                    if success:
                        st.success("🎉 Feature pipeline completed successfully!")
                    else:
                        st.warning("⚠️ Pipeline completed with issues")
    
    with tab3:
        st.subheader("📊 Agent Status Dashboard")
        
        for agent_name, agent_info in st.session_state.orchestrator.agents.items():
            col1, col2, col3 = st.columns([2, 1, 1])
            
            with col1:
                status_emoji = "🟢" if agent_info["active"] else "🔴"
                st.markdown(f"**{status_emoji} {agent_name}**")
                st.caption(agent_info["description"])
            
            with col2:
                st.text("Active" if agent_info["active"] else "Inactive")
            
            with col3:
                if st.button("🧪 Test", key=f"test_{agent_name}"):
                    test_data = {"test": True}
                    result = st.session_state.orchestrator.spawn_agent(agent_name, test_data)
                    st.success("✅ Test passed" if result.success else "❌ Test failed")
    
    with tab4:
        st.subheader("📋 Execution History")
        
        if st.session_state.orchestrator.results:
            summary = st.session_state.orchestrator.get_summary()
            
            col1, col2, col3 = st.columns(3)
            col1.metric("Total Executions", summary["total_agents"])
            col2.metric("Successful", summary["successful"])
            col3.metric("Success Rate", f"{summary['success_rate']:.1f}%")
            
            st.markdown("**Recent Executions:**")
            for result in reversed(st.session_state.orchestrator.results[-5:]):
                status = "✅" if result.success else "❌"
                st.text(f"{status} {result.agent_name} - {result.timestamp[:19]}")
        else:
            st.info("No execution history yet.")

def render_custom_tools_ai():
    """Render AI-powered custom tools interface"""
    st.title("🛠️ AI-Powered Custom Tools")
    st.markdown("**Create and run tools with AI assistance**")
    
    # Initialize tools manager
    workspace_root = os.path.expanduser("~/gringo_workspace")
    if 'tools_manager' not in st.session_state:
        try:
            st.session_state.tools_manager = CustomToolsManager(workspace_root)
        except:
            # Fallback if CustomToolsManager not available
            st.session_state.tools_manager = None
    
    # Create tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🤖 AI Tool Creator",
        "⚡ Quick AI Run", 
        "📚 My Tools",
        "🎯 AI Suggestions"
    ])
    
    with tab1:
        st.subheader("🤖 AI Tool Creator")
        st.markdown("**Describe any tool and AI will create it for you**")
        
        # AI Tool Creation
        tool_description = st.text_area(
            "Describe the tool you want:",
            placeholder="""Examples:
- Create a file organizer that sorts files by date and type
- Make a text analyzer that counts words and finds patterns  
- Build a system monitor that alerts when CPU is high
- Create a backup tool that compresses and timestamps folders
- Make a log parser that extracts error messages""",
            height=120
        )
        
        col1, col2 = st.columns([2, 1])
        with col1:
            tool_language = st.selectbox("Preferred Language:", ["Python", "JavaScript", "Bash"])
        with col2:
            auto_run = st.checkbox("Auto-run after creation", value=False)
        
        if st.button("🚀 Generate Tool with AI", type="primary") and tool_description:
            with st.spinner("🤖 AI is creating your tool..."):
                
                # Generate tool with AI
                ai_prompt = f"""Create a {tool_language.lower()} tool that: {tool_description}

Requirements:
- Include clear comments and documentation
- Add error handling
- Make it production-ready
- Include usage examples
- Add command line arguments if needed

Please provide:
1. A good name for the tool
2. The complete code
3. Brief usage instructions"""
                
                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3", 
                            "prompt": ai_prompt,
                            "stream": False
                        },
                        timeout=60
                    )
                    
                    if response.status_code == 200:
                        ai_response = response.json().get('response', '')
                        
                        # Parse AI response to extract tool details
                        tool_name, tool_code, usage_info = parse_ai_tool_response(ai_response, tool_description)
                        
                        # Display the generated tool
                        st.success("✅ AI has created your tool!")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown(f"**🔧 Tool Name:** {tool_name}")
                            st.markdown(f"**📝 Description:** {tool_description[:100]}...")
                        with col2:
                            st.markdown(f"**💻 Language:** {tool_language}")
                            st.markdown(f"**📅 Created:** {datetime.now().strftime('%Y-%m-%d %H:%M')}")
                        
                        # Show the code
                        with st.expander("📄 Generated Code", expanded=True):
                            st.code(tool_code, language=tool_language.lower())
                        
                        # Save and run options
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("💾 Save Tool"):
                                if st.session_state.tools_manager:
                                    try:
                                        result = st.session_state.tools_manager.create_tool(
                                            name=tool_name,
                                            description=tool_description,
                                            category="ai_generated",
                                            language=tool_language.lower(),
                                            code=tool_code
                                        )
                                        st.success(f"✅ Tool saved as '{tool_name}'")
                                    except Exception as e:
                                        st.error(f"❌ Save failed: {e}")
                                else:
                                    # Fallback save
                                    save_tool_fallback(tool_name, tool_code, tool_language, workspace_root)
                                    st.success(f"✅ Tool saved to workspace")
                        
                        with col2:
                            if st.button("▶️ Run Now"):
                                run_result = execute_tool_code(tool_code, tool_language, workspace_root)
                                if run_result['success']:
                                    st.success("✅ Tool executed successfully!")
                                    st.code(run_result['output'])
                                    
                                    # Save after successful execution
                                    st.session_state['last_executed_tool'] = {
                                        'name': tool_name,
                                        'code': tool_code,
                                        'language': tool_language,
                                        'description': tool_description,
                                        'output': run_result['output']
                                    }
                                    
                                    # Show save option after successful run
                                    if st.button("💾 Save This Tool", key="save_after_run"):
                                        if st.session_state.tools_manager:
                                            try:
                                                result = st.session_state.tools_manager.create_tool(
                                                    name=tool_name,
                                                    description=tool_description,
                                                    category="ai_generated",
                                                    language=tool_language.lower(),
                                                    code=tool_code
                                                )
                                                st.success(f"✅ Tool '{tool_name}' saved to library!")
                                            except Exception as e:
                                                st.error(f"❌ Save failed: {e}")
                                        else:
                                            save_tool_fallback(tool_name, tool_code, tool_language, workspace_root)
                                            st.success(f"✅ Tool '{tool_name}' saved to workspace!")
                                else:
                                    st.error(f"❌ Execution failed: {run_result['error']}")
                                    st.info("💡 Try fixing the code or ask AI to improve it")
                        
                        with col3:
                            if st.button("🔄 Improve Tool"):
                                st.session_state['improve_tool'] = True
                                st.session_state['tool_to_improve'] = tool_code
                        
                        # Auto-run if requested
                        if auto_run:
                            st.info("🔄 Auto-running tool...")
                            run_result = execute_tool_code(tool_code, tool_language, workspace_root)
                            if run_result['success']:
                                st.success("✅ Auto-run completed!")
                                st.code(run_result['output'])
                        
                        # Show usage instructions
                        if usage_info:
                            with st.expander("📖 Usage Instructions"):
                                st.markdown(usage_info)
                    
                    else:
                        st.error("❌ AI service unavailable")
                
                except Exception as e:
                    st.error(f"❌ AI tool generation failed: {e}")
                    st.info("💡 Make sure Ollama is running: `ollama serve`")
        
        # Tool improvement section
        if st.session_state.get('improve_tool', False):
            st.markdown("---")
            st.subheader("🔄 Improve Tool")
            
            improvement_request = st.text_area(
                "How should the tool be improved?",
                placeholder="Add error handling, make it faster, add more features, etc."
            )
            
            if st.button("🚀 Improve with AI") and improvement_request:
                with st.spinner("🤖 AI is improving your tool..."):
                    improve_prompt = f"""Improve this {tool_language.lower()} code based on the request: {improvement_request}

Original code:
{st.session_state['tool_to_improve']}

Please provide the improved version with:
- Better error handling
- Performance optimizations  
- Additional features as requested
- Cleaner code structure
- Better documentation"""

                    try:
                        import requests
                        response = requests.post(
                            "http://localhost:11434/api/generate",
                            json={
                                "model": "llama3",
                                "prompt": improve_prompt,
                                "stream": False
                            },
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            improved_code = response.json().get('response', '')
                            st.success("✅ Tool improved!")
                            st.code(improved_code, language=tool_language.lower())
                            
                            if st.button("💾 Save Improved Version"):
                                st.session_state['tool_to_improve'] = improved_code
                                st.success("✅ Improved version saved!")
                        
                    except Exception as e:
                        st.error(f"❌ Improvement failed: {e}")
    
    with tab2:
        st.subheader("⚡ Quick AI Tool Runner")
        st.markdown("**AI runs tools for you - just describe what you want to do**")
        
        # Quick task description
        task_description = st.text_area(
            "What do you want to do?",
            placeholder="""Examples:
- Organize the files in my Downloads folder
- Find all Python files larger than 1MB
- Count lines of code in my project
- Clean up temporary files older than 7 days
- Generate a report of disk usage by folder""",
            height=100
        )
        
        # AI tool selection and execution
        if st.button("🤖 AI: Find and Run Tool", type="primary") and task_description:
            with st.spinner("🤖 AI is analyzing your request and finding the best tool..."):
                
                # Get available tools
                available_tools = []
                if st.session_state.tools_manager:
                    available_tools = st.session_state.tools_manager.get_tools_by_category()
                
                # AI tool recommendation
                recommend_prompt = f"""I need to: {task_description}

Available tools: {[tool.get('name', 'Unknown') + ': ' + tool.get('description', '') for tool in available_tools[:5]]}

Please either:
1. Recommend which existing tool to use and how to configure it
2. Or create a simple script to accomplish this task

Respond with either:
- EXISTING_TOOL: [tool_name] with parameters [parameters]
- NEW_SCRIPT: [code to accomplish the task]"""

                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3",
                            "prompt": recommend_prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        ai_recommendation = response.json().get('response', '')
                        
                        if "EXISTING_TOOL:" in ai_recommendation:
                            # AI recommends existing tool
                            st.success("🎯 AI found a perfect tool for your task!")
                            st.info(ai_recommendation)
                            
                            # Extract tool name and run it
                            tool_name = extract_tool_name(ai_recommendation)
                            if tool_name and st.session_state.tools_manager:
                                if st.button(f"▶️ Run {tool_name}"):
                                    # Find and run the tool
                                    tools = st.session_state.tools_manager.get_tools_by_category()
                                    target_tool = next((t for t in tools if t['name'].lower() == tool_name.lower()), None)
                                    if target_tool:
                                        result = st.session_state.tools_manager.run_tool(target_tool['id'])
                                        if result.get('success'):
                                            st.success("✅ Tool executed successfully!")
                                            st.code(result['output'])
                                        else:
                                            st.error(f"❌ Tool failed: {result.get('error')}")
                        
                        elif "NEW_SCRIPT:" in ai_recommendation:
                            # AI created new script
                            st.success("🚀 AI created a custom script for your task!")
                            
                            # Extract and display code
                            script_code = extract_script_code(ai_recommendation)
                            st.code(script_code, language='python')
                            
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                if st.button("▶️ Run Script"):
                                    result = execute_tool_code(script_code, 'python', workspace_root)
                                    if result['success']:
                                        st.success("✅ Script executed successfully!")
                                        st.code(result['output'])
                                        
                                        # Save after successful execution
                                        st.session_state['last_executed_script'] = {
                                            'code': script_code,
                                            'output': result['output'],
                                            'task': task_description
                                        }
                                        
                                        # Show save option
                                        if st.button("💾 Save This Script as Tool", key="save_script_after_run"):
                                            script_name = f"ai_task_{datetime.now().strftime('%m%d_%H%M%S')}"
                                            if st.session_state.tools_manager:
                                                try:
                                                    result = st.session_state.tools_manager.create_tool(
                                                        name=script_name,
                                                        description=f"AI-generated for: {task_description}",
                                                        category="ai_generated",
                                                        language="python",
                                                        code=script_code
                                                    )
                                                    st.success(f"✅ Script saved as '{script_name}'!")
                                                except Exception as e:
                                                    st.error(f"❌ Save failed: {e}")
                                            else:
                                                save_tool_fallback(script_name, script_code, 'python', workspace_root)
                                                st.success(f"✅ Script saved as '{script_name}'!")
                                    else:
                                        st.error(f"❌ Script failed: {result['error']}")
                                        st.info("💡 Try modifying the task description for better results")
                            
                            with col2:
                                if st.button("💾 Save as Tool"):
                                    script_name = f"ai_task_{datetime.now().strftime('%H%M%S')}"
                                    save_tool_fallback(script_name, script_code, 'python', workspace_root)
                                    st.success("✅ Script saved as tool!")
                        
                        else:
                            # General AI response
                            st.info("🤖 AI Response:")
                            st.markdown(ai_recommendation)
                    
                    else:
                        st.error("❌ AI service unavailable")
                
                except Exception as e:
                    st.error(f"❌ AI analysis failed: {e}")
        
        # Quick actions
        st.markdown("---")
        st.markdown("**⚡ Quick Actions:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("📁 Organize Files"):
                st.session_state['quick_task'] = "organize files in current directory by type"
        
        with col2:
            if st.button("🧹 Clean Temp Files"):
                st.session_state['quick_task'] = "find and remove temporary files older than 7 days"
        
        with col3:
            if st.button("📊 System Report"):
                st.session_state['quick_task'] = "generate system resource usage report"
        
        # Execute quick task
        if st.session_state.get('quick_task'):
            quick_task = st.session_state['quick_task']
            st.info(f"🔄 Executing: {quick_task}")
            
            # Simple task execution
            if "organize files" in quick_task:
                organize_script = """
import os
import shutil
from pathlib import Path

def organize_files():
    for file in Path('.').iterdir():
        if file.is_file() and file.suffix:
            ext_dir = Path(file.suffix[1:])
            ext_dir.mkdir(exist_ok=True)
            try:
                shutil.move(str(file), str(ext_dir / file.name))
                print(f"Moved {file.name} to {ext_dir}/")
            except:
                print(f"Could not move {file.name}")

organize_files()
print("File organization complete!")
"""
                result = execute_tool_code(organize_script, 'python', workspace_root)
                st.code(result['output'] if result['success'] else result['error'])
            
            st.session_state['quick_task'] = None
    
    with tab3:
        st.subheader("📚 My Tools Library")
        
        # Display saved tools
        if st.session_state.tools_manager:
            tools = st.session_state.tools_manager.get_tools_by_category()
            
            if tools:
                st.markdown(f"**🔧 {len(tools)} Tools Available:**")
                
                for tool in tools:
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.markdown(f"**🛠️ {tool['name']}**")
                            st.caption(tool['description'])
                            st.text(f"Language: {tool['language']} | Uses: {tool.get('usage_count', 0)}")
                        
                        with col2:
                            if st.button("🤖 AI Run", key=f"ai_run_{tool['id']}"):
                                st.info(f"🤖 AI is running {tool['name']} for you...")
                                result = st.session_state.tools_manager.run_tool(tool['id'])
                                if result.get('success'):
                                    st.success("✅ AI execution completed!")
                                    st.code(result['output'])
                                    
                                    # Show save option after successful execution
                                    if st.button("💾 Keep This Tool", key=f"keep_{tool['id']}"):
                                        st.success(f"✅ Tool '{tool['name']}' marked as favorite!")
                                        st.balloons()
                                else:
                                    st.error(f"❌ AI execution failed: {result.get('error')}")
                        
                        with col3:
                            if st.button("👁️ View", key=f"view_{tool['id']}"):
                                with open(tool['file_path'], 'r') as f:
                                    code = f.read()
                                with st.expander(f"📄 {tool['name']} Code", expanded=True):
                                    st.code(code, language=tool['language'])
                        
                        with col4:
                            if st.button("🗑️ Remove", key=f"remove_{tool['id']}"):
                                if st.session_state.tools_manager.delete_tool(tool['id']):
                                    st.success(f"✅ Tool '{tool['name']}' removed!")
                                    st.rerun()
                                else:
                                    st.error("❌ Failed to remove tool")
                        
                        st.markdown("---")
                
                # Batch operations
                st.markdown("---")
                st.markdown("**🔧 Batch Operations:**")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("🧹 Remove Unused Tools"):
                        unused_tools = [tool for tool in tools if tool.get('usage_count', 0) == 0]
                        if unused_tools:
                            st.info(f"Found {len(unused_tools)} unused tools")
                            if st.button("Confirm Removal", key="confirm_remove_unused"):
                                for tool in unused_tools:
                                    st.session_state.tools_manager.delete_tool(tool['id'])
                                st.success(f"✅ Removed {len(unused_tools)} unused tools!")
                                st.rerun()
                        else:
                            st.info("No unused tools found!")
                
                with col2:
                    if st.button("📊 Export All Tools"):
                        export_data = []
                        for tool in tools:
                            export_data.append(st.session_state.tools_manager.export_tool(tool['id']))
                        
                        import json
                        export_json = json.dumps(export_data, indent=2)
                        st.download_button(
                            label="💾 Download Tools Backup",
                            data=export_json,
                            file_name=f"gringo_tools_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                            mime="application/json"
                        )
                
                with col3:
                    if st.button("📈 Tool Usage Stats"):
                        st.markdown("**📊 Usage Statistics:**")
                        total_usage = sum(tool.get('usage_count', 0) for tool in tools)
                        most_used = max(tools, key=lambda x: x.get('usage_count', 0)) if tools else None
                        
                        st.metric("Total Tool Executions", total_usage)
                        if most_used:
                            st.metric("Most Used Tool", f"{most_used['name']} ({most_used.get('usage_count', 0)} uses)")
                        
                        # Show usage chart
                        usage_data = [(tool['name'], tool.get('usage_count', 0)) for tool in tools[-5:]]
                        if usage_data:
                            st.bar_chart({name: count for name, count in usage_data})
            else:
                st.info("No tools created yet. Use the AI Tool Creator to get started!")
        else:
            st.info("Tools manager not available. Using fallback mode.")
            
            # Show recent executed tools that can be saved
            if 'executed_tools_history' in st.session_state:
                st.markdown("**🕒 Recent Executions (Can Save):**")
                
                for i, executed_tool in enumerate(st.session_state['executed_tools_history'][-3:]):
                    with st.expander(f"💻 {executed_tool['name']} - {executed_tool['timestamp'][:19]}"):
                        st.text(f"Description: {executed_tool['description']}")
                        st.text(f"Language: {executed_tool['language']}")
                        st.code(executed_tool['output'], language='text')
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button(f"💾 Save Tool", key=f"save_history_{i}"):
                                save_tool_fallback(
                                    executed_tool['name'], 
                                    executed_tool['code'], 
                                    executed_tool['language'], 
                                    workspace_root
                                )
                                st.success(f"✅ Tool '{executed_tool['name']}' saved!")
                        
                        with col2:
                            if st.button(f"🗑️ Remove from History", key=f"remove_history_{i}"):
                                st.session_state['executed_tools_history'].remove(executed_tool)
                                st.success("✅ Removed from history")
                                st.rerun()
    
    with tab4:
        st.subheader("🎯 AI Tool Suggestions")
        st.markdown("**AI recommends tools based on your workflow**")
        
        # AI-powered tool suggestions
        if st.button("🤖 Get AI Tool Suggestions"):
            with st.spinner("🤖 AI is analyzing your workflow..."):
                
                # Analyze current workspace
                workspace_analysis = analyze_workspace(workspace_root)
                
                suggestion_prompt = f"""Based on this workspace analysis: {workspace_analysis}

Suggest 5 useful development tools that would help with this workflow. For each tool, provide:
1. Tool name
2. Brief description  
3. Why it would be useful
4. Implementation complexity (Low/Medium/High)

Focus on practical tools for productivity and automation."""

                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3",
                            "prompt": suggestion_prompt,
                            "stream": False
                        },
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        suggestions = response.json().get('response', '')
                        st.success("🎯 AI Tool Suggestions:")
                        st.markdown(suggestions)
                        
                        # Quick create buttons
                        st.markdown("**⚡ Quick Create:**")
                        col1, col2, col3 = st.columns(3)
                        
                        with col1:
                            if st.button("🔧 Create Tool 1"):
                                st.session_state['ai_create_tool'] = "first suggested tool"
                        
                        with col2:
                            if st.button("🔧 Create Tool 2"):
                                st.session_state['ai_create_tool'] = "second suggested tool"
                        
                        with col3:
                            if st.button("🔧 Create Tool 3"):
                                st.session_state['ai_create_tool'] = "third suggested tool"
                    
                except Exception as e:
                    st.error(f"❌ AI suggestions failed: {e}")
        
        # Workflow-based suggestions
        st.markdown("---")
        st.markdown("**📊 Common Tool Categories:**")
        
        categories = [
            ("📁 File Management", "Tools for organizing, copying, and managing files"),
            ("📝 Text Processing", "Tools for analyzing, converting, and processing text"),
            ("🔍 Code Analysis", "Tools for analyzing code quality and metrics"),
            ("🧹 System Cleanup", "Tools for cleaning and maintaining your system"),
            ("📊 Data Processing", "Tools for processing and analyzing data files"),
            ("🚀 Automation", "Tools for automating repetitive tasks")
        ]
        
        for category, description in categories:
            if st.button(f"Create {category} Tool"):
                st.session_state['category_create'] = category
                st.info(f"🤖 AI will create a {category.lower()} tool for you!")

# Helper functions for AI tool processing
def parse_ai_tool_response(ai_response, description):
    """Parse AI response to extract tool name, code, and usage"""
    lines = ai_response.split('\n')
    
    # Extract tool name (look for patterns)
    tool_name = "ai_generated_tool"
    for line in lines:
        if "name:" in line.lower() or "tool:" in line.lower():
            tool_name = line.split(':')[-1].strip()
            break
    
    # If no name found, generate from description
    if tool_name == "ai_generated_tool":
        words = description.split()[:3]
        tool_name = "_".join(w.lower() for w in words if w.isalpha())
    
    # Extract code (look for code blocks)
    code_start = -1
    code_end = -1
    
    for i, line in enumerate(lines):
        if '```' in line and code_start == -1:
            code_start = i + 1
        elif '```' in line and code_start != -1:
            code_end = i
            break
    
    if code_start != -1 and code_end != -1:
        tool_code = '\n'.join(lines[code_start:code_end])
    else:
        # Fallback: use the whole response as code
        tool_code = ai_response
    
    # Extract usage info (text after code)
    usage_info = ""
    if code_end != -1 and code_end < len(lines) - 1:
        usage_info = '\n'.join(lines[code_end+1:])
    
    return tool_name, tool_code, usage_info

def execute_tool_code(code, language, workspace_root):
    """Execute tool code safely and track for saving"""
    try:
        if language.lower() == 'python':
            # Create temporary file
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(code)
                temp_file = f.name
            
            # Execute
            result = subprocess.run(
                ['python', temp_file],
                capture_output=True,
                text=True,
                timeout=30,
                cwd=workspace_root
            )
            
            # Cleanup
            os.unlink(temp_file)
            
            execution_result = {
                "success": result.returncode == 0,
                "output": result.stdout,
                "error": result.stderr
            }
            
            # Track successful executions for potential saving
            if execution_result["success"]:
                if 'executed_tools_history' not in st.session_state:
                    st.session_state['executed_tools_history'] = []
                
                # Add to history (keep last 10)
                tool_execution = {
                    'name': f"executed_tool_{datetime.now().strftime('%H%M%S')}",
                    'code': code,
                    'language': language,
                    'output': result.stdout,
                    'timestamp': datetime.now().isoformat(),
                    'description': f"Executed {language} tool"
                }
                
                st.session_state['executed_tools_history'].append(tool_execution)
                if len(st.session_state['executed_tools_history']) > 10:
                    st.session_state['executed_tools_history'].pop(0)
            
            return execution_result
        
        else:
            return {"success": False, "error": f"Language {language} not supported yet"}
            
    except Exception as e:
        return {"success": False, "error": str(e)}

def save_tool_fallback(name, code, language, workspace_root):
    """Fallback tool saving when tools manager not available"""
    tools_dir = os.path.join(workspace_root, "ai_tools")
    os.makedirs(tools_dir, exist_ok=True)
    
    ext = '.py' if language.lower() == 'python' else '.js' if language.lower() == 'javascript' else '.sh'
    file_path = os.path.join(tools_dir, f"{name}{ext}")
    
    with open(file_path, 'w') as f:
        f.write(f"#!/usr/bin/env {language.lower()}\n")
        f.write(f"# Generated by AI on {datetime.now()}\n\n")
        f.write(code)
    
    # Make executable
    os.chmod(file_path, 0o755)

def extract_tool_name(ai_response):
    """Extract tool name from AI response"""
    lines = ai_response.split('\n')
    for line in lines:
        if 'EXISTING_TOOL:' in line:
            parts = line.split(':')
            if len(parts) > 1:
                return parts[1].strip().split()[0]
    return None

def extract_script_code(ai_response):
    """Extract script code from AI response"""
    lines = ai_response.split('\n')
    code_lines = []
    in_code = False
    
    for line in lines:
        if 'NEW_SCRIPT:' in line:
            in_code = True
            continue
        if in_code:
            code_lines.append(line)
    
    return '\n'.join(code_lines).strip()

def analyze_workspace(workspace_root):
    """Analyze workspace for AI suggestions"""
    try:
        analysis = {
            "total_files": 0,
            "python_files": 0,
            "js_files": 0,
            "directories": 0,
            "recent_files": 0
        }
        
        for root, dirs, files in os.walk(workspace_root):
            analysis["directories"] += len(dirs)
            analysis["total_files"] += len(files)
            
            for file in files:
                if file.endswith('.py'):
                    analysis["python_files"] += 1
                elif file.endswith('.js'):
                    analysis["js_files"] += 1
                
                # Check if recent (last 7 days)
                file_path = os.path.join(root, file)
                if os.path.getmtime(file_path) > (datetime.now().timestamp() - 7*24*3600):
                    analysis["recent_files"] += 1
        
        return f"Workspace has {analysis['total_files']} files, {analysis['python_files']} Python files, {analysis['js_files']} JS files, {analysis['directories']} directories, {analysis['recent_files']} recently modified files"
    
    except:
        return "Unable to analyze workspace"

def main():
    """Main application"""
    
    # GRINGO Branded Header
    st.markdown("""
    <div class="gringo-header">
        <div class="gringo-logo">⚙️ GRINGO AI OS</div>
        <div class="gringo-tagline">Ultimate AI-Powered Development Environment</div>
        <div class="gringo-subtitle">Transform ideas into working code • Privacy-first local AI • Multi-agent orchestration</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("🤖 GRINGO Navigation")
    st.sidebar.markdown("**Complete AI Development Suite**")
    
    # Clean sidebar without large logo
    st.sidebar.markdown("""
    <div style="text-align: center; margin: 1rem 0;">
        <div style="font-size: 2rem;">⚙️</div>
        <div style="color: #06b6d4; font-weight: bold;">GRINGO AI OS</div>
        <div style="color: #94a3b8; font-size: 0.9rem;">Ultimate Development Suite</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Navigation
    page = st.sidebar.radio(
        "Navigate:",
        [
            "🚀 Project Creator", 
            "🤖 Agent Control", 
            "🛠️ Custom Tools", 
            "📖 Documentation", 
            "💻 Terminal", 
            "🤖 AI Chat", 
            "📊 Dashboard"
        ]
    )
    
    # Show system info
    st.sidebar.markdown("---")
    workspace_root = os.path.expanduser("~/gringo_workspace")
    st.sidebar.text(f"Workspace: {workspace_root}")
    
    # Page routing
    if page == "🚀 Project Creator":
        render_project_creator()
    
    elif page == "🤖 Agent Control":
        render_agent_control()
    
    elif page == "🛠️ Custom Tools":
        render_custom_tools_ai()
    
    elif page == "📖 Documentation":
        st.title("📖 Documentation")
        st.markdown("""
# 🤖 GRINGO Ultimate Development Dashboard

## Features:
- **🚀 Project Creator** - Natural language project generation
- **🤖 Agent Control** - Multi-agent orchestration system  
- **🛠️ Custom Tools** - Personal development toolkit
- **💻 Terminal** - Integrated command line
- **🤖 AI Chat** - Local LLaMA assistance
- **📊 Dashboard** - System overview

## Multi-Agent System:
Your system includes specialized agents for:
- **Planning** - Task breakdown and architecture
- **Refactoring** - Code optimization  
- **Testing** - Automated test generation
- **Documentation** - Auto-generated docs
- **Security** - Security analysis
- **Performance** - Optimization recommendations
- **Review** - Code quality checks

## Getting Started:
1. Create projects with natural language prompts
2. Use agents to enhance and optimize your code
3. Build custom tools for repetitive tasks
4. Chat with AI for complex planning

**Your complete local development environment!**
""")
    
    elif page == "💻 Terminal":
        st.title("💻 Terminal")
        st.markdown("**Integrated command line interface**")
        
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
        
        user_input = st.text_area("Message:", placeholder="Ask me about your projects...")
        
        if st.button("Send") and user_input:
            with st.spinner("🤖 Thinking..."):
                try:
                    import requests
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={"model": "llama3", "prompt": user_input, "stream": False},
                        timeout=30
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        st.markdown(f"**🧠 You:** {user_input}")
                        st.markdown(f"**🤖 AI:** {result.get('response', 'No response')}")
                    else:
                        st.error("❌ AI service unavailable")
                    
                except Exception as e:
                    st.error(f"❌ AI chat failed: {e}")
                    st.info("💡 Make sure Ollama is running: `ollama serve`")
    
    elif page == "📊 Dashboard":
        st.title("📊 System Dashboard")
        
        workspace_root = os.path.expanduser("~/gringo_workspace")
        
        col1, col2, col3 = st.columns(3)
        col1.metric("🚀 Status", "Running")
        col2.metric("🤖 Agents", "10 Available")
        col3.metric("💾 Workspace", workspace_root.split('/')[-1])
        
        st.markdown("**🎯 Quick Actions:**")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.button("🚀 Create Project")
        with col2:
            st.button("🤖 Run Agents")
        with col3:
            st.button("🛠️ Build Tool")

if __name__ == "__main__":
    main()
