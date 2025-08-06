#!/usr/bin/env python3
"""
GRINGO Personal OS Setup & Check
Verify and initialize the system
"""

import os
import sys
import subprocess
import json
import sqlite3
from datetime import datetime

def check_dependencies():
    """Check if all required dependencies are available"""
    print("🔍 Checking dependencies...")
    
    required_modules = [
        'streamlit', 'requests', 'psutil', 'schedule'
    ]
    
    missing = []
    for module in required_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError:
            print(f"  ❌ {module} - MISSING")
            missing.append(module)
    
    if missing:
        print(f"\n📦 Install missing packages with:")
        print(f"pip install {' '.join(missing)}")
        return False
    
    return True

def check_ollama():
    """Check if Ollama is running"""
    print("\n🦙 Checking Ollama...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=3)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"  ✅ Ollama running with {len(models)} models")
            
            # Check for llama3
            llama3_available = any("llama3" in model.get("name", "") for model in models)
            if llama3_available:
                print("  ✅ LLaMA3 model available")
            else:
                print("  ⚠️  LLaMA3 model not found")
                print("     Run: ollama pull llama3")
            
            return True
        else:
            print("  ❌ Ollama not responding")
            return False
    except Exception as e:
        print(f"  ❌ Ollama not available: {e}")
        print("     Start with: ollama serve")
        return False

def setup_workspace():
    """Create and initialize the workspace"""
    print("\n📁 Setting up workspace...")
    
    # Create workspace directory
    workspace_path = os.path.expanduser("~/gringo_workspace")
    os.makedirs(workspace_path, exist_ok=True)
    print(f"  ✅ Workspace: {workspace_path}")
    
    # Create subdirectories
    subdirs = ['uploads', 'downloads', 'projects', 'backups', 'temp']
    for subdir in subdirs:
        subdir_path = os.path.join(workspace_path, subdir)
        os.makedirs(subdir_path, exist_ok=True)
        print(f"  ✅ Created: {subdir}/")
    
    return workspace_path

def setup_databases(workspace_path):
    """Initialize the SQLite databases"""
    print("\n💾 Setting up databases...")
    
    # Memory database
    memory_db = os.path.join(workspace_path, "memory.db")
    conn = sqlite3.connect(memory_db)
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memory (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value TEXT,
            category TEXT DEFAULT 'general',
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            filepath TEXT UNIQUE,
            filename TEXT,
            file_type TEXT,
            size INTEGER,
            last_modified DATETIME,
            ai_summary TEXT,
            tags TEXT,
            importance INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            task_type TEXT,
            target_files TEXT,
            schedule_pattern TEXT,
            last_run DATETIME,
            next_run DATETIME,
            status TEXT DEFAULT 'active',
            results TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    conn.close()
    
    print(f"  ✅ Memory database: {memory_db}")
    
    # Initialize memory.json if it doesn't exist
    memory_json = os.path.join(os.getcwd(), "memory.json")
    if not os.path.exists(memory_json):
        with open(memory_json, "w") as f:
            json.dump([], f)
        print(f"  ✅ Memory JSON: {memory_json}")

def create_agent_directories():
    """Create agent-related directories"""
    print("\n🤖 Setting up AI agents...")
    
    current_dir = os.getcwd()
    agents_dir = os.path.join(current_dir, "agents")
    
    if not os.path.exists(agents_dir):
        os.makedirs(agents_dir)
        print(f"  ✅ Created agents directory: {agents_dir}")
    
    # Create __init__.py if it doesn't exist
    init_file = os.path.join(agents_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# GRINGO AI Agents\n")
        print("  ✅ Created agents __init__.py")

def verify_files():
    """Verify that all core GRINGO files exist"""
    print("\n📋 Verifying GRINGO files...")
    
    required_files = [
        'gringo_unified_cockpit.py',
        'launch_gringo.py',
        'ollama_chat_ui.py'
    ]
    
    missing_files = []
    for filename in required_files:
        if os.path.exists(filename):
            print(f"  ✅ {filename}")
        else:
            print(f"  ❌ {filename} - MISSING")
            missing_files.append(filename)
    
    return len(missing_files) == 0

def main():
    """Main setup function"""
    print("🤖 GRINGO Personal OS Setup")
    print("=" * 50)
    
    # Check dependencies
    deps_ok = check_dependencies()
    
    # Check Ollama
    ollama_ok = check_ollama()
    
    # Setup workspace
    workspace_path = setup_workspace()
    
    # Setup databases
    setup_databases(workspace_path)
    
    # Create agent directories
    create_agent_directories()
    
    # Verify files
    files_ok = verify_files()
    
    # Final status
    print("\n" + "=" * 50)
    print("📊 Setup Summary:")
    
    if deps_ok:
        print("✅ Dependencies: OK")
    else:
        print("❌ Dependencies: MISSING")
    
    if ollama_ok:
        print("✅ Ollama: RUNNING")
    else:
        print("⚠️  Ollama: NOT RUNNING")
    
    if files_ok:
        print("✅ GRINGO Files: OK")
    else:
        print("❌ GRINGO Files: MISSING")
    
    print(f"✅ Workspace: {workspace_path}")
    
    if deps_ok and files_ok:
        print("\n🚀 Ready to launch GRINGO!")
        print("   Run: python launch_gringo.py")
        print("   Or:  python ollama_chat_ui.py")
        
        if not ollama_ok:
            print("\n💡 Don't forget to start Ollama:")
            print("   Run: ollama serve")
            print("   And: ollama pull llama3")
    else:
        print("\n🔧 Please fix the issues above before launching GRINGO")
    
    print("\n🔒 100% Local & Private AI System")
    return 0

if __name__ == "__main__":
    sys.exit(main())
