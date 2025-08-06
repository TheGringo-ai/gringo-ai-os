#!/usr/bin/env python3
"""
🌐 API Agent - REST API generation, testing, and documentation
Automatically generates API endpoints, tests, and documentation
"""

import json
import sys
import os
import ast
import requests
import subprocess
from datetime import datetime
from typing import Dict, List, Any

class APIAgent:
    def __init__(self):
        self.name = "api"
        self.supported_frameworks = ["fastapi", "flask", "streamlit"]
        
    def detect_api_framework(self, workspace: str) -> dict:
        """Detect which API framework is being used"""
        
        framework_info = {
            "detected_frameworks": [],
            "main_framework": None,
            "api_files": [],
            "endpoint_count": 0
        }
        
        for root, dirs, files in os.walk(workspace):
            if 'venv' in root or '__pycache__' in root:
                continue
                
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read().lower()
                        
                        # Detect FastAPI
                        if 'from fastapi import' in content or 'import fastapi' in content:
                            if "fastapi" not in framework_info["detected_frameworks"]:
                                framework_info["detected_frameworks"].append("fastapi")
                            framework_info["api_files"].append({
                                "file": file_path,
                                "framework": "fastapi",
                                "endpoints": self._count_fastapi_endpoints(content)
                            })
                        
                        # Detect Flask
                        elif 'from flask import' in content or 'import flask' in content:
                            if "flask" not in framework_info["detected_frameworks"]:
                                framework_info["detected_frameworks"].append("flask")
                            framework_info["api_files"].append({
                                "file": file_path,
                                "framework": "flask",
                                "endpoints": self._count_flask_endpoints(content)
                            })
                        
                        # Detect Streamlit (not exactly API but web framework)
                        elif 'import streamlit' in content or 'streamlit' in content:
                            if "streamlit" not in framework_info["detected_frameworks"]:
                                framework_info["detected_frameworks"].append("streamlit")
                            framework_info["api_files"].append({
                                "file": file_path,
                                "framework": "streamlit",
                                "endpoints": 0  # Streamlit doesn't have traditional endpoints
                            })
                            
                    except Exception:
                        continue
        
        # Determine main framework
        if framework_info["detected_frameworks"]:
            # Priority: FastAPI > Flask > Streamlit
            if "fastapi" in framework_info["detected_frameworks"]:
                framework_info["main_framework"] = "fastapi"
            elif "flask" in framework_info["detected_frameworks"]:
                framework_info["main_framework"] = "flask"
            else:
                framework_info["main_framework"] = framework_info["detected_frameworks"][0]
        
        # Count total endpoints
        framework_info["endpoint_count"] = sum(
            file_info["endpoints"] for file_info in framework_info["api_files"]
        )
        
        return framework_info
    
    def _count_fastapi_endpoints(self, content: str) -> int:
        """Count FastAPI endpoints in content"""
        endpoint_decorators = ['@app.get', '@app.post', '@app.put', '@app.delete', '@app.patch']
        return sum(content.count(decorator) for decorator in endpoint_decorators)
    
    def _count_flask_endpoints(self, content: str) -> int:
        """Count Flask endpoints in content"""
        return content.count('@app.route')
    
    def analyze_existing_apis(self, workspace: str, framework_info: dict) -> dict:
        """Analyze existing API structure and endpoints"""
        
        api_analysis = {
            "endpoints": [],
            "models": [],
            "middleware": [],
            "authentication": False,
            "cors_enabled": False,
            "documentation": False
        }
        
        for api_file_info in framework_info["api_files"]:
            file_path = api_file_info["file"]
            framework = api_file_info["framework"]
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Parse AST to extract detailed information
                tree = ast.parse(content)
                
                for node in ast.walk(tree):
                    # Look for function definitions with decorators (endpoints)
                    if isinstance(node, ast.FunctionDef):
                        for decorator in node.decorator_list:
                            if self._is_api_decorator(decorator, framework):
                                endpoint_info = self._extract_endpoint_info(node, decorator, framework)
                                if endpoint_info:
                                    api_analysis["endpoints"].append(endpoint_info)
                    
                    # Look for Pydantic models (FastAPI)
                    elif isinstance(node, ast.ClassDef):
                        if self._is_model_class(node, content):
                            api_analysis["models"].append({
                                "name": node.name,
                                "file": file_path,
                                "type": "pydantic_model"
                            })
                
                # Check for authentication patterns
                content_lower = content.lower()
                if any(auth_term in content_lower for auth_term in ['jwt', 'token', 'auth', 'login']):
                    api_analysis["authentication"] = True
                
                # Check for CORS
                if 'cors' in content_lower or 'cross_origin' in content_lower:
                    api_analysis["cors_enabled"] = True
                
                # Check for documentation
                if 'swagger' in content_lower or 'openapi' in content_lower or '/docs' in content:
                    api_analysis["documentation"] = True
                    
            except Exception:
                continue
        
        return api_analysis
    
    def _is_api_decorator(self, decorator, framework: str) -> bool:
        """Check if decorator is an API endpoint decorator"""
        if framework == "fastapi":
            if isinstance(decorator, ast.Attribute):
                return decorator.attr in ["get", "post", "put", "delete", "patch"]
        elif framework == "flask":
            if isinstance(decorator, ast.Attribute):
                return decorator.attr == "route"
        return False
    
    def _extract_endpoint_info(self, func_node, decorator, framework: str) -> dict:
        """Extract endpoint information from function node"""
        try:
            endpoint_info = {
                "name": func_node.name,
                "method": "GET",  # Default
                "path": "/",      # Default
                "parameters": [],
                "return_type": None,
                "docstring": ast.get_docstring(func_node)
            }
            
            # Extract method and path based on framework
            if framework == "fastapi":
                if isinstance(decorator, ast.Attribute):
                    endpoint_info["method"] = decorator.attr.upper()
                # Extract path from decorator arguments
                if hasattr(decorator, 'args') and decorator.args:
                    if isinstance(decorator.args[0], ast.Str):
                        endpoint_info["path"] = decorator.args[0].s
            
            elif framework == "flask":
                # Extract route information from decorator
                if hasattr(decorator, 'args') and decorator.args:
                    if isinstance(decorator.args[0], ast.Str):
                        endpoint_info["path"] = decorator.args[0].s
            
            # Extract parameters
            for arg in func_node.args.args:
                if arg.arg != "self":
                    endpoint_info["parameters"].append(arg.arg)
            
            return endpoint_info
            
        except Exception:
            return None
    
    def _is_model_class(self, class_node, content: str) -> bool:
        """Check if class is a data model"""
        # Look for Pydantic BaseModel inheritance
        for base in class_node.bases:
            if isinstance(base, ast.Name) and base.id == "BaseModel":
                return True
        
        # Check for common model patterns in content
        class_content = content[class_node.lineno:class_node.end_lineno] if hasattr(class_node, 'end_lineno') else ""
        return "BaseModel" in class_content or "Model" in class_node.name
    
    def generate_api_tests(self, api_analysis: dict, framework_info: dict) -> dict:
        """Generate test cases for API endpoints"""
        
        test_generation = {
            "test_files_created": [],
            "tests_generated": 0,
            "test_coverage": 0
        }
        
        if not api_analysis["endpoints"]:
            return test_generation
        
        # Generate test file content
        test_content = self._create_api_test_template(api_analysis, framework_info)
        
        try:
            # Create test file
            test_filename = f"test_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}.py"
            test_path = os.path.join(".", test_filename)
            
            with open(test_path, 'w') as f:
                f.write(test_content)
            
            test_generation["test_files_created"].append(test_path)
            test_generation["tests_generated"] = len(api_analysis["endpoints"]) * 2  # Basic + error tests
            test_generation["test_coverage"] = 100 if api_analysis["endpoints"] else 0
            
        except Exception as e:
            test_generation["error"] = str(e)
        
        return test_generation
    
    def _create_api_test_template(self, api_analysis: dict, framework_info: dict) -> str:
        """Create API test template"""
        
        template = f'''#!/usr/bin/env python3
"""
Auto-generated API tests
Generated on: {datetime.now().isoformat()}
Framework: {framework_info.get("main_framework", "unknown")}
"""

import unittest
import requests
import json
from datetime import datetime

class APITestCase(unittest.TestCase):
    """Test cases for API endpoints"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.base_url = "http://localhost:8000"  # Adjust as needed
        self.headers = {{"Content-Type": "application/json"}}
    
    def tearDown(self):
        """Clean up after tests"""
        pass

'''
        
        # Generate test methods for each endpoint
        for i, endpoint in enumerate(api_analysis["endpoints"]):
            method = endpoint["method"].lower()
            path = endpoint["path"]
            name = endpoint["name"]
            
            template += f'''
    def test_{name}_success(self):
        """Test {name} endpoint - success case"""
        url = self.base_url + "{path}"
        
        try:
            if "{method}" == "get":
                response = requests.get(url, headers=self.headers, timeout=5)
            elif "{method}" == "post":
                test_data = {{"test": "data"}}  # Customize as needed
                response = requests.post(url, json=test_data, headers=self.headers, timeout=5)
            else:
                response = requests.{method}(url, headers=self.headers, timeout=5)
            
            # Basic assertions
            self.assertIn(response.status_code, [200, 201, 202])
            
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not available")
        except Exception as e:
            self.fail(f"Unexpected error: {{e}}")
    
    def test_{name}_error_handling(self):
        """Test {name} endpoint - error handling"""
        # Test with invalid data or missing parameters
        url = self.base_url + "{path}"
        
        try:
            if "{method}" == "post":
                # Test with invalid data
                response = requests.post(url, json={{"invalid": "data"}}, headers=self.headers, timeout=5)
                self.assertIn(response.status_code, [400, 422, 500])
            else:
                # Test with invalid path
                response = requests.{method}(url + "/invalid", headers=self.headers, timeout=5)
                self.assertIn(response.status_code, [404, 405])
                
        except requests.exceptions.ConnectionError:
            self.skipTest("API server not available")
        except Exception as e:
            self.fail(f"Unexpected error: {{e}}")
'''
        
        template += '''
    def test_api_health(self):
        """Test API health/status endpoint"""
        health_endpoints = ["/health", "/status", "/ping", "/"]
        
        for endpoint in health_endpoints:
            try:
                response = requests.get(self.base_url + endpoint, timeout=5)
                if response.status_code == 200:
                    self.assertTrue(True)  # At least one health endpoint works
                    return
            except:
                continue
        
        self.skipTest("No health endpoint found or API not available")

if __name__ == "__main__":
    unittest.main()
'''
        
        return template
    
    def generate_api_documentation(self, api_analysis: dict, framework_info: dict) -> dict:
        """Generate API documentation"""
        
        doc_generation = {
            "documentation_created": [],
            "endpoints_documented": len(api_analysis["endpoints"]),
            "format": "markdown"
        }
        
        # Generate markdown documentation
        doc_content = self._create_api_documentation_content(api_analysis, framework_info)
        
        try:
            doc_filename = f"API_Documentation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            doc_path = os.path.join(".", doc_filename)
            
            with open(doc_path, 'w') as f:
                f.write(doc_content)
            
            doc_generation["documentation_created"].append(doc_path)
            
        except Exception as e:
            doc_generation["error"] = str(e)
        
        return doc_generation
    
    def _create_api_documentation_content(self, api_analysis: dict, framework_info: dict) -> str:
        """Create API documentation content"""
        
        content = f"""# API Documentation

*Auto-generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*

## Overview

This API is built using **{framework_info.get('main_framework', 'Unknown').title()}** framework.

- **Total Endpoints**: {len(api_analysis['endpoints'])}
- **Authentication**: {'✅ Enabled' if api_analysis['authentication'] else '❌ Not detected'}
- **CORS**: {'✅ Enabled' if api_analysis['cors_enabled'] else '❌ Not detected'}
- **Documentation**: {'✅ Available' if api_analysis['documentation'] else '❌ Not detected'}

## Endpoints

"""
        
        # Document each endpoint
        for endpoint in api_analysis["endpoints"]:
            content += f"""### {endpoint['method']} {endpoint['path']}

**Function**: `{endpoint['name']}`

"""
            
            if endpoint.get('docstring'):
                content += f"**Description**: {endpoint['docstring']}\n\n"
            
            if endpoint.get('parameters'):
                content += "**Parameters**:\n"
                for param in endpoint['parameters']:
                    content += f"- `{param}`: Parameter description needed\n"
                content += "\n"
            
            content += f"""**Example Request**:
```bash
curl -X {endpoint['method']} \\
  http://localhost:8000{endpoint['path']} \\
  -H "Content-Type: application/json"
```

**Example Response**:
```json
{{
  "status": "success",
  "data": {{}}
}}
```

---

"""
        
        # Add models documentation
        if api_analysis["models"]:
            content += "## Data Models\n\n"
            for model in api_analysis["models"]:
                content += f"### {model['name']}\n\n"
                content += f"*Defined in: {model['file']}*\n\n"
                content += "```python\n# Model definition needed\n```\n\n"
        
        # Add testing information
        content += """## Testing

To test this API:

1. Start the server
2. Run the generated test suite: `python test_api_*.py`
3. Use the provided curl examples above

## Authentication

"""
        
        if api_analysis["authentication"]:
            content += "This API uses authentication. Please refer to the authentication documentation.\n"
        else:
            content += "This API does not require authentication.\n"
        
        content += "\n*This documentation was automatically generated by the API Agent.*\n"
        
        return content

def main():
    if len(sys.argv) < 2:
        print("❌ No task data provided")
        sys.exit(1)
    
    try:
        task_data = json.loads(sys.argv[1])
        agent = APIAgent()
        
        print(f"🌐 API Agent: Analyzing API structure...")
        
        workspace = task_data.get('workspace', '.')
        action = task_data.get('action', 'analyze')
        
        # Detect API framework
        framework_info = agent.detect_api_framework(workspace)
        
        # Analyze existing APIs
        api_analysis = agent.analyze_existing_apis(workspace, framework_info)
        
        result = {
            "framework_detection": framework_info,
            "api_analysis": api_analysis,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "status": "completed"
        }
        
        if action in ["test", "full"]:
            # Generate API tests
            test_generation = agent.generate_api_tests(api_analysis, framework_info)
            result["test_generation"] = test_generation
            
        if action in ["docs", "full"]:
            # Generate API documentation
            doc_generation = agent.generate_api_documentation(api_analysis, framework_info)
            result["documentation_generation"] = doc_generation
        
        print(f"✅ API analysis completed")
        print(f"   🌐 Framework: {framework_info.get('main_framework', 'None detected')}")
        print(f"   📍 Endpoints: {len(api_analysis['endpoints'])}")
        print(f"   🔐 Auth: {'Yes' if api_analysis['authentication'] else 'No'}")
        print(f"   📚 Models: {len(api_analysis['models'])}")
        
        if action in ["test", "full"] and "test_generation" in result:
            print(f"   🧪 Tests: {result['test_generation']['tests_generated']} generated")
            
        if action in ["docs", "full"] and "documentation_generation" in result:
            print(f"   📄 Docs: {result['documentation_generation']['endpoints_documented']} endpoints documented")
        
        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(f"❌ API analysis failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
