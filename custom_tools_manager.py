#!/usr/bin/env python3
"""
GRINGO Custom Tools Manager
Create, save, and run custom development tools
"""

import os
import json
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

class CustomToolsManager:
    def __init__(self, workspace_root: str):
        self.workspace_root = workspace_root
        self.tools_dir = os.path.join(workspace_root, "tools")
        self.tools_db = os.path.join(workspace_root, "custom_tools.json")
        self._init_directories()
        self._load_tools_db()
    
    def _init_directories(self):
        """Initialize tools directory structure"""
        categories = [
            "file_operations",
            "text_processing", 
            "data_analysis",
            "system_utilities",
            "web_tools",
            "automation",
            "testing",
            "monitoring"
        ]
        
        os.makedirs(self.tools_dir, exist_ok=True)
        for category in categories:
            os.makedirs(os.path.join(self.tools_dir, category), exist_ok=True)
    
    def _load_tools_db(self):
        """Load tools database"""
        if os.path.exists(self.tools_db):
            with open(self.tools_db, 'r') as f:
                self.tools = json.load(f)
        else:
            self.tools = {
                "tools": [],
                "categories": [
                    "file_operations",
                    "text_processing", 
                    "data_analysis",
                    "system_utilities",
                    "web_tools",
                    "automation",
                    "testing",
                    "monitoring"
                ]
            }
            self._save_tools_db()
    
    def _save_tools_db(self):
        """Save tools database"""
        with open(self.tools_db, 'w') as f:
            json.dump(self.tools, f, indent=2)
    
    def create_tool(self, name: str, description: str, category: str, 
                   language: str, code: str, args_schema: dict = None) -> dict:
        """Create a new custom tool"""
        
        # Generate filename
        safe_name = "".join(c for c in name if c.isalnum() or c in (' ', '-', '_')).rstrip()
        safe_name = safe_name.replace(' ', '_').lower()
        
        if language == 'python':
            filename = f"{safe_name}.py"
        elif language == 'javascript':
            filename = f"{safe_name}.js"
        elif language == 'bash':
            filename = f"{safe_name}.sh"
        else:
            filename = f"{safe_name}.txt"
        
        # Create file path
        file_path = os.path.join(self.tools_dir, category, filename)
        
        # Write code to file
        with open(file_path, 'w') as f:
            if language == 'python':
                f.write(f'#!/usr/bin/env python3\n"""\n{name}\n{description}\n"""\n\n{code}')
            elif language == 'bash':
                f.write(f'#!/bin/bash\n# {name}\n# {description}\n\n{code}')
            else:
                f.write(code)
        
        # Make executable if needed
        if language in ['python', 'bash']:
            os.chmod(file_path, 0o755)
        
        # Add to database
        tool_data = {
            "id": len(self.tools["tools"]) + 1,
            "name": name,
            "description": description,
            "category": category,
            "language": language,
            "filename": filename,
            "file_path": file_path,
            "args_schema": args_schema or {},
            "created_at": datetime.now().isoformat(),
            "usage_count": 0
        }
        
        self.tools["tools"].append(tool_data)
        self._save_tools_db()
        
        return tool_data
    
    def get_tools_by_category(self, category: str = None) -> list:
        """Get tools by category or all tools"""
        if category:
            return [tool for tool in self.tools["tools"] if tool["category"] == category]
        return self.tools["tools"]
    
    def run_tool(self, tool_id: int, args: list = None) -> dict:
        """Run a custom tool"""
        tool = next((t for t in self.tools["tools"] if t["id"] == tool_id), None)
        if not tool:
            return {"error": "Tool not found"}
        
        file_path = tool["file_path"]
        if not os.path.exists(file_path):
            return {"error": "Tool file not found"}
        
        try:
            if tool["language"] == "python":
                cmd = ["python", file_path] + (args or [])
            elif tool["language"] == "javascript":
                cmd = ["node", file_path] + (args or [])
            elif tool["language"] == "bash":
                cmd = ["bash", file_path] + (args or [])
            else:
                return {"error": "Unsupported language"}
            
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30,
                cwd=os.path.dirname(file_path)
            )
            
            # Update usage count
            for t in self.tools["tools"]:
                if t["id"] == tool_id:
                    t["usage_count"] += 1
                    break
            self._save_tools_db()
            
            return {
                "success": True,
                "output": result.stdout,
                "errors": result.stderr,
                "return_code": result.returncode
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Tool execution timed out"}
        except Exception as e:
            return {"error": f"Failed to run tool: {e}"}
    
    def delete_tool(self, tool_id: int) -> bool:
        """Delete a custom tool"""
        tool = next((t for t in self.tools["tools"] if t["id"] == tool_id), None)
        if not tool:
            return False
        
        # Remove file
        if os.path.exists(tool["file_path"]):
            os.remove(tool["file_path"])
        
        # Remove from database
        self.tools["tools"] = [t for t in self.tools["tools"] if t["id"] != tool_id]
        self._save_tools_db()
        
        return True
    
    def export_tool(self, tool_id: int) -> dict:
        """Export a tool for sharing"""
        tool = next((t for t in self.tools["tools"] if t["id"] == tool_id), None)
        if not tool:
            return {"error": "Tool not found"}
        
        # Read code
        with open(tool["file_path"], 'r') as f:
            code = f.read()
        
        export_data = {
            "name": tool["name"],
            "description": tool["description"],
            "category": tool["category"],
            "language": tool["language"],
            "code": code,
            "args_schema": tool["args_schema"],
            "exported_at": datetime.now().isoformat()
        }
        
        return export_data
    
    def import_tool(self, import_data: dict) -> dict:
        """Import a tool from export data"""
        return self.create_tool(
            name=import_data["name"],
            description=import_data["description"],
            category=import_data["category"],
            language=import_data["language"],
            code=import_data["code"],
            args_schema=import_data.get("args_schema", {})
        )
    
    def get_tool_templates(self) -> dict:
        """Get predefined tool templates"""
        return {
            "file_organizer": {
                "name": "File Organizer",
                "description": "Organize files by extension into folders",
                "category": "file_operations",
                "language": "python",
                "code": '''import os
import shutil
from pathlib import Path

def organize_files(directory="."):
    """Organize files by extension"""
    directory = Path(directory)
    
    for file_path in directory.iterdir():
        if file_path.is_file():
            extension = file_path.suffix.lower()
            if extension:
                # Create folder for extension
                ext_folder = directory / extension[1:]  # Remove the dot
                ext_folder.mkdir(exist_ok=True)
                
                # Move file
                new_path = ext_folder / file_path.name
                shutil.move(str(file_path), str(new_path))
                print(f"Moved {file_path.name} to {ext_folder}")

if __name__ == "__main__":
    import sys
    target_dir = sys.argv[1] if len(sys.argv) > 1 else "."
    organize_files(target_dir)
    print("File organization complete!")
''',
                "args_schema": {"directory": "Target directory (optional)"}
            },
            
            "text_processor": {
                "name": "Text Processor", 
                "description": "Process text files with various operations",
                "category": "text_processing",
                "language": "python",
                "code": '''import sys
import re

def process_text(file_path, operation="count"):
    """Process text file with various operations"""
    
    with open(file_path, 'r') as f:
        content = f.read()
    
    if operation == "count":
        lines = len(content.split('\\n'))
        words = len(content.split())
        chars = len(content)
        print(f"Lines: {lines}, Words: {words}, Characters: {chars}")
    
    elif operation == "uppercase":
        result = content.upper()
        output_path = file_path.replace('.txt', '_upper.txt')
        with open(output_path, 'w') as f:
            f.write(result)
        print(f"Uppercase version saved to {output_path}")
    
    elif operation == "remove_duplicates":
        lines = content.split('\\n')
        unique_lines = list(dict.fromkeys(lines))
        result = '\\n'.join(unique_lines)
        output_path = file_path.replace('.txt', '_unique.txt')
        with open(output_path, 'w') as f:
            f.write(result)
        print(f"Deduplicated version saved to {output_path}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python text_processor.py <file_path> [operation]")
        print("Operations: count, uppercase, remove_duplicates")
        sys.exit(1)
    
    file_path = sys.argv[1]
    operation = sys.argv[2] if len(sys.argv) > 2 else "count"
    process_text(file_path, operation)
''',
                "args_schema": {"file_path": "Path to text file", "operation": "count|uppercase|remove_duplicates"}
            },
            
            "system_monitor": {
                "name": "System Monitor",
                "description": "Monitor system resources and processes",
                "category": "system_utilities", 
                "language": "python",
                "code": '''import psutil
import time

def monitor_system(duration=60):
    """Monitor system for specified duration"""
    
    print("System Monitoring Started...")
    print(f"Monitoring for {duration} seconds")
    print("-" * 50)
    
    start_time = time.time()
    
    while time.time() - start_time < duration:
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory usage
        memory = psutil.virtual_memory()
        memory_percent = memory.percent
        
        # Disk usage
        disk = psutil.disk_usage('/')
        disk_percent = (disk.used / disk.total) * 100
        
        print(f"CPU: {cpu_percent:5.1f}% | Memory: {memory_percent:5.1f}% | Disk: {disk_percent:5.1f}%", end='\\r')
        time.sleep(1)
    
    print("\\nMonitoring complete!")

if __name__ == "__main__":
    import sys
    duration = int(sys.argv[1]) if len(sys.argv) > 1 else 60
    monitor_system(duration)
''',
                "args_schema": {"duration": "Monitoring duration in seconds (default: 60)"}
            },
            
            "backup_creator": {
                "name": "Backup Creator",
                "description": "Create compressed backups of directories",
                "category": "automation",
                "language": "python", 
                "code": '''import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def create_backup(source_dir, backup_dir="./backups"):
    """Create a timestamped backup of a directory"""
    
    source_path = Path(source_dir)
    backup_path = Path(backup_dir)
    
    if not source_path.exists():
        print(f"Error: Source directory {source_dir} does not exist")
        return
    
    # Create backup directory
    backup_path.mkdir(exist_ok=True)
    
    # Generate backup filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.name}_backup_{timestamp}.zip"
    backup_file = backup_path / backup_name
    
    # Create zip backup
    with zipfile.ZipFile(backup_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(source_path):
            for file in files:
                file_path = Path(root) / file
                arc_path = file_path.relative_to(source_path.parent)
                zipf.write(file_path, arc_path)
    
    print(f"Backup created: {backup_file}")
    print(f"Size: {backup_file.stat().st_size / (1024*1024):.2f} MB")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python backup_creator.py <source_directory> [backup_directory]")
        sys.exit(1)
    
    source = sys.argv[1]
    backup_dir = sys.argv[2] if len(sys.argv) > 2 else "./backups"
    create_backup(source, backup_dir)
''',
                "args_schema": {"source_dir": "Directory to backup", "backup_dir": "Backup location (optional)"}
            }
        }

def get_example_tools() -> list:
    """Get list of example tools to create"""
    manager = CustomToolsManager("/tmp")  # Dummy instance for templates
    templates = manager.get_tool_templates()
    
    return [
        {
            "name": template["name"],
            "description": template["description"],
            "category": template["category"],
            "language": template["language"],
            "code": template["code"]
        }
        for template in templates.values()
    ]
