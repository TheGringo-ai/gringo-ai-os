#!/usr/bin/env python3
"""
🚀 Deploy Agent - Automated deployment and CI/CD pipeline management
Handles deployment preparation, validation, and automation
"""

import json
import sys
import os
import subprocess
import shutil
from datetime import datetime
from pathlib import Path

class DeployAgent:
    def __init__(self):
        self.name = "deploy"
        
    def analyze_deployment_readiness(self, workspace: str) -> dict:
        """Analyze if project is ready for deployment"""
        
        readiness = {
            "score": 0,
            "max_score": 100,
            "checks": [],
            "blockers": [],
            "recommendations": []
        }
        
        # Check for essential files
        essential_files = {
            "requirements.txt": 20,
            "README.md": 10,
            "main.py": 15,
            "app.py": 15,
            ".gitignore": 5
        }
        
        for file, points in essential_files.items():
            file_path = os.path.join(workspace, file)
            if os.path.exists(file_path):
                readiness["score"] += points
                readiness["checks"].append(f"✅ {file} found")
            else:
                readiness["checks"].append(f"❌ {file} missing")
                if points >= 15:
                    readiness["blockers"].append(f"Missing critical file: {file}")
        
        # Check for tests
        test_files = []
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root:
                continue
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(file)
        
        if test_files:
            readiness["score"] += 15
            readiness["checks"].append(f"✅ {len(test_files)} test files found")
        else:
            readiness["checks"].append("❌ No test files found")
            readiness["recommendations"].append("Add test files for better deployment confidence")
        
        # Check for virtual environment
        if os.path.exists(os.path.join(workspace, "venv")):
            readiness["score"] += 10
            readiness["checks"].append("✅ Virtual environment detected")
        else:
            readiness["checks"].append("❌ No virtual environment found")
            readiness["recommendations"].append("Set up virtual environment for dependency isolation")
        
        # Check for configuration files
        config_files = ["config.py", "settings.py", ".env.example"]
        config_found = any(os.path.exists(os.path.join(workspace, cf)) for cf in config_files)
        
        if config_found:
            readiness["score"] += 10
            readiness["checks"].append("✅ Configuration files found")
        else:
            readiness["checks"].append("❌ No configuration files found")
            readiness["recommendations"].append("Add configuration management")
        
        # Security check
        security_score = self._check_security_basics(workspace)
        readiness["score"] += security_score
        readiness["checks"].append(f"🔐 Security score: {security_score}/15")
        
        return readiness
    
    def _check_security_basics(self, workspace: str) -> int:
        """Basic security checks"""
        score = 0
        
        # Check for .env in .gitignore
        gitignore_path = os.path.join(workspace, ".gitignore")
        if os.path.exists(gitignore_path):
            with open(gitignore_path, 'r') as f:
                content = f.read()
                if '.env' in content:
                    score += 5
                if '__pycache__' in content:
                    score += 2
                if 'venv' in content or '*.pyc' in content:
                    score += 3
        
        # Check for hardcoded secrets (basic scan)
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root:
                continue
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r') as f:
                            content = f.read().lower()
                            # Look for potential secrets
                            if any(term in content for term in ['password = ', 'api_key = ', 'secret = ']):
                                score -= 5  # Deduct points for potential hardcoded secrets
                                break
                    except:
                        continue
        
        return max(0, min(15, score + 5))  # Base 5 points, max 15
    
    def create_deployment_package(self, workspace: str, package_name: str = None) -> dict:
        """Create deployment package"""
        
        if not package_name:
            package_name = f"deploy_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        package_dir = os.path.join(workspace, "deploy_packages", package_name)
        
        try:
            # Create package directory
            os.makedirs(package_dir, exist_ok=True)
            
            # Files to include in deployment
            deploy_files = []
            exclude_patterns = ['venv/', '__pycache__/', '.git/', '*.pyc', 'deploy_packages/']
            
            for root, dirs, files in os.walk(workspace):
                # Skip excluded directories
                if any(pattern.rstrip('/') in root for pattern in exclude_patterns):
                    continue
                    
                for file in files:
                    if not any(file.endswith(ext) for ext in ['.pyc', '.pyo', '.DS_Store']):
                        src_path = os.path.join(root, file)
                        rel_path = os.path.relpath(src_path, workspace)
                        
                        # Skip excluded files
                        if not any(pattern in rel_path for pattern in exclude_patterns):
                            dest_path = os.path.join(package_dir, rel_path)
                            os.makedirs(os.path.dirname(dest_path), exist_ok=True)
                            shutil.copy2(src_path, dest_path)
                            deploy_files.append(rel_path)
            
            # Create deployment manifest
            manifest = {
                "package_name": package_name,
                "created_at": datetime.now().isoformat(),
                "files": deploy_files,
                "file_count": len(deploy_files),
                "deployment_notes": "Auto-generated deployment package"
            }
            
            with open(os.path.join(package_dir, "DEPLOY_MANIFEST.json"), 'w') as f:
                json.dump(manifest, f, indent=2)
            
            return {
                "success": True,
                "package_path": package_dir,
                "manifest": manifest,
                "size_mb": self._get_directory_size(package_dir)
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "package_path": None
            }
    
    def _get_directory_size(self, directory: str) -> float:
        """Get directory size in MB"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except:
                    continue
        return round(total_size / (1024 * 1024), 2)
    
    def run_pre_deployment_tests(self, workspace: str) -> dict:
        """Run pre-deployment validation tests"""
        
        test_results = {
            "total_tests": 0,
            "passed": 0,
            "failed": 0,
            "test_details": []
        }
        
        # Find and run test files
        test_files = []
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root:
                continue
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(os.path.join(root, file))
        
        for test_file in test_files:
            try:
                result = subprocess.run([
                    'python3', test_file
                ], capture_output=True, text=True, timeout=30, cwd=workspace)
                
                test_results["total_tests"] += 1
                
                if result.returncode == 0:
                    test_results["passed"] += 1
                    status = "passed"
                else:
                    test_results["failed"] += 1
                    status = "failed"
                
                test_results["test_details"].append({
                    "file": os.path.basename(test_file),
                    "status": status,
                    "output": result.stdout[:200] if result.stdout else "No output"
                })
                
            except subprocess.TimeoutExpired:
                test_results["total_tests"] += 1
                test_results["failed"] += 1
                test_results["test_details"].append({
                    "file": os.path.basename(test_file),
                    "status": "timeout",
                    "output": "Test execution timeout"
                })
            except Exception as e:
                test_results["total_tests"] += 1
                test_results["failed"] += 1
                test_results["test_details"].append({
                    "file": os.path.basename(test_file),
                    "status": "error",
                    "output": str(e)
                })
        
        return test_results
    
    def generate_deployment_script(self, workspace: str, deployment_type: str = "basic") -> str:
        """Generate deployment script"""
        
        script_content = f"""#!/bin/bash
# Auto-generated deployment script
# Generated on: {datetime.now().isoformat()}
# Deployment type: {deployment_type}

set -e  # Exit on any error

echo "🚀 Starting deployment..."

# Check Python version
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
if [ -f "requirements.txt" ]; then
    echo "📥 Installing dependencies..."
    pip install -r requirements.txt
else
    echo "⚠️ No requirements.txt found"
fi

# Run tests
echo "🧪 Running tests..."
"""
        
        # Add test running logic
        test_files = []
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root:
                continue
            for file in files:
                if file.startswith('test_') and file.endswith('.py'):
                    test_files.append(file)
        
        if test_files:
            for test_file in test_files[:3]:  # Limit to first 3 test files
                script_content += f"python3 {test_file}\n"
        else:
            script_content += "echo 'No test files found'\n"
        
        script_content += f"""
echo "✅ Pre-deployment tests completed"

# Start application (customize as needed)
if [ -f "main.py" ]; then
    echo "🏃 Starting application via main.py..."
    python3 main.py
elif [ -f "app.py" ]; then
    echo "🏃 Starting application via app.py..."
    python3 app.py
else
    echo "ℹ️ No standard entry point found"
fi

echo "🎉 Deployment completed successfully!"
"""
        
        return script_content

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = DeployAgent()
        
        print(f"🚀 Deploy Agent: Preparing deployment analysis...")
        
        workspace = task_data.get('workspace', '.')
        action = task_data.get('action', 'analyze')
        
        result = {
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        if action == "analyze" or action == "full":
            # Analyze deployment readiness
            readiness = agent.analyze_deployment_readiness(workspace)
            result["readiness_analysis"] = readiness
            
            print(f"📊 Deployment readiness: {readiness['score']}/{readiness['max_score']}")
            
        if action == "package" or action == "full":
            # Create deployment package
            package_result = agent.create_deployment_package(workspace)
            result["package_creation"] = package_result
            
            if package_result["success"]:
                print(f"📦 Package created: {package_result['size_mb']}MB")
            
        if action == "test" or action == "full":
            # Run pre-deployment tests
            test_results = agent.run_pre_deployment_tests(workspace)
            result["test_results"] = test_results
            
            print(f"🧪 Tests: {test_results['passed']}/{test_results['total_tests']} passed")
            
        if action == "script" or action == "full":
            # Generate deployment script
            script = agent.generate_deployment_script(workspace)
            result["deployment_script"] = script
            
            # Save script to file
            script_path = os.path.join(workspace, "deploy.sh")
            with open(script_path, 'w') as f:
                f.write(script)
            os.chmod(script_path, 0o755)  # Make executable
            
            print(f"📄 Deployment script created: deploy.sh")
        
        print("✅ Deployment analysis completed")
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Deployment analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
