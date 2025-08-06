#!/usr/bin/env python3
"""
Review Agent - Code quality assessment and final validation
"""

import json
import sys
import os
import ast
import subprocess
from datetime import datetime

class ReviewAgent:
    def __init__(self):
        self.name = "reviewer"
        
    def assess_code_quality(self, workspace: str) -> dict:
        """Comprehensive code quality assessment"""
        
        assessment = {
            "files_reviewed": 0,
            "total_lines": 0,
            "issues": [],
            "metrics": {
                "complexity_score": 0,
                "documentation_coverage": 0,
                "test_coverage_estimate": 0
            },
            "recommendations": []
        }
        
        python_files = []
        test_files = []
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    if 'test_' in file:
                        test_files.append(file_path)
                    else:
                        python_files.append(file_path)
        
        # Analyze each Python file
        total_functions = 0
        documented_functions = 0
        
        for py_file in python_files:
            try:
                with open(py_file, 'r') as f:
                    content = f.read()
                    lines = len(content.splitlines())
                    assessment["total_lines"] += lines
                    assessment["files_reviewed"] += 1
                
                tree = ast.parse(content)
                
                # Count functions and documentation
                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef):
                        total_functions += 1
                        if ast.get_docstring(node):
                            documented_functions += 1
                        
                        # Check for overly complex functions
                        if len(node.body) > 15:
                            assessment["issues"].append({
                                "file": py_file,
                                "type": "complexity",
                                "function": node.name,
                                "severity": "medium",
                                "description": f"Function {node.name} has {len(node.body)} statements (consider refactoring)"
                            })
                
                # Check for common issues
                if lines > 200:
                    assessment["issues"].append({
                        "file": py_file,
                        "type": "size",
                        "severity": "low",
                        "description": f"File is {lines} lines (consider splitting)"
                    })
                    
            except Exception as e:
                assessment["issues"].append({
                    "file": py_file,
                    "type": "parse_error",
                    "severity": "high",
                    "description": f"Cannot parse file: {str(e)}"
                })
        
        # Calculate metrics
        if total_functions > 0:
            assessment["metrics"]["documentation_coverage"] = documented_functions / total_functions * 100
        
        if len(python_files) > 0:
            assessment["metrics"]["test_coverage_estimate"] = len(test_files) / len(python_files) * 100
        
        # Complexity score (simple heuristic)
        avg_lines_per_file = assessment["total_lines"] / assessment["files_reviewed"] if assessment["files_reviewed"] > 0 else 0
        complexity_factors = [
            len(assessment["issues"]) * 5,  # Issues increase complexity
            max(0, avg_lines_per_file - 50),  # Large files increase complexity
            max(0, 100 - assessment["metrics"]["documentation_coverage"])  # Poor docs increase complexity
        ]
        assessment["metrics"]["complexity_score"] = min(100, sum(complexity_factors))
        
        return assessment
    
    def run_static_analysis(self, workspace: str) -> dict:
        """Run static analysis tools if available"""
        
        analysis_results = {
            "tools_run": [],
            "issues_found": 0,
            "suggestions": []
        }
        
        # Try running flake8
        try:
            result = subprocess.run([
                'python3', '-m', 'flake8', workspace, '--count', '--statistics'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                analysis_results["tools_run"].append("flake8")
                analysis_results["suggestions"].append("Code follows PEP8 style guidelines")
            else:
                lines = result.stdout.strip().split('\n')
                if lines and lines[-1].isdigit():
                    analysis_results["issues_found"] += int(lines[-1])
                    
        except:
            pass  # flake8 not available
        
        # Try running mypy for type checking
        try:
            result = subprocess.run([
                'python3', '-m', 'mypy', workspace, '--ignore-missing-imports'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                analysis_results["tools_run"].append("mypy")
                analysis_results["suggestions"].append("Type hints are properly used")
            
        except:
            pass  # mypy not available
        
        return analysis_results
    
    def generate_quality_report(self, assessment: dict, static_analysis: dict) -> dict:
        """Generate comprehensive quality report"""
        
        # Calculate overall quality score
        factors = {
            "documentation": min(100, assessment["metrics"]["documentation_coverage"]),
            "test_coverage": min(100, assessment["metrics"]["test_coverage_estimate"]),
            "complexity": max(0, 100 - assessment["metrics"]["complexity_score"]),
            "issues": max(0, 100 - len(assessment["issues"]) * 10)
        }
        
        overall_score = sum(factors.values()) / len(factors)
        
        # Determine quality grade
        if overall_score >= 90:
            grade = "A"
            status = "Excellent"
        elif overall_score >= 80:
            grade = "B"
            status = "Good"
        elif overall_score >= 70:
            grade = "C"
            status = "Acceptable"
        elif overall_score >= 60:
            grade = "D"
            status = "Needs Improvement"
        else:
            grade = "F"
            status = "Poor"
        
        # Generate recommendations
        recommendations = []
        
        if assessment["metrics"]["documentation_coverage"] < 50:
            recommendations.append({
                "priority": "high",
                "category": "documentation",
                "description": "Improve function and class documentation",
                "action": "Add docstrings to undocumented functions"
            })
        
        if assessment["metrics"]["test_coverage_estimate"] < 60:
            recommendations.append({
                "priority": "high",
                "category": "testing",
                "description": "Increase test coverage",
                "action": "Create tests for uncovered modules"
            })
        
        if len(assessment["issues"]) > 5:
            recommendations.append({
                "priority": "medium",
                "category": "quality",
                "description": "Address code quality issues",
                "action": "Refactor complex functions and fix style issues"
            })
        
        return {
            "overall_score": round(overall_score, 1),
            "grade": grade,
            "status": status,
            "factor_scores": factors,
            "recommendations": recommendations,
            "summary": {
                "files_reviewed": assessment["files_reviewed"],
                "total_lines": assessment["total_lines"],
                "issues_count": len(assessment["issues"]),
                "tools_used": static_analysis["tools_run"]
            }
        }

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = ReviewAgent()
        
        print(f"🔍 Review Agent: Conducting quality assessment...")
        
        workspace = task_data.get('workspace', '.')
        
        assessment = agent.assess_code_quality(workspace)
        static_analysis = agent.run_static_analysis(workspace)
        quality_report = agent.generate_quality_report(assessment, static_analysis)
        
        result = {
            "assessment": assessment,
            "static_analysis": static_analysis,
            "quality_report": quality_report,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Quality review completed")
        print(f"   📊 Overall Score: {quality_report['overall_score']}/100 (Grade: {quality_report['grade']})")
        print(f"   📁 Files Reviewed: {assessment['files_reviewed']}")
        print(f"   ⚠️ Issues Found: {len(assessment['issues'])}")
        print(f"   💡 Recommendations: {len(quality_report['recommendations'])}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Quality review failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
