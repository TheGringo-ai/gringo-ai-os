#!/usr/bin/env python3
"""
🔐 Security Agent - Code security scanning and vulnerability detection
Performs static analysis for security issues and best practices
"""

import json
import sys
import os
import re
import subprocess
from datetime import datetime
import hashlib

class SecurityAgent:
    def __init__(self):
        self.name = "security"
        self.vulnerability_patterns = self._load_vulnerability_patterns()
        
    def _load_vulnerability_patterns(self) -> dict:
        """Load security vulnerability patterns to scan for"""
        return {
            "hardcoded_secrets": [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']',
                r'aws_access_key_id\s*=\s*["\'][^"\']+["\']',
                r'sk-[a-zA-Z0-9]{48}',  # OpenAI API keys
            ],
            "sql_injection": [
                r'execute\s*\(\s*["\'].*%.*["\']',
                r'cursor\.execute\s*\(\s*["\'].*\+.*["\']',
                r'query\s*=\s*["\'].*%.*["\']',
                r'SELECT.*\+.*FROM',
            ],
            "command_injection": [
                r'os\.system\s*\(',
                r'subprocess\.call\s*\(',
                r'subprocess\.run\s*\([^,]*shell\s*=\s*True',
                r'eval\s*\(',
                r'exec\s*\(',
            ],
            "path_traversal": [
                r'open\s*\([^,]*\.\./.*\)',
                r'file\s*=.*\.\./.*',
                r'path.*\.\./.*',
            ],
            "weak_crypto": [
                r'md5\s*\(',
                r'sha1\s*\(',
                r'DES\s*\(',
                r'random\.random\s*\(',
            ]
        }
    
    def scan_file_for_vulnerabilities(self, file_path: str) -> list:
        """Scan a single file for security vulnerabilities"""
        vulnerabilities = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                lines = content.split('\n')
                
            for category, patterns in self.vulnerability_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, content, re.IGNORECASE)
                    for match in matches:
                        # Find line number
                        line_num = content[:match.start()].count('\n') + 1
                        
                        vulnerabilities.append({
                            "file": file_path,
                            "line": line_num,
                            "category": category,
                            "pattern": pattern,
                            "matched_text": match.group()[:100],  # Limit to 100 chars
                            "severity": self._get_severity(category),
                            "description": self._get_vulnerability_description(category)
                        })
                        
        except Exception as e:
            vulnerabilities.append({
                "file": file_path,
                "line": 0,
                "category": "scan_error",
                "pattern": "file_read_error",
                "matched_text": str(e),
                "severity": "low",
                "description": "Could not scan file for vulnerabilities"
            })
            
        return vulnerabilities
    
    def _get_severity(self, category: str) -> str:
        """Get severity level for vulnerability category"""
        severity_map = {
            "hardcoded_secrets": "high",
            "sql_injection": "high",
            "command_injection": "critical",
            "path_traversal": "medium",
            "weak_crypto": "medium",
            "scan_error": "low"
        }
        return severity_map.get(category, "medium")
    
    def _get_vulnerability_description(self, category: str) -> str:
        """Get description for vulnerability category"""
        descriptions = {
            "hardcoded_secrets": "Hardcoded secrets/credentials detected",
            "sql_injection": "Potential SQL injection vulnerability",
            "command_injection": "Potential command injection vulnerability",
            "path_traversal": "Potential path traversal vulnerability",
            "weak_crypto": "Weak cryptographic algorithm usage",
            "scan_error": "Error occurred during security scan"
        }
        return descriptions.get(category, "Security issue detected")
    
    def check_dependencies_security(self, workspace: str) -> dict:
        """Check for known vulnerable dependencies"""
        
        security_issues = {
            "requirements_file": None,
            "dependencies": [],
            "security_warnings": [],
            "recommendations": []
        }
        
        requirements_path = os.path.join(workspace, "requirements.txt")
        
        if os.path.exists(requirements_path):
            security_issues["requirements_file"] = requirements_path
            
            try:
                with open(requirements_path, 'r') as f:
                    requirements = f.read().strip().split('\n')
                
                for req in requirements:
                    req = req.strip()
                    if req and not req.startswith('#'):
                        package_name = req.split('==')[0].split('>=')[0].split('<=')[0].strip()
                        security_issues["dependencies"].append({
                            "name": package_name,
                            "requirement": req,
                            "security_status": "unknown"  # Would need API call to check
                        })
                
                # Check for potentially risky packages
                risky_patterns = ['eval', 'exec', 'pickle', 'yaml', 'subprocess']
                for dep in security_issues["dependencies"]:
                    if any(risk in dep["name"].lower() for risk in risky_patterns):
                        security_issues["security_warnings"].append(
                            f"Potentially risky dependency: {dep['name']}"
                        )
                
            except Exception as e:
                security_issues["security_warnings"].append(f"Error reading requirements.txt: {e}")
        else:
            security_issues["recommendations"].append("Add requirements.txt for dependency tracking")
        
        return security_issues
    
    def check_file_permissions(self, workspace: str) -> dict:
        """Check file permissions for security issues"""
        
        permission_issues = {
            "executable_files": [],
            "world_writable": [],
            "suspicious_permissions": [],
            "recommendations": []
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    stat_info = os.stat(file_path)
                    mode = stat_info.st_mode
                    
                    # Check for executable Python files
                    if file.endswith('.py') and os.access(file_path, os.X_OK):
                        permission_issues["executable_files"].append(file_path)
                    
                    # Check for world-writable files
                    if mode & 0o002:
                        permission_issues["world_writable"].append(file_path)
                    
                    # Check for suspicious permissions (777, etc.)
                    if mode & 0o777 == 0o777:
                        permission_issues["suspicious_permissions"].append({
                            "file": file_path,
                            "permissions": oct(mode)[-3:]
                        })
                        
                except Exception:
                    continue
        
        # Generate recommendations
        if permission_issues["world_writable"]:
            permission_issues["recommendations"].append(
                "Remove world-write permissions from sensitive files"
            )
        if permission_issues["suspicious_permissions"]:
            permission_issues["recommendations"].append(
                "Review and fix overly permissive file permissions"
            )
            
        return permission_issues
    
    def generate_security_report(self, vulnerabilities: list, deps_security: dict, 
                                permissions: dict) -> dict:
        """Generate comprehensive security report"""
        
        # Count vulnerabilities by severity
        severity_counts = {"critical": 0, "high": 0, "medium": 0, "low": 0}
        for vuln in vulnerabilities:
            severity_counts[vuln["severity"]] += 1
        
        # Calculate security score (100 - penalties)
        score = 100
        score -= severity_counts["critical"] * 20
        score -= severity_counts["high"] * 10
        score -= severity_counts["medium"] * 5
        score -= severity_counts["low"] * 2
        score -= len(deps_security["security_warnings"]) * 5
        score -= len(permissions["world_writable"]) * 3
        score = max(0, score)
        
        # Determine security grade
        if score >= 90:
            grade = "A"
            status = "Excellent"
        elif score >= 80:
            grade = "B"
            status = "Good"
        elif score >= 70:
            grade = "C"
            status = "Acceptable"
        elif score >= 60:
            grade = "D"
            status = "Needs Attention"
        else:
            grade = "F"
            status = "Critical Issues"
        
        # Generate recommendations
        recommendations = []
        
        if severity_counts["critical"] > 0:
            recommendations.append({
                "priority": "critical",
                "action": "Fix critical security vulnerabilities immediately",
                "details": f"{severity_counts['critical']} critical issues found"
            })
        
        if severity_counts["high"] > 0:
            recommendations.append({
                "priority": "high",
                "action": "Address high-severity security issues",
                "details": f"{severity_counts['high']} high-severity issues found"
            })
        
        if deps_security["security_warnings"]:
            recommendations.append({
                "priority": "medium",
                "action": "Review dependency security warnings",
                "details": f"{len(deps_security['security_warnings'])} dependency warnings"
            })
        
        if not deps_security["requirements_file"]:
            recommendations.append({
                "priority": "low",
                "action": "Add requirements.txt for dependency management",
                "details": "No requirements file found"
            })
        
        return {
            "security_score": score,
            "grade": grade,
            "status": status,
            "vulnerability_summary": severity_counts,
            "total_vulnerabilities": len(vulnerabilities),
            "dependency_issues": len(deps_security["security_warnings"]),
            "permission_issues": len(permissions["world_writable"]) + len(permissions["suspicious_permissions"]),
            "recommendations": recommendations
        }

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = SecurityAgent()
        
        print(f"🔐 Security Agent: Performing security scan...")
        
        workspace = task_data.get('workspace', '.')
        scan_type = task_data.get('scan_type', 'full')
        
        # Scan for vulnerabilities
        all_vulnerabilities = []
        files_scanned = 0
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    vulns = agent.scan_file_for_vulnerabilities(file_path)
                    all_vulnerabilities.extend(vulns)
                    files_scanned += 1
        
        # Check dependencies
        deps_security = agent.check_dependencies_security(workspace)
        
        # Check file permissions
        permissions = agent.check_file_permissions(workspace)
        
        # Generate security report
        security_report = agent.generate_security_report(
            all_vulnerabilities, deps_security, permissions
        )
        
        result = {
            "scan_summary": {
                "files_scanned": files_scanned,
                "vulnerabilities_found": len(all_vulnerabilities),
                "scan_type": scan_type
            },
            "vulnerabilities": all_vulnerabilities[:20],  # Limit output size
            "dependency_security": deps_security,
            "file_permissions": permissions,
            "security_report": security_report,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        print(f"✅ Security scan completed")
        print(f"   📊 Security Score: {security_report['security_score']}/100 (Grade: {security_report['grade']})")
        print(f"   📁 Files Scanned: {files_scanned}")
        print(f"   ⚠️ Vulnerabilities: {len(all_vulnerabilities)}")
        print(f"   🔒 Status: {security_report['status']}")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ Security scan failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
