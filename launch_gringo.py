#!/usr/bin/env python3
"""
GRINGO Personal OS Launcher
Simple entry point for the unified cockpit
"""

import sys
import os
import subprocess

def main():
    print("🤖 Starting GRINGO Personal OS...")
    print("🔒 100% Local AI-Powered Assistant")
    print("=" * 50)
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cockpit_path = os.path.join(script_dir, "gringo_unified_cockpit.py")
    
    # Check if the cockpit exists
    if not os.path.exists(cockpit_path):
        print(f"❌ Error: {cockpit_path} not found!")
        return 1
    
    # Launch Streamlit with the cockpit
    try:
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            cockpit_path, 
            "--server.port", "8501",
            "--server.address", "localhost",
            "--browser.gatherUsageStats", "false"
        ]
        
        print("🚀 Launching Streamlit interface...")
        print("📱 Open your browser to: http://localhost:8501")
        print("🛑 Press Ctrl+C to stop")
        print("-" * 50)
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n🛑 GRINGO Personal OS stopped")
        return 0
    except Exception as e:
        print(f"❌ Error launching: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
