#!/usr/bin/env python3
"""
GRINGO Personal OS - Smart Launcher
Detects available components and launches the best version
"""

import os
import sys
import importlib
import subprocess

def check_module(module_name):
    """Check if a module is available"""
    try:
        importlib.import_module(module_name)
        return True
    except ImportError:
        return False

def install_missing_modules():
    """Install missing required modules"""
    required_modules = {
        'streamlit': 'streamlit',
        'requests': 'requests', 
        'psutil': 'psutil',
        'schedule': 'schedule'
    }
    
    missing = []
    for module, package in required_modules.items():
        if not check_module(module):
            missing.append(package)
    
    if missing:
        print(f"📦 Installing missing packages: {', '.join(missing)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing)
            print("✅ Installation complete!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Installation failed: {e}")
            return False
    
    return True

def launch_gringo():
    """Launch the best available version of GRINGO"""
    
    print("🤖 GRINGO Personal OS Smart Launcher")
    print("=" * 40)
    
    # Check current directory
    current_dir = os.getcwd()
    print(f"📁 Working directory: {current_dir}")
    
    # Check for required files
    available_versions = []
    
    if os.path.exists("simple_gringo.py"):
        available_versions.append(("Simple GRINGO", "simple_gringo.py", "Basic functionality, minimal dependencies"))
    
    if os.path.exists("ollama_chat_ui.py"):
        available_versions.append(("Enhanced Chat UI", "ollama_chat_ui.py", "Enhanced chat with project integration"))
    
    if os.path.exists("gringo_unified_cockpit.py"):
        # Check if all dependencies are available for the full version
        complex_modules = ['schedule', 'psutil']
        complex_ready = all(check_module(mod) for mod in complex_modules)
        
        if complex_ready:
            available_versions.append(("Full GRINGO Cockpit", "gringo_unified_cockpit.py", "Complete feature set"))
        else:
            print(f"⚠️  Full cockpit requires: {', '.join(mod for mod in complex_modules if not check_module(mod))}")
    
    if not available_versions:
        print("❌ No GRINGO versions found!")
        return False
    
    print(f"\n🚀 Available GRINGO versions:")
    for i, (name, file, desc) in enumerate(available_versions, 1):
        print(f"  {i}. {name} ({file})")
        print(f"     {desc}")
    
    # Auto-select best version or let user choose
    if len(available_versions) == 1:
        selected_version = available_versions[0]
        print(f"\n🎯 Auto-launching: {selected_version[0]}")
    else:
        print(f"\n🎯 Recommended: {available_versions[-1][0]} (most features)")
        
        try:
            choice = input(f"\nSelect version (1-{len(available_versions)}) or press Enter for recommended: ").strip()
            
            if choice == "":
                selected_version = available_versions[-1]  # Most advanced
            else:
                idx = int(choice) - 1
                if 0 <= idx < len(available_versions):
                    selected_version = available_versions[idx]
                else:
                    selected_version = available_versions[-1]
        except (ValueError, KeyboardInterrupt):
            selected_version = available_versions[-1]
    
    # Install missing modules if needed
    if not install_missing_modules():
        print("⚠️  Some modules missing, launching simple version...")
        selected_version = next((v for v in available_versions if v[1] == "simple_gringo.py"), available_versions[0])
    
    # Launch selected version
    print(f"\n🚀 Launching {selected_version[0]}...")
    print(f"📁 File: {selected_version[1]}")
    print(f"🌐 Will open browser to: http://localhost:8501")
    print(f"🛑 Press Ctrl+C to stop")
    print("-" * 40)
    
    try:
        # Determine port based on version
        if "simple" in selected_version[1]:
            port = "8503"
        else:
            port = "8501"
        
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            selected_version[1],
            "--server.port", port,
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 GRINGO Personal OS stopped")
        return True
    except Exception as e:
        print(f"❌ Launch failed: {e}")
        return False

def main():
    """Main launcher function"""
    try:
        success = launch_gringo()
        return 0 if success else 1
    except Exception as e:
        print(f"❌ Launcher error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
