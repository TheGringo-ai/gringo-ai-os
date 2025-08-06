#!/usr/bin/env python3
"""
Refactor Agent - Code optimization, cleanup, and restructuring
"""

import json
import sys
import os
import ast
import subprocess
from datetime import datetime

class RefactorAgent:
    def __init__(self):
        self.name = "refactor"
        self.improvements = []
        
    def analyze_code_quality(self, workspace: str) -> dict:
        """Analyze code quality and suggest improvements"""
        
        issues = []
        files_analyzed = 0
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    files_analyzed += 1
                    
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read()
                            
                        # Basic AST analysis
                        tree = ast.parse(content)
                        
                        # Check for long functions
                        for node in ast.walk(tree):
                            if isinstance(node, ast.FunctionDef):
                                if len(node.body) > 20:
                                    issues.append({
                                        "file": file_path,
                                        "type": "long_function",
                                        "function": node.name,
                                        "lines": len(node.body),
                                        "suggestion": "Consider breaking into smaller functions"
                                    })
                        
                        # Check for missing docstrings
                        for node in ast.walk(tree):
                            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                                if not ast.get_docstring(node):
                                    issues.append({
                                        "file": file_path,
                                        "type": "missing_docstring",
                                        "name": node.name,
                                        "suggestion": "Add docstring for better documentation"
                                    })
                                    
                    except Exception as e:
                        issues.append({
                            "file": file_path,
                            "type": "parse_error",
                            "error": str(e),
                            "suggestion": "Fix syntax errors"
                        })
        
        return {
            "files_analyzed": files_analyzed,
            "total_issues": len(issues),
            "issues": issues[:10],  # Limit to top 10
            "categories": self._categorize_issues(issues)
        }
    
    def _categorize_issues(self, issues: list) -> dict:
        """Categorize issues by type"""
        categories = {}
        for issue in issues:
            issue_type = issue["type"]
            if issue_type not in categories:
                categories[issue_type] = 0
            categories[issue_type] += 1
        return categories
    
    def apply_basic_fixes(self, workspace: str) -> list:
        """Apply basic automated fixes"""
        fixes_applied = []
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    
                    try:
                        with open(file_path, 'r') as f:
                            original = f.read()
                        
                        # Apply basic formatting with autopep8 if available
                        try:
                            result = subprocess.run([
                                'python3', '-c', 
                                'import autopep8; import sys; print(autopep8.fix_code(sys.stdin.read()))'
                            ], input=original, text=True, capture_output=True)
                            
                            if result.returncode == 0 and result.stdout != original:
                                with open(file_path, 'w') as f:
                                    f.write(result.stdout)
                                fixes_applied.append({
                                    "file": file_path,
                                    "fix": "autopep8_formatting",
                                    "description": "Applied PEP8 formatting"
                                })
                        except:
                            pass  # autopep8 not available
                            
                    except Exception as e:
                        continue
        
        return fixes_applied
    
    def generate_recommendations(self, analysis: dict) -> list:
        """Generate specific improvement recommendations"""
        recommendations = []
        
        if analysis["categories"].get("long_function", 0) > 0:
            recommendations.append({
                "priority": "medium",
                "category": "structure",
                "description": "Break down long functions into smaller, focused functions",
                "estimated_effort": "2-4 hours"
            })
        
        if analysis["categories"].get("missing_docstring", 0) > 0:
            recommendations.append({
                "priority": "low", 
                "category": "documentation",
                "description": "Add docstrings to functions and classes",
                "estimated_effort": "1-2 hours"
            })
        
        if analysis["total_issues"] > 10:
            recommendations.append({
                "priority": "high",
                "category": "quality",
                "description": "Address code quality issues systematically",
                "estimated_effort": "4-8 hours"
            })
            
        return recommendations

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = RefactorAgent()
        
        print(f"⚙️ Refactor Agent: Analyzing code quality...")
        
        workspace = task_data.get('workspace', '.')
        target = task_data.get('target', 'general')
        
        analysis = agent.analyze_code_quality(workspace)
        fixes = agent.apply_basic_fixes(workspace)
        recommendations = agent.generate_recommendations(analysis)
        
        result = {
            "analysis": analysis,
            "fixes_applied": fixes,
            "recommendations": recommendations,
            "target": target,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Refactoring analysis completed")
        print(f"   📊 Files analyzed: {analysis['files_analyzed']}")
        print(f"   🔧 Fixes applied: {len(fixes)}")
        print(f"   💡 Recommendations: {len(recommendations)}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Refactoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
