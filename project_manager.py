#!/usr/bin/env python3
"""
GRINGO Project Manager - Create, manage, and deploy any type of project through prompts
"""

import os
import json
import shutil
import subprocess
import zipfile
import tempfile
from datetime import datetime
from pathlib import Path
import sqlite3

class ProjectManager:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.projects_dir = os.path.join(workspace_root, "projects")
        self.templates_dir = os.path.join(workspace_root, "templates")
        self.db_path = os.path.join(workspace_root, "projects.db")
        self._init_directories()
        self._init_database()
    
    def _init_directories(self):
        """Initialize project directories"""
        os.makedirs(self.projects_dir, exist_ok=True)
        os.makedirs(self.templates_dir, exist_ok=True)
    
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
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS project_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                filename TEXT,
                filepath TEXT,
                file_type TEXT,
                size INTEGER,
                purpose TEXT,
                ai_generated BOOLEAN DEFAULT FALSE,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_project_from_prompt(self, prompt: str, project_name: str = None) -> dict:
        """Create a complete project from a natural language prompt"""
        
        # Analyze prompt to determine project type and requirements
        project_info = self._analyze_prompt(prompt)
        
        if not project_name:
            project_name = project_info.get('suggested_name', f"project_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Create project directory
        project_path = os.path.join(self.projects_dir, project_name)
        os.makedirs(project_path, exist_ok=True)
        
        # Generate project structure based on type
        files_created = self._generate_project_structure(project_path, project_info)
        
        # Save project to database
        project_id = self._save_project_to_db(project_name, project_info, project_path)
        
        # Generate initial files based on prompt
        ai_files = self._generate_ai_files(project_path, project_info, prompt)
        files_created.extend(ai_files)
        
        # Create run/build scripts
        run_scripts = self._create_run_scripts(project_path, project_info)
        files_created.extend(run_scripts)
        
        return {
            "project_id": project_id,
            "name": project_name,
            "path": project_path,
            "type": project_info['type'],
            "files_created": files_created,
            "status": "created",
            "next_steps": project_info.get('next_steps', [])
        }
    
    def _analyze_prompt(self, prompt: str) -> dict:
        """Analyze prompt to determine project type and requirements"""
        
        prompt_lower = prompt.lower()
        
        # Detect project type
        if any(word in prompt_lower for word in ['web app', 'website', 'frontend', 'react', 'vue', 'angular']):
            project_type = 'web_frontend'
        elif any(word in prompt_lower for word in ['api', 'backend', 'server', 'flask', 'django', 'fastapi', 'express']):
            project_type = 'web_backend'
        elif any(word in prompt_lower for word in ['data', 'analysis', 'pandas', 'jupyter', 'machine learning', 'ml', 'ai']):
            project_type = 'data_science'
        elif any(word in prompt_lower for word in ['game', 'pygame', 'unity', 'godot']):
            project_type = 'game'
        elif any(word in prompt_lower for word in ['automation', 'script', 'tool', 'utility']):
            project_type = 'automation'
        elif any(word in prompt_lower for word in ['mobile', 'android', 'ios', 'react native', 'flutter']):
            project_type = 'mobile'
        elif any(word in prompt_lower for word in ['desktop', 'gui', 'tkinter', 'pyqt', 'electron']):
            project_type = 'desktop'
        else:
            project_type = 'general'
        
        # Detect programming language
        if any(word in prompt_lower for word in ['python', 'py', 'django', 'flask', 'fastapi']):
            language = 'python'
        elif any(word in prompt_lower for word in ['javascript', 'js', 'node', 'react', 'vue', 'angular']):
            language = 'javascript'
        elif any(word in prompt_lower for word in ['typescript', 'ts']):
            language = 'typescript'
        elif any(word in prompt_lower for word in ['java', 'spring']):
            language = 'java'
        elif any(word in prompt_lower for word in ['c++', 'cpp']):
            language = 'cpp'
        elif any(word in prompt_lower for word in ['rust', 'cargo']):
            language = 'rust'
        elif any(word in prompt_lower for word in ['go', 'golang']):
            language = 'go'
        else:
            language = 'python'  # Default
        
        # Extract features/requirements
        features = []
        if 'database' in prompt_lower or 'db' in prompt_lower:
            features.append('database')
        if 'auth' in prompt_lower or 'login' in prompt_lower:
            features.append('authentication')
        if 'api' in prompt_lower:
            features.append('api')
        if 'ui' in prompt_lower or 'interface' in prompt_lower:
            features.append('ui')
        if 'test' in prompt_lower:
            features.append('testing')
        
        return {
            'type': project_type,
            'language': language,
            'features': features,
            'description': prompt,
            'suggested_name': self._suggest_project_name(prompt, project_type),
            'next_steps': self._get_next_steps(project_type, language)
        }
    
    def _suggest_project_name(self, prompt: str, project_type: str) -> str:
        """Suggest a project name based on prompt"""
        words = prompt.lower().split()
        key_words = [w for w in words if len(w) > 3 and w not in ['create', 'build', 'make', 'develop', 'app', 'project']]
        
        if key_words:
            name = '_'.join(key_words[:3])
        else:
            name = project_type
        
        return f"{name}_{datetime.now().strftime('%Y%m%d')}"
    
    def _generate_project_structure(self, project_path: str, project_info: dict) -> list:
        """Generate basic project structure"""
        
        files_created = []
        project_type = project_info['type']
        language = project_info['language']
        
        # Common directories
        dirs_to_create = ['src', 'docs', 'tests']
        
        if project_type == 'web_frontend':
            dirs_to_create.extend(['public', 'assets', 'components'])
        elif project_type == 'web_backend':
            dirs_to_create.extend(['api', 'models', 'routes'])
        elif project_type == 'data_science':
            dirs_to_create.extend(['data', 'notebooks', 'models', 'visualizations'])
        elif project_type == 'game':
            dirs_to_create.extend(['assets', 'sprites', 'sounds', 'levels'])
        elif project_type == 'mobile':
            dirs_to_create.extend(['screens', 'components', 'assets'])
        elif project_type == 'desktop':
            dirs_to_create.extend(['ui', 'resources', 'assets'])
        
        # Create directories
        for dir_name in dirs_to_create:
            dir_path = os.path.join(project_path, dir_name)
            os.makedirs(dir_path, exist_ok=True)
            files_created.append(f"📁 {dir_name}/")
        
        # Create basic files
        if language == 'python':
            files_created.extend(self._create_python_files(project_path, project_info))
        elif language == 'javascript':
            files_created.extend(self._create_javascript_files(project_path, project_info))
        elif language == 'typescript':
            files_created.extend(self._create_typescript_files(project_path, project_info))
        
        return files_created
    
    def _create_python_files(self, project_path: str, project_info: dict) -> list:
        """Create Python-specific files"""
        files = []
        
        # requirements.txt
        requirements_content = self._get_python_requirements(project_info)
        with open(os.path.join(project_path, 'requirements.txt'), 'w') as f:
            f.write(requirements_content)
        files.append("📄 requirements.txt")
        
        # main.py
        main_content = self._get_python_main(project_info)
        with open(os.path.join(project_path, 'main.py'), 'w') as f:
            f.write(main_content)
        files.append("🐍 main.py")
        
        # setup.py
        setup_content = self._get_python_setup(project_info)
        with open(os.path.join(project_path, 'setup.py'), 'w') as f:
            f.write(setup_content)
        files.append("⚙️ setup.py")
        
        # README.md
        readme_content = self._get_readme(project_info)
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        files.append("📖 README.md")
        
        return files
    
    def _create_javascript_files(self, project_path: str, project_info: dict) -> list:
        """Create JavaScript-specific files"""
        files = []
        
        # package.json
        package_content = self._get_package_json(project_info)
        with open(os.path.join(project_path, 'package.json'), 'w') as f:
            f.write(package_content)
        files.append("📦 package.json")
        
        # index.js or app.js
        main_file = 'index.js' if project_info['type'] == 'web_backend' else 'app.js'
        main_content = self._get_javascript_main(project_info)
        with open(os.path.join(project_path, main_file), 'w') as f:
            f.write(main_content)
        files.append(f"📄 {main_file}")
        
        # README.md
        readme_content = self._get_readme(project_info)
        with open(os.path.join(project_path, 'README.md'), 'w') as f:
            f.write(readme_content)
        files.append("📖 README.md")
        
        return files
    
    def _create_typescript_files(self, project_path: str, project_info: dict) -> list:
        """Create TypeScript-specific files"""
        files = self._create_javascript_files(project_path, project_info)
        
        # tsconfig.json
        tsconfig_content = self._get_tsconfig(project_info)
        with open(os.path.join(project_path, 'tsconfig.json'), 'w') as f:
            f.write(tsconfig_content)
        files.append("⚙️ tsconfig.json")
        
        return files
    
    def _generate_ai_files(self, project_path: str, project_info: dict, prompt: str) -> list:
        """Generate AI-assisted files based on the prompt"""
        files = []
        
        # This would integrate with your LLaMA/AI system
        # For now, creating placeholder files with AI instructions
        
        ai_instructions_file = os.path.join(project_path, 'AI_INSTRUCTIONS.md')
        with open(ai_instructions_file, 'w') as f:
            f.write(f"""# AI Generation Instructions

## Original Prompt
{prompt}

## Project Analysis
- Type: {project_info['type']}
- Language: {project_info['language']}
- Features: {', '.join(project_info['features'])}

## Next AI Tasks
1. Generate detailed implementation based on prompt
2. Create specific functionality modules
3. Add error handling and validation
4. Generate comprehensive tests
5. Create documentation

## Files to Generate
- Core application logic
- Configuration files
- Test files
- Documentation
- Deployment scripts
""")
        files.append("🤖 AI_INSTRUCTIONS.md")
        
        return files
    
    def _create_run_scripts(self, project_path: str, project_info: dict) -> list:
        """Create run and build scripts"""
        files = []
        language = project_info['language']
        
        if language == 'python':
            # run.py
            run_content = f"""#!/usr/bin/env python3
'''
{project_info.get('description', 'Project runner')}
'''

import sys
import os

def main():
    print("🚀 Starting {os.path.basename(os.getcwd())}...")
    
    # Add your startup logic here
    from main import main as app_main
    app_main()

if __name__ == "__main__":
    main()
"""
            with open(os.path.join(project_path, 'run.py'), 'w') as f:
                f.write(run_content)
            files.append("🚀 run.py")
            
        elif language == 'javascript':
            # Create npm scripts in package.json (already done)
            pass
        
        # Universal run script
        if os.name == 'posix':  # Unix-like systems
            run_script = os.path.join(project_path, 'run.sh')
            with open(run_script, 'w') as f:
                if language == 'python':
                    f.write("#!/bin/bash\npython run.py\n")
                elif language == 'javascript':
                    f.write("#!/bin/bash\nnpm start\n")
            os.chmod(run_script, 0o755)
            files.append("🔧 run.sh")
        
        return files
    
    def _get_python_requirements(self, project_info: dict) -> str:
        """Generate Python requirements based on project type"""
        base_requirements = []
        
        if project_info['type'] == 'web_backend':
            base_requirements.extend(['flask', 'requests', 'python-dotenv'])
        elif project_info['type'] == 'data_science':
            base_requirements.extend(['pandas', 'numpy', 'matplotlib', 'jupyter'])
        elif project_info['type'] == 'automation':
            base_requirements.extend(['requests', 'beautifulsoup4', 'selenium'])
        elif project_info['type'] == 'game':
            base_requirements.extend(['pygame'])
        elif project_info['type'] == 'desktop':
            base_requirements.extend(['tkinter'])
        
        if 'database' in project_info['features']:
            base_requirements.append('sqlite3')
        if 'testing' in project_info['features']:
            base_requirements.extend(['pytest', 'pytest-cov'])
        
        return '\n'.join(base_requirements)
    
    def _get_python_main(self, project_info: dict) -> str:
        """Generate main Python file"""
        return f'''#!/usr/bin/env python3
"""
{project_info.get('description', 'Main application file')}

Project Type: {project_info['type']}
Language: {project_info['language']}
Features: {', '.join(project_info['features'])}
"""

def main():
    """Main application entry point"""
    print("🚀 Starting application...")
    
    # TODO: Implement your application logic here
    # This is generated based on your prompt: {project_info.get('description', '')}
    
    print("✅ Application setup complete!")

if __name__ == "__main__":
    main()
'''
    
    def _get_package_json(self, project_info: dict) -> str:
        """Generate package.json for JavaScript projects"""
        return json.dumps({
            "name": project_info.get('suggested_name', 'new-project'),
            "version": "1.0.0",
            "description": project_info.get('description', ''),
            "main": "index.js",
            "scripts": {
                "start": "node index.js",
                "dev": "nodemon index.js",
                "test": "jest"
            },
            "dependencies": self._get_js_dependencies(project_info),
            "devDependencies": {
                "nodemon": "^2.0.0",
                "jest": "^28.0.0"
            }
        }, indent=2)
    
    def _get_js_dependencies(self, project_info: dict) -> dict:
        """Get JavaScript dependencies based on project type"""
        deps = {}
        
        if project_info['type'] == 'web_backend':
            deps.update({"express": "^4.18.0", "cors": "^2.8.5"})
        elif project_info['type'] == 'web_frontend':
            deps.update({"react": "^18.0.0", "react-dom": "^18.0.0"})
        
        return deps
    
    def _get_readme(self, project_info: dict) -> str:
        """Generate README.md"""
        return f"""# {project_info.get('suggested_name', 'New Project')}

{project_info.get('description', 'AI-generated project')}

## Project Details
- **Type**: {project_info['type']}
- **Language**: {project_info['language']}
- **Features**: {', '.join(project_info['features']) if project_info['features'] else 'Basic setup'}

## Getting Started

### Installation
```bash
# Clone or download this project
cd {project_info.get('suggested_name', 'project')}

# Install dependencies
{'pip install -r requirements.txt' if project_info['language'] == 'python' else 'npm install'}
```

### Running
```bash
# Run the application
{'python run.py' if project_info['language'] == 'python' else 'npm start'}
```

## Project Structure
```
{project_info.get('suggested_name', 'project')}/
├── src/           # Source code
├── tests/         # Test files
├── docs/          # Documentation
└── README.md      # This file
```

## Next Steps
{chr(10).join(f"- {step}" for step in project_info.get('next_steps', ['Implement core functionality', 'Add tests', 'Deploy']))}

---
*Generated by GRINGO AI Assistant*
"""
    
    def _get_tsconfig(self, project_info: dict) -> str:
        """Generate TypeScript configuration"""
        return json.dumps({
            "compilerOptions": {
                "target": "ES2020",
                "module": "commonjs",
                "outDir": "./dist",
                "rootDir": "./src",
                "strict": True,
                "esModuleInterop": True,
                "skipLibCheck": True,
                "forceConsistentCasingInFileNames": True
            },
            "include": ["src/**/*"],
            "exclude": ["node_modules", "dist"]
        }, indent=2)
    
    def _get_next_steps(self, project_type: str, language: str) -> list:
        """Get recommended next steps for the project"""
        steps = [
            "Review and customize the generated code",
            "Install dependencies",
            "Implement core functionality",
            "Add comprehensive testing",
            "Set up CI/CD pipeline"
        ]
        
        if project_type == 'web_backend':
            steps.insert(2, "Set up database schema")
            steps.insert(3, "Implement API endpoints")
        elif project_type == 'web_frontend':
            steps.insert(2, "Design UI components")
            steps.insert(3, "Implement routing")
        elif project_type == 'data_science':
            steps.insert(2, "Prepare and clean data")
            steps.insert(3, "Build analysis models")
        
        return steps
    
    def _save_project_to_db(self, name: str, project_info: dict, path: str) -> int:
        """Save project information to database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO projects (name, type, description, path, metadata)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            name,
            project_info['type'],
            project_info.get('description', ''),
            path,
            json.dumps(project_info)
        ))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def list_projects(self) -> list:
        """List all projects"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT id, name, type, description, path, status, created_at
            FROM projects
            ORDER BY last_updated DESC
        ''')
        
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT path, type, metadata FROM projects WHERE name = ?', (project_name,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            return {"error": "Project not found"}
        
        project_path, project_type, metadata_json = result
        metadata = json.loads(metadata_json)
        language = metadata.get('language', 'python')
        
        # Determine run command
        if language == 'python':
            run_file = os.path.join(project_path, 'run.py')
            if os.path.exists(run_file):
                cmd = ['python', run_file]
            else:
                cmd = ['python', 'main.py']
        elif language == 'javascript':
            cmd = ['npm', 'start']
        else:
            return {"error": f"Don't know how to run {language} projects"}
        
        try:
            # Change to project directory and run
            result = subprocess.run(
                cmd,
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=30
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
            return {"error": f"Failed to run project: {e}"}
    
    def export_project(self, project_name: str, export_path: str = None) -> str:
        """Export project as zip file"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT path FROM projects WHERE name = ?', (project_name,))
        result = cursor.fetchone()
        conn.close()
        
        if not result:
            raise ValueError("Project not found")
        
        project_path = result[0]
        
        if not export_path:
            export_path = f"{project_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip"
        
        with zipfile.ZipFile(export_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(project_path):
                for file in files:
                    file_path = os.path.join(root, file)
                    archive_name = os.path.relpath(file_path, project_path)
                    zipf.write(file_path, archive_name)
        
        return export_path
