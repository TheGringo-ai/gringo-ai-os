#!/usr/bin/env python3
"""
Documentation Generator Agent - Auto-generates docs and README files
"""

import json
import sys
import os
import ast
from datetime import datetime

class DocGeneratorAgent:
    def __init__(self):
        self.name = "doc_gen"
        
    def scan_project_structure(self, workspace: str) -> dict:
        """Scan project for structure and components"""
        
        structure = {
            "python_files": [],
            "directories": [],
            "entry_points": [],
            "test_files": [],
            "config_files": []
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            # Track directories
            rel_root = os.path.relpath(root, workspace)
            if rel_root != '.':
                structure["directories"].append(rel_root)
            
            for file in files:
                file_path = os.path.join(root, file)
                rel_path = os.path.relpath(file_path, workspace)
                
                if file.endswith('.py'):
                    structure["python_files"].append(rel_path)
                    
                    # Check if it's an entry point
                    if file in ['main.py', 'app.py', 'server.py', 'run.py']:
                        structure["entry_points"].append(rel_path)
                    
                    # Check if it's a test file
                    if 'test_' in file or file.endswith('_test.py'):
                        structure["test_files"].append(rel_path)
                
                elif file in ['requirements.txt', 'setup.py', 'pyproject.toml', 'Pipfile']:
                    structure["config_files"].append(rel_path)
        
        return structure
    
    def extract_module_info(self, file_path: str) -> dict:
        """Extract information from a Python module"""
        
        info = {
            "file": file_path,
            "docstring": None,
            "classes": [],
            "functions": [],
            "imports": []
        }
        
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Get module docstring
            info["docstring"] = ast.get_docstring(tree)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    info["classes"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "methods": [m.name for m in node.body if isinstance(m, ast.FunctionDef)]
                    })
                
                elif isinstance(node, ast.FunctionDef) and node.col_offset == 0:  # Top-level functions
                    info["functions"].append({
                        "name": node.name,
                        "docstring": ast.get_docstring(node),
                        "args": [arg.arg for arg in node.args.args]
                    })
                
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        info["imports"].append(alias.name)
                
                elif isinstance(node, ast.ImportFrom):
                    if node.module:
                        info["imports"].append(node.module)
                        
        except Exception as e:
            info["error"] = str(e)
            
        return info
    
    def generate_api_docs(self, workspace: str, python_files: list) -> str:
        """Generate API documentation"""
        
        docs = "# API Documentation\n\n"
        docs += f"*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n\n"
        
        for py_file in python_files:
            if 'test_' in py_file or '__pycache__' in py_file:
                continue
                
            file_path = os.path.join(workspace, py_file)
            module_info = self.extract_module_info(file_path)
            
            if module_info.get("error"):
                continue
                
            docs += f"## {py_file}\n\n"
            
            if module_info["docstring"]:
                docs += f"{module_info['docstring']}\n\n"
            
            # Document classes
            if module_info["classes"]:
                docs += "### Classes\n\n"
                for cls in module_info["classes"]:
                    docs += f"#### `{cls['name']}`\n\n"
                    if cls["docstring"]:
                        docs += f"{cls['docstring']}\n\n"
                    if cls["methods"]:
                        docs += f"**Methods:** {', '.join(cls['methods'])}\n\n"
            
            # Document functions
            if module_info["functions"]:
                docs += "### Functions\n\n"
                for func in module_info["functions"]:
                    if func["name"] == "main":
                        continue
                    docs += f"#### `{func['name']}({', '.join(func['args'])})`\n\n"
                    if func["docstring"]:
                        docs += f"{func['docstring']}\n\n"
            
            docs += "---\n\n"
        
        return docs
    
    def generate_readme(self, workspace: str, structure: dict) -> str:
        """Generate comprehensive README"""
        
        project_name = os.path.basename(os.path.abspath(workspace))
        
        readme = f"# {project_name}\n\n"
        readme += "*Auto-generated project documentation*\n\n"
        
        # Project overview
        readme += "## Overview\n\n"
        readme += f"This project contains {len(structure['python_files'])} Python files "
        readme += f"with {len(structure['test_files'])} test files.\n\n"
        
        # Entry points
        if structure["entry_points"]:
            readme += "## Quick Start\n\n"
            readme += "### Entry Points\n\n"
            for entry in structure["entry_points"]:
                readme += f"- `{entry}` - Main application entry point\n"
            readme += "\n"
            
            readme += "### Running the Application\n\n"
            readme += "```bash\n"
            readme += f"python3 {structure['entry_points'][0]}\n"
            readme += "```\n\n"
        
        # Project structure
        readme += "## Project Structure\n\n"
        readme += "```\n"
        
        # Sort files and directories for better presentation
        all_items = structure["python_files"] + structure["config_files"]
        all_items.sort()
        
        for item in all_items:
            readme += f"{item}\n"
        
        readme += "```\n\n"
        
        # Development setup
        readme += "## Development\n\n"
        
        if structure["test_files"]:
            readme += "### Running Tests\n\n"
            readme += "```bash\n"
            readme += "python3 -m pytest\n"
            readme += "# or run individual test files:\n"
            for test_file in structure["test_files"][:3]:  # Show first 3
                readme += f"python3 {test_file}\n"
            readme += "```\n\n"
        
        # Requirements
        if any('requirements.txt' in f for f in structure["config_files"]):
            readme += "### Installation\n\n"
            readme += "```bash\n"
            readme += "pip install -r requirements.txt\n"
            readme += "```\n\n"
        
        readme += f"## Documentation\n\n"
        readme += f"- **Files:** {len(structure['python_files'])} Python modules\n"
        readme += f"- **Tests:** {len(structure['test_files'])} test files\n"
        readme += f"- **Directories:** {len(structure['directories'])} subdirectories\n\n"
        
        readme += "*Generated automatically by Doc Generator Agent*\n"
        
        return readme

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = DocGeneratorAgent()
        
        print(f"📚 Doc Generator Agent: Creating documentation...")
        
        workspace = task_data.get('workspace', '.')
        doc_format = task_data.get('format', 'markdown')
        
        structure = agent.scan_project_structure(workspace)
        readme_content = agent.generate_readme(workspace, structure)
        api_docs = agent.generate_api_docs(workspace, structure['python_files'])
        
        # Write documentation files
        docs_created = []
        
        try:
            with open(os.path.join(workspace, 'README.md'), 'w') as f:
                f.write(readme_content)
            docs_created.append('README.md')
            
            with open(os.path.join(workspace, 'API_DOCS.md'), 'w') as f:
                f.write(api_docs)
            docs_created.append('API_DOCS.md')
            
        except Exception as e:
            print(f"Warning: Could not write docs: {e}")
        
        result = {
            "project_structure": structure,
            "documentation_created": docs_created,
            "format": doc_format,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Documentation generation completed")
        print(f"   📄 Files documented: {len(structure['python_files'])}")
        print(f"   📝 Docs created: {', '.join(docs_created)}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Documentation generation failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
