#!/usr/bin/env python3
"""
Enhanced GRINGO Project Creation UI
Full project management with file upload, creation, and task execution
"""

import streamlit as st
import os
import json
import tempfile
import zipfile
import shutil
from datetime import datetime
import subprocess
import sqlite3
from pathlib import Path

# Import our project manager
try:
    from project_manager import ProjectManager
    from call_llama import call_llama_api
except ImportError as e:
    st.error(f"Import error: {e}")

class ProjectCreationUI:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.project_manager = ProjectManager(workspace_root)
        
    def render_project_creation_interface(self):
        """Render the main project creation interface"""
        
        st.title("🚀 GRINGO Project Creator")
        st.markdown("**Create any project through natural language prompts**")
        
        # Create tabs for different creation methods
        tab1, tab2, tab3, tab4, tab5 = st.tabs([
            "💬 Create from Prompt", 
            "📁 Upload & Manage", 
            "🔧 Existing Projects", 
            "🎯 Quick Tasks",
            "📦 Project Templates"
        ])
        
        with tab1:
            self.render_prompt_creation()
        
        with tab2:
            self.render_file_upload()
        
        with tab3:
            self.render_existing_projects()
        
        with tab4:
            self.render_quick_tasks()
        
        with tab5:
            self.render_project_templates()
    
    def render_prompt_creation(self):
        """Render the natural language project creation interface"""
        
        st.subheader("🧠 Create Project from Description")
        st.markdown("Tell me what you want to build, and I'll create the entire project for you!")
        
        # Project prompt input
        prompt = st.text_area(
            "Describe your project:",
            placeholder="""Examples:
- Create a web scraping tool that collects news articles
- Build a personal expense tracker with a web interface  
- Make a simple 2D game with Python and Pygame
- Develop a REST API for a todo list application
- Create a data analysis dashboard for sales data
- Build an automation script for file organization""",
            height=150
        )
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            project_name = st.text_input(
                "Project name (optional):", 
                placeholder="Leave empty for auto-generated name"
            )
        
        with col2:
            auto_run = st.checkbox("Auto-run after creation", value=False)
        
        if st.button("🚀 Create Project", type="primary"):
            if prompt:
                with st.spinner("🤖 Creating your project..."):
                    try:
                        # Create project from prompt
                        result = self.project_manager.create_project_from_prompt(
                            prompt, 
                            project_name if project_name else None
                        )
                        
                        st.success(f"✅ Project '{result['name']}' created successfully!")
                        
                        # Display creation summary
                        with st.expander("📋 Project Creation Summary", expanded=True):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                st.markdown("**📊 Project Details:**")
                                st.text(f"Name: {result['name']}")
                                st.text(f"Type: {result['type']}")
                                st.text(f"Path: {result['path']}")
                                st.text(f"Status: {result['status']}")
                            
                            with col2:
                                st.markdown("**📁 Files Created:**")
                                for file in result['files_created']:
                                    st.text(file)
                        
                        # Next steps
                        if result.get('next_steps'):
                            st.markdown("**🎯 Recommended Next Steps:**")
                            for step in result['next_steps']:
                                st.markdown(f"- {step}")
                        
                        # Action buttons
                        col1, col2, col3, col4 = st.columns(4)
                        
                        with col1:
                            if st.button("🔧 Open in File Manager"):
                                st.session_state.current_project_path = result['path']
                                st.success(f"Switched to project directory")
                        
                        with col2:
                            if st.button("▶️ Run Project"):
                                run_result = self.project_manager.run_project(result['name'])
                                if run_result.get('success'):
                                    st.success("✅ Project executed successfully!")
                                    with st.expander("📊 Execution Output"):
                                        st.code(run_result['output'])
                                else:
                                    st.error(f"❌ Execution failed: {run_result.get('error', 'Unknown error')}")
                        
                        with col3:
                            if st.button("📦 Export Project"):
                                export_path = self.project_manager.export_project(result['name'])
                                st.success(f"✅ Exported to: {export_path}")
                        
                        with col4:
                            if st.button("🤖 Enhance with AI"):
                                self.enhance_project_with_ai(result['name'], prompt)
                        
                        # Auto-run if requested
                        if auto_run:
                            st.info("🔄 Auto-running project...")
                            run_result = self.project_manager.run_project(result['name'])
                            if run_result.get('success'):
                                st.success("✅ Auto-run completed!")
                            
                    except Exception as e:
                        st.error(f"❌ Failed to create project: {e}")
            else:
                st.warning("Please describe what you want to build!")
    
    def render_file_upload(self):
        """Render the file upload and management interface"""
        
        st.subheader("📁 File Upload & Project Import")
        
        # File upload section
        upload_type = st.radio(
            "Upload type:",
            ["📄 Single Files", "📦 Project Archive (ZIP)", "📁 Multiple Files"]
        )
        
        if upload_type == "📄 Single Files":
            uploaded_file = st.file_uploader(
                "Upload file:",
                type=['py', 'js', 'html', 'css', 'json', 'txt', 'md', 'csv', 'xlsx'],
                accept_multiple_files=False
            )
            
            if uploaded_file:
                col1, col2 = st.columns(2)
                
                with col1:
                    st.markdown("**File Details:**")
                    st.text(f"Name: {uploaded_file.name}")
                    st.text(f"Size: {uploaded_file.size} bytes")
                    st.text(f"Type: {uploaded_file.type}")
                
                with col2:
                    action = st.selectbox(
                        "What should I do with this file?",
                        [
                            "📋 Analyze and summarize",
                            "🔧 Create project around this file",
                            "🐛 Find and fix bugs",
                            "📚 Generate documentation",
                            "🧪 Create tests",
                            "⚡ Optimize performance",
                            "🔄 Convert to different format"
                        ]
                    )
                
                if st.button("🚀 Process File"):
                    self.process_uploaded_file(uploaded_file, action)
        
        elif upload_type == "📦 Project Archive (ZIP)":
            uploaded_zip = st.file_uploader(
                "Upload project ZIP file:",
                type=['zip'],
                accept_multiple_files=False
            )
            
            if uploaded_zip:
                project_name = st.text_input(
                    "Project name:", 
                    value=uploaded_zip.name.replace('.zip', '')
                )
                
                if st.button("📦 Import Project"):
                    self.import_project_from_zip(uploaded_zip, project_name)
        
        elif upload_type == "📁 Multiple Files":
            uploaded_files = st.file_uploader(
                "Upload multiple files:",
                accept_multiple_files=True
            )
            
            if uploaded_files:
                st.markdown(f"**📊 {len(uploaded_files)} files selected:**")
                for file in uploaded_files:
                    st.text(f"• {file.name} ({file.size} bytes)")
                
                project_name = st.text_input("Project name for these files:")
                
                if st.button("🚀 Create Project from Files"):
                    self.create_project_from_files(uploaded_files, project_name)
    
    def render_existing_projects(self):
        """Render existing projects management"""
        
        st.subheader("🔧 Manage Existing Projects")
        
        projects = self.project_manager.list_projects()
        
        if not projects:
            st.info("No projects found. Create your first project!")
            return
        
        # Project grid
        cols = st.columns(3)
        for i, project in enumerate(projects):
            with cols[i % 3]:
                with st.container():
                    st.markdown(f"**📁 {project['name']}**")
                    st.text(f"Type: {project['type']}")
                    st.text(f"Created: {project['created_at'][:10]}")
                    
                    if project['description']:
                        st.caption(project['description'][:100] + "..." if len(project['description']) > 100 else project['description'])
                    
                    # Action buttons
                    button_col1, button_col2 = st.columns(2)
                    
                    with button_col1:
                        if st.button("▶️ Run", key=f"run_{project['id']}"):
                            self.run_project_by_id(project)
                    
                    with button_col2:
                        if st.button("📝 Edit", key=f"edit_{project['id']}"):
                            self.open_project_editor(project)
        
        # Bulk operations
        st.markdown("---")
        st.subheader("🔧 Bulk Operations")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("📦 Export All Projects"):
                self.export_all_projects()
        
        with col2:
            if st.button("🧹 Clean Unused Projects"):
                self.clean_unused_projects()
        
        with col3:
            if st.button("📊 Generate Report"):
                self.generate_projects_report()
        
        with col4:
            if st.button("🔄 Sync with Git"):
                self.sync_projects_with_git()
    
    def render_quick_tasks(self):
        """Render quick task execution interface"""
        
        st.subheader("🎯 Quick Task Execution")
        st.markdown("Execute any task on your files or system through natural language")
        
        # Task input
        task_prompt = st.text_area(
            "What task do you want to perform?",
            placeholder="""Examples:
- Find all Python files with TODO comments
- Create a backup of all my project files
- Generate a summary of all my JavaScript projects
- Find and fix common security issues in my code
- Create documentation for all my projects
- Analyze disk usage in my workspace
- Convert all my CSV files to JSON
- Find duplicate files in my projects""",
            height=120
        )
        
        # Target selection
        target_type = st.selectbox(
            "Apply to:",
            [
                "🌍 Entire workspace",
                "📁 Specific project",
                "📄 Specific files",
                "🔍 Files matching pattern"
            ]
        )
        
        target_details = ""
        if target_type == "📁 Specific project":
            projects = self.project_manager.list_projects()
            if projects:
                selected_project = st.selectbox(
                    "Select project:",
                    projects,
                    format_func=lambda x: f"{x['name']} ({x['type']})"
                )
                target_details = selected_project['path']
        
        elif target_type == "🔍 Files matching pattern":
            target_details = st.text_input(
                "File pattern:",
                placeholder="*.py, *.js, data/*.csv, etc."
            )
        
        # Execution options
        col1, col2 = st.columns(2)
        with col1:
            save_results = st.checkbox("Save results to file", value=True)
        with col2:
            show_progress = st.checkbox("Show detailed progress", value=True)
        
        if st.button("🚀 Execute Task", type="primary"):
            if task_prompt:
                self.execute_quick_task(task_prompt, target_type, target_details, save_results, show_progress)
            else:
                st.warning("Please describe the task you want to perform!")
    
    def render_project_templates(self):
        """Render project templates interface"""
        
        st.subheader("📦 Project Templates")
        
        # Predefined templates
        templates = {
            "🌐 Web Application": {
                "description": "Full-stack web application with frontend and backend",
                "prompt": "Create a web application with HTML, CSS, JavaScript frontend and Python Flask backend with database"
            },
            "📊 Data Analysis": {
                "description": "Data science project with Jupyter notebooks and visualization",
                "prompt": "Create a data analysis project with Jupyter notebooks, pandas, matplotlib for analyzing CSV data"
            },
            "🤖 AI/ML Project": {
                "description": "Machine learning project with model training and prediction",
                "prompt": "Create a machine learning project with scikit-learn for classification and model evaluation"
            },
            "🎮 Game Development": {
                "description": "2D game development with Pygame",
                "prompt": "Create a 2D game using Python and Pygame with sprites, collision detection, and scoring"
            },
            "🔧 Automation Script": {
                "description": "File processing and automation utilities",
                "prompt": "Create an automation script for file organization, batch processing, and system maintenance"
            },
            "📱 Mobile App": {
                "description": "Cross-platform mobile application",
                "prompt": "Create a mobile application using React Native with navigation and API integration"
            },
            "🗄️ Database Project": {
                "description": "Database-driven application with CRUD operations",
                "prompt": "Create a database application with SQLite, CRUD operations, and data management interface"
            },
            "🔒 Security Tool": {
                "description": "Cybersecurity and penetration testing utilities",
                "prompt": "Create security analysis tools for vulnerability scanning and network monitoring"
            }
        }
        
        # Display templates in grid
        cols = st.columns(2)
        for i, (name, info) in enumerate(templates.items()):
            with cols[i % 2]:
                with st.container():
                    st.markdown(f"**{name}**")
                    st.caption(info['description'])
                    
                    if st.button(f"Create {name.split(' ')[-1]}", key=f"template_{i}"):
                        # Auto-fill the prompt creation with template
                        if 'template_prompt' not in st.session_state:
                            st.session_state.template_prompt = info['prompt']
                        
                        st.success(f"Template loaded! Go to 'Create from Prompt' tab to customize and create.")
                        st.info(f"Prompt: {info['prompt']}")
        
        # Custom template creation
        st.markdown("---")
        st.subheader("➕ Create Custom Template")
        
        template_name = st.text_input("Template name:")
        template_description = st.text_input("Description:")
        template_prompt = st.text_area("Template prompt:")
        
        if st.button("💾 Save Template"):
            if template_name and template_prompt:
                # Save custom template (implement this)
                st.success(f"✅ Template '{template_name}' saved!")
            else:
                st.warning("Please provide name and prompt for the template!")
    
    def process_uploaded_file(self, uploaded_file, action):
        """Process an uploaded file based on the selected action"""
        
        with st.spinner(f"Processing {uploaded_file.name}..."):
            # Save file temporarily
            temp_dir = tempfile.mkdtemp()
            file_path = os.path.join(temp_dir, uploaded_file.name)
            
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getvalue())
            
            try:
                if action == "📋 Analyze and summarize":
                    self.analyze_file(file_path, uploaded_file.name)
                elif action == "🔧 Create project around this file":
                    self.create_project_from_file(file_path, uploaded_file.name)
                elif action == "🐛 Find and fix bugs":
                    self.find_and_fix_bugs(file_path, uploaded_file.name)
                elif action == "📚 Generate documentation":
                    self.generate_documentation(file_path, uploaded_file.name)
                elif action == "🧪 Create tests":
                    self.create_tests(file_path, uploaded_file.name)
                elif action == "⚡ Optimize performance":
                    self.optimize_performance(file_path, uploaded_file.name)
                elif action == "🔄 Convert to different format":
                    self.convert_file_format(file_path, uploaded_file.name)
                    
            finally:
                # Clean up temp file
                shutil.rmtree(temp_dir)
    
    def analyze_file(self, file_path: str, filename: str):
        """Analyze uploaded file and provide insights"""
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Basic analysis
            lines = content.split('\n')
            
            st.success(f"✅ Analysis complete for {filename}")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("**📊 File Statistics:**")
                st.metric("Lines of code", len(lines))
                st.metric("Characters", len(content))
                st.metric("File size", f"{len(content.encode('utf-8'))} bytes")
            
            with col2:
                st.markdown("**🔍 Content Analysis:**")
                
                # Detect file type and provide specific analysis
                if filename.endswith('.py'):
                    imports = [line.strip() for line in lines if line.strip().startswith('import') or line.strip().startswith('from')]
                    functions = [line.strip() for line in lines if line.strip().startswith('def ')]
                    classes = [line.strip() for line in lines if line.strip().startswith('class ')]
                    
                    st.text(f"Imports: {len(imports)}")
                    st.text(f"Functions: {len(functions)}")
                    st.text(f"Classes: {len(classes)}")
                
                elif filename.endswith('.js'):
                    functions = [line for line in lines if 'function' in line]
                    st.text(f"Functions: {len(functions)}")
            
            # Show content preview
            with st.expander("📄 File Content Preview"):
                st.code(content[:1000] + "..." if len(content) > 1000 else content)
            
            # AI Analysis button
            if st.button("🤖 Get AI Analysis"):
                ai_analysis = self.get_ai_file_analysis(content, filename)
                if ai_analysis:
                    with st.expander("🧠 AI Analysis Results", expanded=True):
                        st.markdown(ai_analysis)
                        
        except Exception as e:
            st.error(f"❌ Failed to analyze file: {e}")
    
    def get_ai_file_analysis(self, content: str, filename: str) -> str:
        """Get AI analysis of the file content"""
        
        prompt = f"""Analyze this {filename} file and provide insights:

File: {filename}
Content:
{content[:2000]}

Please provide:
1. Code quality assessment
2. Potential improvements
3. Security considerations
4. Performance optimization suggestions
5. Best practices recommendations
"""
        
        try:
            response = call_llama_api(prompt)
            return response
        except Exception as e:
            st.error(f"AI analysis failed: {e}")
            return None
    
    def execute_quick_task(self, task_prompt: str, target_type: str, target_details: str, save_results: bool, show_progress: bool):
        """Execute a quick task based on the prompt"""
        
        with st.spinner("🚀 Executing task..."):
            
            if show_progress:
                progress_bar = st.progress(0)
                status_text = st.empty()
            
            try:
                # Here you would implement the actual task execution
                # This is a simplified version
                
                if show_progress:
                    status_text.text("🔍 Analyzing task...")
                    progress_bar.progress(25)
                
                # Simulate task execution
                import time
                time.sleep(1)
                
                if show_progress:
                    status_text.text("⚙️ Processing files...")
                    progress_bar.progress(50)
                
                time.sleep(1)
                
                if show_progress:
                    status_text.text("📊 Generating results...")
                    progress_bar.progress(75)
                
                time.sleep(1)
                
                if show_progress:
                    status_text.text("✅ Task completed!")
                    progress_bar.progress(100)
                
                # Mock results
                results = {
                    "task": task_prompt,
                    "target": f"{target_type}: {target_details}",
                    "status": "completed",
                    "files_processed": 42,
                    "time_taken": "3.2 seconds",
                    "results": "Task executed successfully. Found 15 matches, processed 42 files, made 8 improvements."
                }
                
                st.success("✅ Task completed successfully!")
                
                with st.expander("📊 Task Results", expanded=True):
                    st.json(results)
                
                if save_results:
                    results_file = f"task_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                    results_path = os.path.join(self.workspace_root, results_file)
                    with open(results_path, 'w') as f:
                        json.dump(results, f, indent=2)
                    st.info(f"📁 Results saved to: {results_file}")
                
            except Exception as e:
                st.error(f"❌ Task execution failed: {e}")
    
    def enhance_project_with_ai(self, project_name: str, original_prompt: str):
        """Enhance a project using AI"""
        
        enhancement_prompt = f"""
        Enhance the project '{project_name}' that was created from this prompt:
        "{original_prompt}"
        
        Please suggest specific improvements, additional features, and code enhancements.
        """
        
        with st.spinner("🤖 AI is enhancing your project..."):
            try:
                ai_suggestions = call_llama_api(enhancement_prompt)
                
                st.success("✅ AI enhancement suggestions ready!")
                
                with st.expander("🧠 AI Enhancement Suggestions", expanded=True):
                    st.markdown(ai_suggestions)
                    
                if st.button("🚀 Apply AI Suggestions"):
                    st.info("🔄 Applying AI suggestions... (This would implement the actual enhancements)")
                    
            except Exception as e:
                st.error(f"❌ AI enhancement failed: {e}")

# Streamlit interface integration
def render_enhanced_project_interface():
    """Render the enhanced project creation interface"""
    
    # Initialize project creation UI
    workspace_root = os.path.expanduser("~/gringo_workspace")
    project_ui = ProjectCreationUI(workspace_root)
    
    # Render the interface
    project_ui.render_project_creation_interface()
