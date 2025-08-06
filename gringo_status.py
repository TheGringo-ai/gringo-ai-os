#!/usr/bin/env python3
"""
GRINGO Status and Quick Actions
"""

import subprocess
import sys
import os
import requests
import time

def check_gringo_status():
    """Check if GRINGO is running and get status"""
    
    print("🤖 GRINGO Personal OS Status Check")
    print("=" * 40)
    
    # Check if Streamlit is running on common ports
    ports_to_check = [8501, 8502, 8503]
    running_instances = []
    
    for port in ports_to_check:
        try:
            response = requests.get(f"http://localhost:{port}/_stcore/health", timeout=2)
            if response.status_code == 200:
                running_instances.append(port)
        except:
            pass
    
    if running_instances:
        print(f"✅ GRINGO is running on ports: {', '.join(map(str, running_instances))}")
        for port in running_instances:
            print(f"   🌐 http://localhost:{port}")
    else:
        print("❌ GRINGO is not running")
    
    # Check Ollama status
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            models = response.json().get("models", [])
            print(f"✅ Ollama is running with {len(models)} models")
            
            llama3_available = any("llama3" in model.get("name", "") for model in models)
            if llama3_available:
                print("   🦙 LLaMA3 model available")
            else:
                print("   ⚠️  LLaMA3 model not found - run: ollama pull llama3")
        else:
            print("❌ Ollama not responding")
    except:
        print("❌ Ollama not running - start with: ollama serve")
    
    # Check workspace
    workspace = os.path.expanduser("~/gringo_workspace")
    if os.path.exists(workspace):
        print(f"✅ Workspace exists: {workspace}")
        
        # Count projects
        projects_dir = os.path.join(workspace, "projects")
        if os.path.exists(projects_dir):
            projects = [d for d in os.listdir(projects_dir) if os.path.isdir(os.path.join(projects_dir, d))]
            print(f"   📁 Projects: {len(projects)}")
        else:
            print("   📁 No projects directory yet")
    else:
        print(f"⚠️  Workspace not found: {workspace}")
    
    return running_instances

def quick_actions():
    """Show quick action options"""
    
    running_instances = check_gringo_status()
    
    print("\n🚀 Quick Actions:")
    print("1. 🌐 Open GRINGO in browser")
    print("2. 🆕 Create a test project")
    print("3. 💻 Test terminal command")
    print("4. 🤖 Test AI chat")
    print("5. 📁 Open workspace folder")
    print("6. 🔄 Restart GRINGO")
    print("7. ❌ Exit")
    
    try:
        choice = input("\nSelect action (1-7): ").strip()
        
        if choice == "1":
            if running_instances:
                port = running_instances[0]
                print(f"🌐 Open http://localhost:{port} in your browser")
                try:
                    import webbrowser
                    webbrowser.open(f"http://localhost:{port}")
                except:
                    pass
            else:
                print("❌ GRINGO is not running. Start it first.")
        
        elif choice == "2":
            print("🆕 Creating test project...")
            workspace = os.path.expanduser("~/gringo_workspace")
            projects_dir = os.path.join(workspace, "projects")
            os.makedirs(projects_dir, exist_ok=True)
            
            test_project = os.path.join(projects_dir, "test_project")
            os.makedirs(test_project, exist_ok=True)
            
            with open(os.path.join(test_project, "main.py"), "w") as f:
                f.write('''#!/usr/bin/env python3
"""
Test project created by GRINGO
"""

def main():
    print("Hello from GRINGO test project!")
    print("🤖 This project was created by your AI assistant")

if __name__ == "__main__":
    main()
''')
            
            print(f"✅ Test project created: {test_project}")
            print("   📄 main.py created")
            
        elif choice == "3":
            print("💻 Testing terminal command...")
            try:
                result = subprocess.run(["python", "--version"], capture_output=True, text=True)
                print(f"✅ Command executed: {result.stdout.strip()}")
            except Exception as e:
                print(f"❌ Command failed: {e}")
        
        elif choice == "4":
            print("🤖 Testing AI chat...")
            try:
                response = requests.post(
                    "http://localhost:11434/api/generate",
                    json={"model": "llama3", "prompt": "Say hello in exactly 5 words"},
                    stream=True,
                    timeout=10
                )
                
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            full_response += data.get("response", "")
                        except:
                            continue
                
                print(f"🤖 AI Response: {full_response.strip()}")
                
            except Exception as e:
                print(f"❌ AI chat failed: {e}")
                print("💡 Make sure Ollama is running: ollama serve")
        
        elif choice == "5":
            workspace = os.path.expanduser("~/gringo_workspace")
            print(f"📁 Workspace: {workspace}")
            try:
                if sys.platform == "darwin":  # macOS
                    subprocess.run(["open", workspace])
                elif sys.platform == "win32":  # Windows
                    subprocess.run(["explorer", workspace])
                else:  # Linux
                    subprocess.run(["xdg-open", workspace])
            except:
                print("Open manually in your file manager")
        
        elif choice == "6":
            print("🔄 Restarting GRINGO...")
            print("To restart:")
            print("1. Press Ctrl+C in the terminal running GRINGO")
            print("2. Run: python smart_launcher.py")
        
        elif choice == "7":
            print("👋 Goodbye!")
            return
        
        else:
            print("❌ Invalid choice")
        
        # Ask if user wants to continue
        if input("\nPress Enter to continue or 'q' to quit: ").strip().lower() == 'q':
            return
        
        quick_actions()  # Recursive call to show menu again
        
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
        return

def main():
    """Main function"""
    quick_actions()

if __name__ == "__main__":
    main()
