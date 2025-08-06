#!/usr/bin/env python3
"""
GRINGO Demo Script - Show off the enhanced project creation capabilities
"""

import json
import os
from project_manager import ProjectManager

def demo_project_creation():
    """Demonstrate the enhanced project creation features"""
    
    print("🤖 GRINGO Enhanced Project Creation Demo")
    print("=" * 50)
    
    # Initialize project manager
    workspace_root = os.path.expanduser("~/gringo_workspace")
    pm = ProjectManager(workspace_root)
    
    # Demo prompts to show the capabilities
    demo_prompts = [
        {
            "name": "Web Scraper",
            "prompt": "Create a web scraping tool that collects news articles from multiple websites, saves them to a database, and generates daily summaries",
            "expected_type": "automation"
        },
        {
            "name": "Personal Finance Tracker",
            "prompt": "Build a personal expense tracker web application with Flask backend, SQLite database, and HTML/CSS/JavaScript frontend for tracking income and expenses",
            "expected_type": "web_backend"
        },
        {
            "name": "Data Analysis Dashboard",
            "prompt": "Create a data analysis dashboard using Python, pandas, and matplotlib to analyze sales data from CSV files with interactive charts",
            "expected_type": "data_science"
        },
        {
            "name": "File Organization Tool",
            "prompt": "Build an automation script that organizes files by type, removes duplicates, and creates backups with scheduling capabilities",
            "expected_type": "automation"
        },
        {
            "name": "Simple 2D Game",
            "prompt": "Create a 2D platformer game using Python and Pygame with player movement, collision detection, enemies, and scoring system",
            "expected_type": "game"
        }
    ]
    
    for i, demo in enumerate(demo_prompts, 1):
        print(f"\n📋 Demo {i}: {demo['name']}")
        print(f"Prompt: {demo['prompt']}")
        print(f"Expected Type: {demo['expected_type']}")
        
        # Analyze the prompt (without creating the project)
        analysis = pm._analyze_prompt(demo['prompt'])
        
        print(f"✅ Analysis Results:")
        print(f"   Detected Type: {analysis['type']}")
        print(f"   Language: {analysis['language']}")
        print(f"   Features: {', '.join(analysis['features']) if analysis['features'] else 'Basic'}")
        print(f"   Suggested Name: {analysis['suggested_name']}")
        
        # Show what files would be created
        print(f"📁 Would create project structure for {analysis['type']} project")
        
        match = "✅ CORRECT" if analysis['type'] == demo['expected_type'] else "⚠️ DIFFERENT"
        print(f"   {match} (Expected: {demo['expected_type']}, Got: {analysis['type']})")
    
    print("\n" + "=" * 50)
    print("🎯 Demo Summary:")
    print("   ✅ GRINGO can understand natural language project descriptions")
    print("   ✅ Automatically detects project type and language")
    print("   ✅ Suggests appropriate project structure and files")
    print("   ✅ Creates runnable projects with proper setup")
    print("   ✅ Supports Python, JavaScript, TypeScript, and more")
    print("   ✅ Handles web apps, data science, games, automation, and mobile apps")
    
    print("\n🚀 To use GRINGO Project Creator:")
    print("   1. Open http://localhost:8501 in your browser")
    print("   2. Click on '🚀 Project Creator' tab")
    print("   3. Describe what you want to build in natural language")
    print("   4. Click 'Create Project' and watch the magic happen!")
    print("   5. Upload files, run quick tasks, and manage all your projects")
    
    print("\n🔒 Everything is 100% local and private!")

if __name__ == "__main__":
    demo_project_creation()
