#!/usr/bin/env python3
"""
📊 Analytics Agent - Advanced performance metrics and project analytics
Provides detailed insights into code quality, performance, and project health
"""

import json
import sys
import os
import ast
import time
import psutil
import subprocess
from datetime import datetime, timedelta
from collections import defaultdict

class AnalyticsAgent:
    def __init__(self):
        self.name = "analytics"
        
    def analyze_code_complexity(self, workspace: str) -> dict:
        """Analyze code complexity metrics"""
        
        complexity_data = {
            "files_analyzed": 0,
            "total_lines": 0,
            "total_functions": 0,
            "total_classes": 0,
            "complexity_scores": [],
            "file_details": [],
            "complexity_distribution": {
                "simple": 0,    # < 10 complexity
                "moderate": 0,  # 10-20 complexity
                "complex": 0,   # 20-50 complexity
                "very_complex": 0  # > 50 complexity
            }
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    file_complexity = self._analyze_file_complexity(file_path)
                    
                    if file_complexity:
                        complexity_data["files_analyzed"] += 1
                        complexity_data["total_lines"] += file_complexity["lines"]
                        complexity_data["total_functions"] += file_complexity["functions"]
                        complexity_data["total_classes"] += file_complexity["classes"]
                        complexity_data["complexity_scores"].append(file_complexity["complexity"])
                        complexity_data["file_details"].append(file_complexity)
                        
                        # Categorize complexity
                        if file_complexity["complexity"] < 10:
                            complexity_data["complexity_distribution"]["simple"] += 1
                        elif file_complexity["complexity"] < 20:
                            complexity_data["complexity_distribution"]["moderate"] += 1
                        elif file_complexity["complexity"] < 50:
                            complexity_data["complexity_distribution"]["complex"] += 1
                        else:
                            complexity_data["complexity_distribution"]["very_complex"] += 1
        
        # Calculate averages
        if complexity_data["files_analyzed"] > 0:
            complexity_data["avg_complexity"] = sum(complexity_data["complexity_scores"]) / len(complexity_data["complexity_scores"])
            complexity_data["avg_lines_per_file"] = complexity_data["total_lines"] / complexity_data["files_analyzed"]
            complexity_data["avg_functions_per_file"] = complexity_data["total_functions"] / complexity_data["files_analyzed"]
        else:
            complexity_data.update({"avg_complexity": 0, "avg_lines_per_file": 0, "avg_functions_per_file": 0})
        
        return complexity_data
    
    def _analyze_file_complexity(self, file_path: str) -> dict:
        """Analyze complexity of a single file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = len(content.splitlines())
            
            tree = ast.parse(content)
            
            functions = 0
            classes = 0
            complexity_score = 0
            
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions += 1
                    # Simple complexity calculation based on nested structures
                    complexity_score += self._calculate_node_complexity(node)
                elif isinstance(node, ast.ClassDef):
                    classes += 1
                    complexity_score += 2  # Base complexity for class
            
            return {
                "file": os.path.relpath(file_path),
                "lines": lines,
                "functions": functions,
                "classes": classes,
                "complexity": complexity_score,
                "complexity_per_line": complexity_score / lines if lines > 0 else 0
            }
            
        except Exception:
            return None
    
    def _calculate_node_complexity(self, node) -> int:
        """Calculate complexity score for an AST node"""
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.While, ast.For)):
                complexity += 1
            elif isinstance(child, ast.Try):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, ast.With):
                complexity += 1
        
        return complexity
    
    def analyze_performance_metrics(self, workspace: str) -> dict:
        """Analyze performance-related metrics"""
        
        perf_data = {
            "system_metrics": self._get_system_metrics(),
            "workspace_metrics": self._get_workspace_metrics(workspace),
            "import_analysis": self._analyze_imports(workspace),
            "potential_bottlenecks": []
        }
        
        # Identify potential performance issues
        if perf_data["workspace_metrics"]["avg_file_size_kb"] > 100:
            perf_data["potential_bottlenecks"].append({
                "type": "large_files",
                "description": "Large Python files detected",
                "metric": f"Avg file size: {perf_data['workspace_metrics']['avg_file_size_kb']:.1f}KB"
            })
        
        if len(perf_data["import_analysis"]["heavy_imports"]) > 0:
            perf_data["potential_bottlenecks"].append({
                "type": "heavy_imports",
                "description": "Heavy imports detected",
                "metric": f"{len(perf_data['import_analysis']['heavy_imports'])} heavy imports"
            })
        
        return perf_data
    
    def _get_system_metrics(self) -> dict:
        """Get current system performance metrics"""
        try:
            return {
                "cpu_percent": psutil.cpu_percent(interval=0.1),
                "memory_percent": psutil.virtual_memory().percent,
                "disk_usage_percent": psutil.disk_usage('/').percent,
                "load_average": os.getloadavg()[0] if hasattr(os, 'getloadavg') else 0,
                "timestamp": datetime.now().isoformat()
            }
        except Exception:
            return {
                "cpu_percent": 0,
                "memory_percent": 0,
                "disk_usage_percent": 0,
                "load_average": 0,
                "timestamp": datetime.now().isoformat(),
                "error": "Could not retrieve system metrics"
            }
    
    def _get_workspace_metrics(self, workspace: str) -> dict:
        """Get workspace-specific metrics"""
        
        total_size = 0
        file_count = 0
        file_sizes = []
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        total_size += size
                        file_count += 1
                        file_sizes.append(size)
                    except:
                        continue
        
        return {
            "total_size_kb": total_size / 1024,
            "file_count": file_count,
            "avg_file_size_kb": (total_size / file_count / 1024) if file_count > 0 else 0,
            "largest_file_kb": (max(file_sizes) / 1024) if file_sizes else 0,
            "smallest_file_kb": (min(file_sizes) / 1024) if file_sizes else 0
        }
    
    def _analyze_imports(self, workspace: str) -> dict:
        """Analyze import patterns and dependencies"""
        
        import_data = {
            "total_imports": 0,
            "unique_modules": set(),
            "heavy_imports": [],
            "import_frequency": defaultdict(int),
            "external_dependencies": set(),
            "standard_library": set()
        }
        
        # Common heavy/slow imports
        heavy_modules = {
            'pandas', 'numpy', 'tensorflow', 'torch', 'matplotlib', 
            'scipy', 'sklearn', 'requests', 'beautifulsoup4'
        }
        
        # Standard library modules (partial list)
        stdlib_modules = {
            'os', 'sys', 'json', 'time', 'datetime', 'subprocess', 
            'threading', 'multiprocessing', 'collections', 'itertools',
            'functools', 're', 'math', 'random', 'urllib', 'http'
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            tree = ast.parse(f.read())
                        
                        for node in ast.walk(tree):
                            if isinstance(node, ast.Import):
                                for alias in node.names:
                                    module = alias.name.split('.')[0]
                                    import_data["total_imports"] += 1
                                    import_data["unique_modules"].add(module)
                                    import_data["import_frequency"][module] += 1
                                    
                                    if module in heavy_modules:
                                        import_data["heavy_imports"].append(module)
                                    elif module in stdlib_modules:
                                        import_data["standard_library"].add(module)
                                    else:
                                        import_data["external_dependencies"].add(module)
                            
                            elif isinstance(node, ast.ImportFrom):
                                if node.module:
                                    module = node.module.split('.')[0]
                                    import_data["total_imports"] += 1
                                    import_data["unique_modules"].add(module)
                                    import_data["import_frequency"][module] += 1
                                    
                                    if module in heavy_modules:
                                        import_data["heavy_imports"].append(module)
                                    elif module in stdlib_modules:
                                        import_data["standard_library"].add(module)
                                    else:
                                        import_data["external_dependencies"].add(module)
                    except:
                        continue
        
        # Convert sets to lists for JSON serialization
        import_data["unique_modules"] = list(import_data["unique_modules"])
        import_data["external_dependencies"] = list(import_data["external_dependencies"])
        import_data["standard_library"] = list(import_data["standard_library"])
        import_data["heavy_imports"] = list(set(import_data["heavy_imports"]))
        import_data["import_frequency"] = dict(import_data["import_frequency"])
        
        return import_data
    
    def generate_project_health_score(self, complexity_data: dict, perf_data: dict) -> dict:
        """Generate overall project health score"""
        
        health_score = 100
        factors = {}
        
        # Complexity factor (0-30 points)
        if complexity_data["files_analyzed"] > 0:
            avg_complexity = complexity_data["avg_complexity"]
            if avg_complexity > 50:
                complexity_penalty = 30
            elif avg_complexity > 30:
                complexity_penalty = 20
            elif avg_complexity > 15:
                complexity_penalty = 10
            else:
                complexity_penalty = 0
            
            health_score -= complexity_penalty
            factors["complexity"] = 30 - complexity_penalty
        else:
            factors["complexity"] = 30
        
        # File size factor (0-20 points)
        avg_file_size = perf_data["workspace_metrics"]["avg_file_size_kb"]
        if avg_file_size > 200:
            size_penalty = 20
        elif avg_file_size > 100:
            size_penalty = 15
        elif avg_file_size > 50:
            size_penalty = 10
        else:
            size_penalty = 0
        
        health_score -= size_penalty
        factors["file_size"] = 20 - size_penalty
        
        # Import factor (0-25 points)
        heavy_imports = len(perf_data["import_analysis"]["heavy_imports"])
        if heavy_imports > 10:
            import_penalty = 25
        elif heavy_imports > 5:
            import_penalty = 15
        elif heavy_imports > 2:
            import_penalty = 10
        else:
            import_penalty = 0
        
        health_score -= import_penalty
        factors["imports"] = 25 - import_penalty
        
        # Performance bottlenecks factor (0-25 points)
        bottleneck_count = len(perf_data["potential_bottlenecks"])
        bottleneck_penalty = min(25, bottleneck_count * 10)
        health_score -= bottleneck_penalty
        factors["performance"] = 25 - bottleneck_penalty
        
        # Determine grade
        if health_score >= 90:
            grade = "A"
            status = "Excellent"
        elif health_score >= 80:
            grade = "B"
            status = "Good"
        elif health_score >= 70:
            grade = "C"
            status = "Fair"
        elif health_score >= 60:
            grade = "D"
            status = "Needs Improvement"
        else:
            grade = "F"
            status = "Poor"
        
        return {
            "health_score": max(0, health_score),
            "grade": grade,
            "status": status,
            "factor_scores": factors,
            "total_possible": 100
        }
    
    def generate_recommendations(self, complexity_data: dict, perf_data: dict, health_score: dict) -> list:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        # Complexity recommendations
        if complexity_data["avg_complexity"] > 20:
            recommendations.append({
                "category": "complexity",
                "priority": "high",
                "title": "Reduce code complexity",
                "description": f"Average complexity is {complexity_data['avg_complexity']:.1f}. Consider refactoring complex functions.",
                "action": "Break down complex functions into smaller, focused functions"
            })
        
        # File size recommendations
        if perf_data["workspace_metrics"]["avg_file_size_kb"] > 100:
            recommendations.append({
                "category": "file_size",
                "priority": "medium",
                "title": "Optimize file sizes",
                "description": f"Average file size is {perf_data['workspace_metrics']['avg_file_size_kb']:.1f}KB",
                "action": "Split large files into smaller, focused modules"
            })
        
        # Import recommendations
        if len(perf_data["import_analysis"]["heavy_imports"]) > 3:
            recommendations.append({
                "category": "imports",
                "priority": "medium",
                "title": "Optimize heavy imports",
                "description": f"{len(perf_data['import_analysis']['heavy_imports'])} heavy imports detected",
                "action": "Consider lazy loading or alternative lightweight libraries"
            })
        
        # Performance recommendations
        if perf_data["potential_bottlenecks"]:
            recommendations.append({
                "category": "performance",
                "priority": "medium",
                "title": "Address performance bottlenecks",
                "description": f"{len(perf_data['potential_bottlenecks'])} potential bottlenecks found",
                "action": "Review and optimize identified performance issues"
            })
        
        # Overall health recommendations
        if health_score["health_score"] < 70:
            recommendations.append({
                "category": "overall",
                "priority": "high",
                "title": "Improve overall project health",
                "description": f"Project health score is {health_score['health_score']}/100",
                "action": "Focus on addressing complexity, file size, and performance issues"
            })
        
        return recommendations

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = AnalyticsAgent()
        
        print(f"📊 Analytics Agent: Performing comprehensive analysis...")
        
        workspace = task_data.get('workspace', '.')
        analysis_type = task_data.get('analysis_type', 'full')
        
        # Perform complexity analysis
        complexity_data = agent.analyze_code_complexity(workspace)
        
        # Perform performance analysis
        perf_data = agent.analyze_performance_metrics(workspace)
        
        # Generate health score
        health_score = agent.generate_project_health_score(complexity_data, perf_data)
        
        # Generate recommendations
        recommendations = agent.generate_recommendations(complexity_data, perf_data, health_score)
        
        result = {
            "analysis_type": analysis_type,
            "complexity_analysis": complexity_data,
            "performance_analysis": perf_data,
            "health_score": health_score,
            "recommendations": recommendations,
            "summary": {
                "files_analyzed": complexity_data["files_analyzed"],
                "overall_grade": health_score["grade"],
                "health_score": health_score["health_score"],
                "recommendations_count": len(recommendations)
            },
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Analytics analysis completed")
        print(f"   📊 Health Score: {health_score['health_score']}/100 (Grade: {health_score['grade']})")
        print(f"   📁 Files Analyzed: {complexity_data['files_analyzed']}")
        print(f"   ⚡ Avg Complexity: {complexity_data.get('avg_complexity', 0):.1f}")
        print(f"   💡 Recommendations: {len(recommendations)}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Analytics analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
