#!/usr/bin/env python3
"""
GRINGO AI OS Setup Script

This script helps users set up GRINGO AI OS with all dependencies and optional components.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path


class GringoSetup:
    def __init__(self):
        self.system = platform.system()
        self.python_version = sys.version_info
        self.requirements_met = True
        
    def check_python_version(self):
        """Check if Python version meets requirements."""
        print("🐍 Checking Python version...")
        if self.python_version < (3, 8):
            print(f"❌ Python 3.8+ required, found {self.python_version.major}.{self.python_version.minor}")
            self.requirements_met = False
            return False
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} detected")
        return True
    
    def install_python_deps(self):
        """Install Python dependencies."""
        print("\n📦 Installing Python dependencies...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
            print("✅ Python dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install Python dependencies: {e}")
            return False
    
    def check_ollama(self):
        """Check if Ollama is installed."""
        print("\n🤖 Checking Ollama installation...")
        try:
            result = subprocess.run(["ollama", "--version"], capture_output=True, text=True)
            if result.returncode == 0:
                print("✅ Ollama is installed")
                return True
        except FileNotFoundError:
            pass
        
        print("❌ Ollama not found")
        return False
    
    def install_ollama(self):
        """Install Ollama based on the operating system."""
        print("\n🚀 Installing Ollama...")
        
        if self.system == "Darwin":  # macOS
            print("Installing Ollama for macOS...")
            try:
                subprocess.check_call(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], shell=True)
                print("✅ Ollama installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install Ollama via script")
                print("💡 Please visit https://ollama.ai to install manually")
                return False
                
        elif self.system == "Linux":
            print("Installing Ollama for Linux...")
            try:
                subprocess.check_call(["curl", "-fsSL", "https://ollama.ai/install.sh", "|", "sh"], shell=True)
                print("✅ Ollama installed successfully")
                return True
            except subprocess.CalledProcessError:
                print("❌ Failed to install Ollama via script")
                print("💡 Please visit https://ollama.ai to install manually")
                return False
                
        elif self.system == "Windows":
            print("❌ Automatic Ollama installation not supported on Windows")
            print("💡 Please download from https://ollama.ai and install manually")
            return False
        
        else:
            print(f"❌ Unsupported operating system: {self.system}")
            return False
    
    def install_llama_model(self):
        """Install LLaMA3 model."""
        print("\n🧠 Installing LLaMA3 model...")
        try:
            subprocess.check_call(["ollama", "pull", "llama3"])
            print("✅ LLaMA3 model installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install LLaMA3 model: {e}")
            print("💡 You can install it later with: ollama pull llama3")
            return False
    
    def create_workspace_structure(self):
        """Create recommended workspace structure."""
        print("\n📁 Creating workspace structure...")
        
        workspace_dirs = [
            "gringo_workspace",
            "gringo_workspace/projects",
            "gringo_workspace/tools",
            "gringo_workspace/agents",
            "gringo_workspace/temp"
        ]
        
        for dir_path in workspace_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
        
        print("✅ Workspace structure created")
        return True
    
    def test_installation(self):
        """Test the installation by importing key modules."""
        print("\n🧪 Testing installation...")
        
        test_imports = [
            ("streamlit", "Streamlit"),
            ("pandas", "Pandas"),
            ("psutil", "Psutil"),
            ("requests", "Requests"),
        ]
        
        for module, name in test_imports:
            try:
                __import__(module)
                print(f"✅ {name} import successful")
            except ImportError:
                print(f"❌ {name} import failed")
                return False
        
        # Test Streamlit can start
        try:
            import streamlit as st
            print("✅ Streamlit is ready")
        except Exception as e:
            print(f"❌ Streamlit test failed: {e}")
            return False
        
        return True
    
    def display_next_steps(self):
        """Display next steps for the user."""
        print("\n" + "="*60)
        print("🎉 GRINGO AI OS Setup Complete!")
        print("="*60)
        print("\n📋 Next steps:")
        print("1. Start GRINGO:")
        print("   streamlit run ultimate_gringo.py --server.port 8504")
        print("\n2. Open your browser to:")
        print("   http://localhost:8504")
        print("\n3. If you installed Ollama, start the service:")
        print("   ollama serve")
        print("\n4. Create your first AI project using natural language!")
        print("\n💡 Tips:")
        print("   - Use the Project Creator to build complete applications")
        print("   - Try the Custom Tools section to create utility scripts")
        print("   - Explore the Agent Control panel for advanced workflows")
        print("   - All processing happens locally for privacy")
        
        print("\n📚 Documentation:")
        print("   - README.md - Quick start guide")
        print("   - CONTRIBUTING.md - Development guide")
        print("   - GitHub Issues - Report bugs or request features")
        
        print("\n🚀 Happy coding with GRINGO!")
    
    def run_setup(self):
        """Run the complete setup process."""
        print("🤖 Welcome to GRINGO AI OS Setup!")
        print("="*50)
        
        # Check Python version
        if not self.check_python_version():
            print("\n❌ Setup failed: Python version requirements not met")
            sys.exit(1)
        
        # Install Python dependencies
        if not self.install_python_deps():
            print("\n❌ Setup failed: Could not install Python dependencies")
            sys.exit(1)
        
        # Test Python installation
        if not self.test_installation():
            print("\n❌ Setup failed: Installation test failed")
            sys.exit(1)
        
        # Check for Ollama (optional)
        ollama_installed = self.check_ollama()
        if not ollama_installed:
            install_ollama = input("\n🤖 Install Ollama for AI features? (y/N): ").lower().strip()
            if install_ollama in ['y', 'yes']:
                if self.install_ollama():
                    # Try to install LLaMA3 model
                    install_model = input("📥 Install LLaMA3 model? (~4GB download) (y/N): ").lower().strip()
                    if install_model in ['y', 'yes']:
                        self.install_llama_model()
                else:
                    print("⚠️  You can install Ollama later for AI features")
            else:
                print("⚠️  Skipping Ollama installation - some AI features will be disabled")
        else:
            # Ollama is installed, check for LLaMA3
            try:
                result = subprocess.run(["ollama", "list"], capture_output=True, text=True)
                if "llama3" not in result.stdout:
                    install_model = input("📥 Install LLaMA3 model? (~4GB download) (y/N): ").lower().strip()
                    if install_model in ['y', 'yes']:
                        self.install_llama_model()
                else:
                    print("✅ LLaMA3 model already installed")
            except subprocess.CalledProcessError:
                print("⚠️  Could not check Ollama models")
        
        # Create workspace structure
        self.create_workspace_structure()
        
        # Display next steps
        self.display_next_steps()


def main():
    """Main setup function."""
    if len(sys.argv) > 1 and sys.argv[1] in ['-h', '--help']:
        print("GRINGO AI OS Setup Script")
        print("\nUsage: python setup.py")
        print("\nThis script will:")
        print("  - Check Python version requirements")
        print("  - Install Python dependencies")
        print("  - Optionally install Ollama and LLaMA3")
        print("  - Create workspace structure")
        print("  - Test the installation")
        return
    
    setup = GringoSetup()
    setup.run_setup()


if __name__ == "__main__":
    main()
