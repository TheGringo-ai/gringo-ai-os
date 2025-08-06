#!/usr/bin/env python3
"""
Planning Agent - Breaks down complex tasks into actionable steps
"""

import json
import sys
import os
from datetime import datetime

class PlannerAgent:
    def __init__(self):
        self.name = "planner"
        
    def analyze_request(self, request: str, workspace: str) -> dict:
        """Analyze feature request and create implementation plan"""
        
        # Scan workspace for existing structure
        python_files = []
        test_files = []
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    full_path = os.path.join(root, file)
                    if 'test_' in file:
                        test_files.append(full_path)
                    else:
                        python_files.append(full_path)
        
        # Create implementation plan
        plan = {
            "request": request,
            "analysis": {
                "existing_files": len(python_files),
                "existing_tests": len(test_files),
                "complexity": "medium" if len(python_files) > 5 else "simple"
            },
            "implementation_steps": [
                {
                    "phase": "code_analysis",
                    "description": "Analyze existing codebase for integration points",
                    "estimated_time": "5 minutes",
                    "agents_needed": ["refactor"]
                },
                {
                    "phase": "feature_implementation", 
                    "description": f"Implement: {request}",
                    "estimated_time": "15 minutes",
                    "agents_needed": ["refactor"]
                },
                {
                    "phase": "test_generation",
                    "description": "Generate comprehensive tests for new functionality",
                    "estimated_time": "10 minutes", 
                    "agents_needed": ["test_gen"]
                },
                {
                    "phase": "documentation",
                    "description": "Update documentation and create usage examples",
                    "estimated_time": "8 minutes",
                    "agents_needed": ["doc_gen"]
                },
                {
                    "phase": "quality_review",
                    "description": "Code review and quality validation",
                    "estimated_time": "5 minutes",
                    "agents_needed": ["reviewer"]
                }
            ],
            "total_estimated_time": "43 minutes",
            "risk_assessment": "low",
            "timestamp": datetime.now().isoformat()
        }
        
        return plan
    
    def create_task_breakdown(self, plan: dict) -> list:
        """Convert plan into executable task list"""
        tasks = []
        
        for step in plan["implementation_steps"]:
            for agent in step["agents_needed"]:
                tasks.append({
                    "agent": agent,
                    "phase": step["phase"],
                    "description": step["description"],
                    "context": plan["request"]
                })
        
        return tasks

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = PlannerAgent()
        
        print(f"🧠 Planning Agent: Analyzing '{task_data.get('request', 'unknown')}'")
        
        plan = agent.analyze_request(
            task_data.get('request', ''), 
            task_data.get('workspace', '.')
        )
        
        tasks = agent.create_task_breakdown(plan)
        
        result = {
            "plan": plan,
            "tasks": tasks,
            "status": "completed"
        }
        
        print("✅ Planning completed successfully")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Planning failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
