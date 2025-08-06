#!/usr/bin/env python3
"""
Custom Performance Agent - System performance monitoring and optimization
"""

import json
import sys
import os
import psutil
import time
from datetime import datetime

class PerformanceAgent:
    def __init__(self):
        self.name = "performance"
        
    def monitor_system(self) -> dict:
        """Monitor current system performance"""
        
        # Get system metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Get process info for current Python processes
        python_processes = []
        for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
            try:
                if 'python' in proc.info['name'].lower():
                    python_processes.append(proc.info)
            except:
                continue
        
        return {
            "cpu_usage": cpu_percent,
            "memory": {
                "total": memory.total,
                "available": memory.available,
                "percent": memory.percent,
                "used": memory.used
            },
            "disk": {
                "total": disk.total,
                "free": disk.free,
                "percent": (disk.used / disk.total) * 100
            },
            "python_processes": len(python_processes),
            "top_processes": python_processes[:5]
        }
    
    def analyze_performance(self, workspace: str) -> dict:
        """Analyze workspace performance characteristics"""
        
        file_count = 0
        total_size = 0
        largest_files = []
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        size = os.path.getsize(file_path)
                        file_count += 1
                        total_size += size
                        
                        largest_files.append({
                            "file": file_path,
                            "size": size,
                            "size_mb": round(size / 1024 / 1024, 2)
                        })
                    except:
                        continue
        
        # Sort by size and get top 5
        largest_files.sort(key=lambda x: x['size'], reverse=True)
        largest_files = largest_files[:5]
        
        return {
            "file_analysis": {
                "python_files": file_count,
                "total_size_mb": round(total_size / 1024 / 1024, 2),
                "avg_file_size_kb": round((total_size / file_count) / 1024, 2) if file_count > 0 else 0,
                "largest_files": largest_files
            },
            "recommendations": self._generate_performance_recommendations(file_count, total_size, largest_files)
        }
    
    def _generate_performance_recommendations(self, file_count: int, total_size: int, largest_files: list) -> list:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        if file_count > 50:
            recommendations.append({
                "category": "structure",
                "priority": "medium",
                "description": f"Large number of Python files ({file_count}). Consider modularization."
            })
        
        if total_size > 10 * 1024 * 1024:  # 10MB
            recommendations.append({
                "category": "size",
                "priority": "low", 
                "description": f"Codebase size is {total_size/1024/1024:.1f}MB. Monitor for bloat."
            })
        
        for large_file in largest_files:
            if large_file['size'] > 1024 * 1024:  # 1MB
                recommendations.append({
                    "category": "file_size",
                    "priority": "high",
                    "description": f"Large file detected: {large_file['file']} ({large_file['size_mb']}MB)"
                })
        
        return recommendations

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = PerformanceAgent()
        
        print(f"⚡ Performance Agent: Monitoring system...")
        
        workspace = task_data.get('workspace', '.')
        monitor_type = task_data.get('type', 'full')
        
        system_metrics = agent.monitor_system()
        workspace_analysis = agent.analyze_performance(workspace)
        
        result = {
            "system_metrics": system_metrics,
            "workspace_analysis": workspace_analysis,
            "monitor_type": monitor_type,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Performance monitoring completed")
        print(f"   💻 CPU Usage: {system_metrics['cpu_usage']:.1f}%")
        print(f"   🧠 Memory Usage: {system_metrics['memory']['percent']:.1f}%")
        print(f"   📁 Python Files: {workspace_analysis['file_analysis']['python_files']}")
        print(f"   💡 Recommendations: {len(workspace_analysis['recommendations'])}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Performance monitoring failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
